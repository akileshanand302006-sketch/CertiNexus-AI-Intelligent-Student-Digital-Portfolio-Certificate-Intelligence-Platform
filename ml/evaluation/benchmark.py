"""
CertiNexus AI — ML Model Benchmarking Engine

Runs systematic benchmarking across all 9 experimental setups:
- 3 Algorithms: MultinomialNB, LogisticRegression, Calibrated LinearSVC
- 3 Feature Sets: tfidf_word, tfidf_word_char, tfidf_enriched

Measures:
- Stratified 5-Fold Cross Validation Macro-F1, Accuracy, Precision, Recall
- Held-out Test Set Macro-F1, Accuracy, Precision, Recall
- Fit time (seconds) and Single-sample Inference Latency (ms)
- Produces ml/evaluation/benchmark_results.json and summary report.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.data.loaders import load_capcc_v1
from ml.data.splits import create_stratified_splits
from ml.features.feature_pipeline import FeaturePipelineBuilder
from ml.classifiers.calibration import CalibratedClassifierWrapper


class ModelBenchmarkRunner:
    """Benchmark runner for certificate classification models."""

    CONFIGS = [
        # MultinomialNB
        {"model": "MultinomialNB", "feature_set": "tfidf_word", "params": {"alpha": 1.0}},
        {"model": "MultinomialNB", "feature_set": "tfidf_word_char", "params": {"alpha": 0.5}},
        {"model": "MultinomialNB", "feature_set": "tfidf_enriched", "params": {"alpha": 0.1}},
        # LogisticRegression
        {"model": "LogisticRegression", "feature_set": "tfidf_word", "params": {"C": 1.0, "max_iter": 1000}},
        {"model": "LogisticRegression", "feature_set": "tfidf_word_char", "params": {"C": 2.0, "max_iter": 1000}},
        {"model": "LogisticRegression", "feature_set": "tfidf_enriched", "params": {"C": 5.0, "max_iter": 1000}},
        # LinearSVC (Calibrated)
        {"model": "LinearSVC", "feature_set": "tfidf_word", "params": {"C": 1.0}},
        {"model": "LinearSVC", "feature_set": "tfidf_word_char", "params": {"C": 1.0}},
        {"model": "LinearSVC", "feature_set": "tfidf_enriched", "params": {"C": 0.5}},
    ]

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.output_dir = os.path.join(PROJECT_ROOT, "ml", "evaluation")
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_estimator(self, model_name: str, params: dict):
        if model_name == "MultinomialNB":
            return MultinomialNB(**params)
        elif model_name == "LogisticRegression":
            return LogisticRegression(random_state=self.random_seed, **params)
        elif model_name == "LinearSVC":
            base = LinearSVC(random_state=self.random_seed, **params)
            return CalibratedClassifierWrapper(base, calibration_method="sigmoid", cv=3)
        raise ValueError(f"Unknown model: {model_name}")

    def run(self) -> Dict[str, Any]:
        print("=" * 65)
        print("CertiNexus AI — ML System Benchmark Suite")
        print("=" * 65)

        df, info = load_capcc_v1()
        splits = create_stratified_splits(df, random_seed=self.random_seed)

        X_train_raw = splits.X_train
        y_train = splits.y_train
        X_test_raw = splits.X_test
        y_test = splits.y_test
        classes = list(splits.label_encoder.classes_)

        results = []
        best_f1 = -1.0
        best_config = None

        for idx, cfg in enumerate(self.CONFIGS, 1):
            name = f"{cfg['model']}__{cfg['feature_set']}"
            print(f"[{idx}/{len(self.CONFIGS)}] Benchmarking {name}...")

            # Build feature pipeline
            builder = FeaturePipelineBuilder.build(cfg["feature_set"])
            t0 = time.time()
            X_train = builder.fit_transform(X_train_raw)
            fit_transform_time = time.time() - t0

            # 5-Fold Stratified Cross Validation
            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_seed)
            cv_f1s = []
            cv_accs = []

            for tr_idx, val_idx in skf.split(X_train, y_train):
                X_tr, y_tr = X_train[tr_idx], y_train[tr_idx]
                X_vl, y_val_fold = X_train[val_idx], y_train[val_idx]

                clf = self._get_estimator(cfg["model"], cfg["params"])
                clf.fit(X_tr, y_tr)
                preds = clf.predict(X_vl)
                cv_f1s.append(f1_score(y_val_fold, preds, average="macro"))
                cv_accs.append(accuracy_score(y_val_fold, preds))

            # Train on full train set and evaluate on test set
            final_clf = self._get_estimator(cfg["model"], cfg["params"])
            t_train_start = time.time()
            final_clf.fit(X_train, y_train)
            train_duration = time.time() - t_train_start + fit_transform_time

            # Inference on test set
            X_test = builder.transform(X_test_raw)
            t_inf_start = time.time()
            test_preds = final_clf.predict(X_test)
            inf_duration_ms = ((time.time() - t_inf_start) / max(len(X_test_raw), 1)) * 1000

            test_acc = float(accuracy_score(y_test, test_preds))
            test_f1 = float(f1_score(y_test, test_preds, average="macro"))
            test_prec = float(precision_score(y_test, test_preds, average="macro"))
            test_rec = float(recall_score(y_test, test_preds, average="macro"))

            record = {
                "experiment_name": name,
                "model": cfg["model"],
                "feature_set": cfg["feature_set"],
                "parameters": cfg["params"],
                "cv_macro_f1_mean": round(float(np.mean(cv_f1s)), 4),
                "cv_macro_f1_std": round(float(np.std(cv_f1s)), 4),
                "cv_accuracy_mean": round(float(np.mean(cv_accs)), 4),
                "test_accuracy": round(test_acc, 4),
                "test_macro_f1": round(test_f1, 4),
                "test_macro_precision": round(test_prec, 4),
                "test_macro_recall": round(test_rec, 4),
                "training_time_sec": round(train_duration, 3),
                "latency_per_sample_ms": round(inf_duration_ms, 2),
            }
            results.append(record)

            if test_f1 > best_f1:
                best_f1 = test_f1
                best_config = name

            print(f"    CV F1: {record['cv_macro_f1_mean']:.4f} | Test F1: {test_f1:.4f} | Latency: {inf_duration_ms:.2f}ms")

        benchmark_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "num_experiments": len(results),
            "best_configuration": best_config,
            "classes": classes,
            "results": results,
        }

        # Save results
        out_path = os.path.join(self.output_dir, "benchmark_results.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, indent=2)

        print(f"\n[OK] Benchmark complete! Results saved to: {out_path}")
        print(f"     Champion Model: {best_config} with Test Macro-F1: {best_f1:.4f}")
        return benchmark_data


if __name__ == "__main__":
    runner = ModelBenchmarkRunner()
    runner.run()
