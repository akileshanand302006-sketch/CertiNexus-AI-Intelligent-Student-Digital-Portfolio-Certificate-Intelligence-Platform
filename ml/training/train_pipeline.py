"""
CertiNexus AI — Complete ML Training Pipeline

Implements the full ML experimentation workflow:
1. Data loading and stratified splitting
2. Feature engineering (3 experiment configurations)
3. Baseline model (Multinomial Naive Bayes)
4. Candidate models (Logistic Regression, Linear SVM)
5. Hyperparameter tuning (GridSearchCV)
6. Final evaluation on held-out test set
7. Error analysis
8. Model serialization
9. Experiment logging

All results are saved to experiments.csv and ml/evaluation/
"""

import csv
import json
import os
import sys
import time
import warnings
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

warnings.filterwarnings('ignore')

# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15  # of the remaining after test split (≈ 0.176 of remaining)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "processed", "cleaned_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
EVAL_DIR = os.path.join(BASE_DIR, "ml", "evaluation")
FIGURES_DIR = os.path.join(EVAL_DIR, "figures")
EXPERIMENTS_FILE = os.path.join(BASE_DIR, "experiments.csv")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

np.random.seed(RANDOM_SEED)


# ============================================================
# Experiment Logger
# ============================================================

class ExperimentLogger:
    """Log experiments to CSV file."""

    FIELDNAMES = [
        "experiment_id", "date", "dataset_version", "preprocessing_version",
        "feature_set", "model", "parameters", "validation_accuracy",
        "macro_precision", "macro_recall", "macro_f1", "weighted_f1",
        "training_time", "inference_time", "observations"
    ]

    def __init__(self, filepath=EXPERIMENTS_FILE):
        self.filepath = filepath
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
        self.counter = 0

    def log(self, **kwargs):
        self.counter += 1
        row = {k: "" for k in self.FIELDNAMES}
        row["experiment_id"] = f"EXP-{self.counter:03d}"
        row["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        row["dataset_version"] = "synthetic_v1"
        row["preprocessing_version"] = "v1"
        row.update(kwargs)

        # Serialize dicts/lists
        for k, v in row.items():
            if isinstance(v, (dict, list)):
                row[k] = json.dumps(v)
            elif isinstance(v, float):
                row[k] = f"{v:.4f}"

        with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(row)

        print(f"  [LOG] {row['experiment_id']}: {row.get('model', '?')} | "
              f"F1={row.get('macro_f1', '?')}")
        return row


# ============================================================
# Data Loading and Splitting
# ============================================================

def load_and_split_data(dataset_path=DATASET_PATH):
    """Load dataset and perform stratified train/validation/test split."""
    print("\n" + "=" * 60)
    print("STEP 1: Loading and Splitting Data")
    print("=" * 60)

    df = pd.read_csv(dataset_path)
    print(f"  Total samples: {len(df)}")
    print(f"  Categories: {df['category'].nunique()}")

    X = df['clean_text'].values
    y = df['category'].values

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"  Classes: {list(le.classes_)}")

    # First split: separate test set (15%)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y_encoded, test_size=TEST_SIZE,
        stratify=y_encoded, random_state=RANDOM_SEED
    )

    # Second split: train and validation from remaining (≈ 70/15 overall)
    val_fraction = VAL_SIZE / (1 - TEST_SIZE)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_fraction,
        stratify=y_temp, random_state=RANDOM_SEED
    )

    print(f"\n  Split sizes:")
    print(f"    Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"    Validation: {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
    print(f"    Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")

    # Verify stratification
    print(f"\n  Class distribution in train:")
    for cls_idx in range(len(le.classes_)):
        count = (y_train == cls_idx).sum()
        print(f"    {le.classes_[cls_idx]}: {count}")

    return X_train, X_val, X_test, y_train, y_val, y_test, le


# ============================================================
# Feature Engineering
# ============================================================

def create_feature_configs():
    """Define three feature experiment configurations."""
    configs = {
        "tfidf_word": {
            "name": "TF-IDF Word N-grams",
            "vectorizer": TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,
                sublinear_tf=True,
                min_df=2,
                max_df=0.95,
            ),
        },
        "tfidf_word_char": {
            "name": "TF-IDF Word + Character N-grams",
            "vectorizer": FeatureUnion([
                ("word", TfidfVectorizer(
                    analyzer='word',
                    ngram_range=(1, 2),
                    max_features=4000,
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.95,
                )),
                ("char", TfidfVectorizer(
                    analyzer='char_wb',
                    ngram_range=(2, 4),
                    max_features=3000,
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.95,
                )),
            ]),
        },
        "tfidf_enriched": {
            "name": "TF-IDF + Engineered Features",
            "vectorizer": FeatureUnion([
                ("word", TfidfVectorizer(
                    analyzer='word',
                    ngram_range=(1, 2),
                    max_features=4000,
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.95,
                )),
                ("char", TfidfVectorizer(
                    analyzer='char_wb',
                    ngram_range=(2, 4),
                    max_features=2000,
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.95,
                )),
            ]),
        },
    }
    return configs


# ============================================================
# Model Training and Evaluation
# ============================================================

def evaluate_model(model, X, y, le, dataset_name="Validation"):
    """Evaluate a model and return metrics dict."""
    start = time.time()
    y_pred = model.predict(X)
    inference_time = time.time() - start

    acc = accuracy_score(y, y_pred)
    macro_p = precision_score(y, y_pred, average='macro', zero_division=0)
    macro_r = recall_score(y, y_pred, average='macro', zero_division=0)
    macro_f1 = f1_score(y, y_pred, average='macro', zero_division=0)
    weighted_f1 = f1_score(y, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y, y_pred)
    report = classification_report(y, y_pred, target_names=le.classes_,
                                   zero_division=0, output_dict=True)

    metrics = {
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "inference_time": inference_time,
        "confusion_matrix": cm,
        "classification_report": report,
        "y_pred": y_pred,
    }

    print(f"\n  {dataset_name} Results:")
    print(f"    Accuracy:        {acc:.4f}")
    print(f"    Macro Precision: {macro_p:.4f}")
    print(f"    Macro Recall:    {macro_r:.4f}")
    print(f"    Macro F1:        {macro_f1:.4f}")
    print(f"    Weighted F1:     {weighted_f1:.4f}")
    print(f"    Inference Time:  {inference_time:.4f}s")

    return metrics


def train_baseline(X_train, X_val, y_train, y_val, le, logger):
    """Train the Multinomial Naive Bayes baseline."""
    print("\n" + "=" * 60)
    print("STEP 2: Baseline Model — Multinomial Naive Bayes")
    print("=" * 60)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), max_features=5000,
        sublinear_tf=True, min_df=2, max_df=0.95,
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_val_tfidf = vectorizer.transform(X_val)

    model = MultinomialNB(alpha=1.0)

    start = time.time()
    model.fit(X_train_tfidf, y_train)
    train_time = time.time() - start
    print(f"  Training time: {train_time:.4f}s")

    metrics = evaluate_model(model, X_val_tfidf, y_val, le, "Validation")

    # Build pipeline for serialization
    pipeline = Pipeline([
        ("vectorizer", vectorizer),
        ("classifier", model)
    ])

    logger.log(
        feature_set="tfidf_word",
        model="MultinomialNB",
        parameters={"alpha": 1.0},
        validation_accuracy=metrics["accuracy"],
        macro_precision=metrics["macro_precision"],
        macro_recall=metrics["macro_recall"],
        macro_f1=metrics["macro_f1"],
        weighted_f1=metrics["weighted_f1"],
        training_time=train_time,
        inference_time=metrics["inference_time"],
        observations="Baseline model with default parameters"
    )

    return pipeline, metrics


def train_candidates(X_train, X_val, y_train, y_val, le, logger):
    """Train and compare candidate models with hyperparameter tuning."""
    print("\n" + "=" * 60)
    print("STEP 3: Candidate Models — Logistic Regression & Linear SVM")
    print("=" * 60)

    feature_configs = create_feature_configs()
    results = {}

    # ---- Model definitions with hyperparameter grids ----
    model_configs = {
        "LogisticRegression": {
            "model": LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
            "param_grid": {
                "C": [0.1, 1.0, 10.0],
                "class_weight": [None, "balanced"],
            },
        },
        "LinearSVM": {
            "model": LinearSVC(max_iter=2000, random_state=RANDOM_SEED),
            "param_grid": {
                "C": [0.1, 1.0, 10.0],
                "class_weight": [None, "balanced"],
            },
        },
        "MultinomialNB_tuned": {
            "model": MultinomialNB(),
            "param_grid": {
                "alpha": [0.01, 0.1, 0.5, 1.0, 2.0],
            },
        },
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    best_overall_score = 0
    best_overall_config = None

    for feat_key, feat_config in feature_configs.items():
        print(f"\n  --- Feature Set: {feat_config['name']} ---")

        vectorizer = feat_config["vectorizer"]
        X_train_feat = vectorizer.fit_transform(X_train)
        X_val_feat = vectorizer.transform(X_val)

        for model_name, model_config in model_configs.items():
            # Skip MNB with non-word features (MNB needs non-negative features)
            if model_name == "MultinomialNB_tuned" and feat_key != "tfidf_word":
                continue

            print(f"\n  Model: {model_name} | Features: {feat_key}")

            grid_search = GridSearchCV(
                model_config["model"],
                model_config["param_grid"],
                cv=cv,
                scoring='f1_macro',
                n_jobs=-1,
                verbose=0,
                refit=True,
            )

            start = time.time()
            grid_search.fit(X_train_feat, y_train)
            train_time = time.time() - start

            print(f"    Best CV Score: {grid_search.best_score_:.4f}")
            print(f"    Best Params: {grid_search.best_params_}")
            print(f"    Training Time: {train_time:.4f}s")

            # Evaluate on validation set
            best_model = grid_search.best_estimator_
            metrics = evaluate_model(best_model, X_val_feat, y_val, le, "Validation")

            # Build pipeline
            pipeline = Pipeline([
                ("vectorizer", vectorizer),
                ("classifier", best_model)
            ])

            config_key = f"{model_name}__{feat_key}"
            results[config_key] = {
                "pipeline": pipeline,
                "metrics": metrics,
                "train_time": train_time,
                "best_params": grid_search.best_params_,
                "cv_score": grid_search.best_score_,
                "model_name": model_name,
                "feature_set": feat_key,
            }

            logger.log(
                feature_set=feat_key,
                model=model_name,
                parameters=grid_search.best_params_,
                validation_accuracy=metrics["accuracy"],
                macro_precision=metrics["macro_precision"],
                macro_recall=metrics["macro_recall"],
                macro_f1=metrics["macro_f1"],
                weighted_f1=metrics["weighted_f1"],
                training_time=train_time,
                inference_time=metrics["inference_time"],
                observations=f"Best CV score: {grid_search.best_score_:.4f}"
            )

            if metrics["macro_f1"] > best_overall_score:
                best_overall_score = metrics["macro_f1"]
                best_overall_config = config_key

    print(f"\n  ★ Best configuration: {best_overall_config}")
    print(f"    Validation Macro F1: {best_overall_score:.4f}")

    return results, best_overall_config


def final_test_evaluation(pipeline, X_test, y_test, le, config_name, logger):
    """Evaluate the final selected model on the held-out test set."""
    print("\n" + "=" * 60)
    print("STEP 4: Final Evaluation on Held-Out Test Set")
    print("=" * 60)
    print(f"  Selected model: {config_name}")
    print("  WARNING: This is the ONLY evaluation on the test set.")

    # The pipeline was already fit during training, so we just transform+predict
    metrics = evaluate_model(pipeline, X_test, y_test, le, "TEST SET")

    # Save detailed classification report
    report_text = classification_report(
        y_test, metrics["y_pred"],
        target_names=le.classes_, zero_division=0
    )
    print(f"\n  Detailed Classification Report:\n{report_text}")

    # Save confusion matrix
    cm = metrics["confusion_matrix"]

    logger.log(
        feature_set="final",
        model=config_name,
        parameters={"note": "FINAL TEST EVALUATION"},
        validation_accuracy=metrics["accuracy"],
        macro_precision=metrics["macro_precision"],
        macro_recall=metrics["macro_recall"],
        macro_f1=metrics["macro_f1"],
        weighted_f1=metrics["weighted_f1"],
        training_time=0,
        inference_time=metrics["inference_time"],
        observations="FINAL HELD-OUT TEST SET EVALUATION"
    )

    return metrics


# ============================================================
# Error Analysis
# ============================================================

def perform_error_analysis(pipeline, X_test, y_test, le):
    """Analyze misclassifications and identify failure patterns."""
    print("\n" + "=" * 60)
    print("STEP 5: Error Analysis")
    print("=" * 60)

    y_pred = pipeline.predict(X_test)
    errors = []

    for i in range(len(X_test)):
        if y_pred[i] != y_test[i]:
            errors.append({
                "text": X_test[i][:200],  # Truncate for readability
                "actual": le.classes_[y_test[i]],
                "predicted": le.classes_[y_pred[i]],
            })

    print(f"  Total misclassifications: {len(errors)} / {len(X_test)}")
    print(f"  Error rate: {len(errors)/len(X_test)*100:.1f}%")

    # Analyze error patterns
    from collections import Counter
    confusion_pairs = Counter()
    for e in errors:
        pair = f"{e['actual']} → {e['predicted']}"
        confusion_pairs[pair] += 1

    print(f"\n  Most common confusion pairs:")
    for pair, count in confusion_pairs.most_common(10):
        print(f"    {pair}: {count}")

    # Show example misclassifications
    print(f"\n  Example misclassifications:")
    for e in errors[:5]:
        print(f"\n    Actual: {e['actual']}")
        print(f"    Predicted: {e['predicted']}")
        print(f"    Text: {e['text'][:150]}...")

    # Save error analysis
    error_report = {
        "total_test_samples": len(X_test),
        "total_errors": len(errors),
        "error_rate": len(errors) / len(X_test),
        "confusion_pairs": dict(confusion_pairs.most_common(20)),
        "example_errors": errors[:20],
    }

    error_path = os.path.join(EVAL_DIR, "error_analysis.json")
    with open(error_path, 'w', encoding='utf-8') as f:
        json.dump(error_report, f, indent=2, default=str)
    print(f"\n  Error analysis saved to {error_path}")

    return error_report


# ============================================================
# Save Results
# ============================================================

def save_results(pipeline, le, metrics, all_results, config_name):
    """Save model artifacts and evaluation results."""
    print("\n" + "=" * 60)
    print("STEP 6: Saving Model Artifacts")
    print("=" * 60)

    # Save production model
    prod_dir = os.path.join(MODELS_DIR, "production")
    os.makedirs(prod_dir, exist_ok=True)

    model_path = os.path.join(prod_dir, "certificate_classifier.joblib")
    joblib.dump(pipeline, model_path)
    print(f"  Pipeline saved: {model_path}")

    le_path = os.path.join(prod_dir, "label_encoder.joblib")
    joblib.dump(le, le_path)
    print(f"  Label encoder saved: {le_path}")

    # Save model metadata
    metadata = {
        "model_id": "certificate_classifier_v1",
        "model_name": "CertificateClassifier",
        "version": "1.0",
        "dataset_version": "synthetic_v1",
        "feature_version": config_name.split("__")[1] if "__" in config_name else "tfidf_word",
        "training_date": datetime.now().isoformat(),
        "algorithm": config_name.split("__")[0] if "__" in config_name else config_name,
        "metrics": {
            "accuracy": float(metrics["accuracy"]),
            "macro_precision": float(metrics["macro_precision"]),
            "macro_recall": float(metrics["macro_recall"]),
            "macro_f1": float(metrics["macro_f1"]),
            "weighted_f1": float(metrics["weighted_f1"]),
        },
        "classes": list(le.classes_),
        "status": "production"
    }

    meta_path = os.path.join(prod_dir, "model_metadata.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved: {meta_path}")

    # Save confusion matrix
    cm = metrics["confusion_matrix"]
    cm_data = {
        "matrix": cm.tolist(),
        "labels": list(le.classes_),
    }
    cm_path = os.path.join(EVAL_DIR, "confusion_matrix.json")
    with open(cm_path, 'w', encoding='utf-8') as f:
        json.dump(cm_data, f, indent=2)
    print(f"  Confusion matrix saved: {cm_path}")

    # Save classification report
    report = metrics["classification_report"]
    report_path = os.path.join(EVAL_DIR, "classification_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Classification report saved: {report_path}")

    # Save model comparison summary
    comparison = {}
    for key, result in all_results.items():
        comparison[key] = {
            "model": result["model_name"],
            "feature_set": result["feature_set"],
            "best_params": result["best_params"],
            "cv_score": float(result["cv_score"]),
            "val_accuracy": float(result["metrics"]["accuracy"]),
            "val_macro_f1": float(result["metrics"]["macro_f1"]),
            "val_weighted_f1": float(result["metrics"]["weighted_f1"]),
            "train_time": float(result["train_time"]),
        }

    comp_path = os.path.join(EVAL_DIR, "model_comparison.json")
    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)
    print(f"  Model comparison saved: {comp_path}")

    print("\n✓ All artifacts saved!")


# ============================================================
# Visualization
# ============================================================

def generate_figures(metrics, all_results, le):
    """Generate evaluation figures."""
    print("\n" + "=" * 60)
    print("STEP 7: Generating Figures")
    print("=" * 60)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("  matplotlib/seaborn not available, skipping figures")
        return

    # 1. Confusion Matrix Heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    cm = metrics["confusion_matrix"]
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=le.classes_, yticklabels=le.classes_, ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title('Confusion Matrix — Final Test Set')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "confusion_matrix.png"), dpi=150)
    plt.close()
    print("  Saved confusion_matrix.png")

    # 2. Model Comparison Bar Chart
    model_names = []
    f1_scores = []
    for key, result in all_results.items():
        model_names.append(f"{result['model_name']}\n({result['feature_set']})")
        f1_scores.append(result["metrics"]["macro_f1"])

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(model_names, f1_scores, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(model_names))))
    ax.set_xlabel('Macro F1 Score')
    ax.set_title('Model Comparison — Validation Set')
    ax.set_xlim(0, 1)
    for bar, score in zip(bars, f1_scores):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{score:.3f}', va='center', fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "model_comparison.png"), dpi=150)
    plt.close()
    print("  Saved model_comparison.png")

    # 3. Per-class F1 scores
    report = metrics["classification_report"]
    classes = [c for c in le.classes_ if c in report]
    per_class_f1 = [report[c]["f1-score"] for c in classes]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(classes, per_class_f1, color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(classes))))
    ax.set_xlabel('F1 Score')
    ax.set_title('Per-Class F1 Score — Final Test Set')
    ax.set_xlim(0, 1)
    for bar, score in zip(bars, per_class_f1):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{score:.3f}', va='center', fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "per_class_f1.png"), dpi=150)
    plt.close()
    print("  Saved per_class_f1.png")

    print("\n✓ All figures generated!")


# ============================================================
# Main Pipeline
# ============================================================

def run_full_pipeline():
    """Execute the complete ML experimentation pipeline."""
    print("=" * 60)
    print("CertiNexus AI — ML Training Pipeline")
    print("=" * 60)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Random Seed: {RANDOM_SEED}")
    print(f"  Dataset: {DATASET_PATH}")

    logger = ExperimentLogger()

    # Step 1: Load and split data
    X_train, X_val, X_test, y_train, y_val, y_test, le = load_and_split_data()

    # Step 2: Baseline
    baseline_pipeline, baseline_metrics = train_baseline(
        X_train, X_val, y_train, y_val, le, logger
    )

    # Step 3: Candidate models with hyperparameter tuning
    all_results, best_config = train_candidates(
        X_train, X_val, y_train, y_val, le, logger
    )

    # Add baseline to results for comparison
    all_results["MultinomialNB_baseline__tfidf_word"] = {
        "pipeline": baseline_pipeline,
        "metrics": baseline_metrics,
        "train_time": 0,
        "best_params": {"alpha": 1.0},
        "cv_score": baseline_metrics["macro_f1"],
        "model_name": "MultinomialNB_baseline",
        "feature_set": "tfidf_word",
    }

    # Step 4: Final test evaluation with best model
    best_pipeline = all_results[best_config]["pipeline"]

    # IMPORTANT: Re-fit the best pipeline on combined train+val for final model
    print("\n  Re-fitting best model on train + validation data...")
    X_trainval = np.concatenate([X_train, X_val])
    y_trainval = np.concatenate([y_train, y_val])
    best_pipeline.fit(X_trainval, y_trainval)

    test_metrics = final_test_evaluation(
        best_pipeline, X_test, y_test, le, best_config, logger
    )

    # Step 5: Error analysis
    error_report = perform_error_analysis(best_pipeline, X_test, y_test, le)

    # Step 6: Save everything
    save_results(best_pipeline, le, test_metrics, all_results, best_config)

    # Step 7: Generate figures
    generate_figures(test_metrics, all_results, le)

    # Print summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE — SUMMARY")
    print("=" * 60)
    print(f"  Best Model: {best_config}")
    print(f"  Test Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"  Test Macro F1: {test_metrics['macro_f1']:.4f}")
    print(f"  Test Weighted F1: {test_metrics['weighted_f1']:.4f}")
    print(f"  Total Errors: {error_report['total_errors']}/{error_report['total_test_samples']}")
    print(f"  Models saved to: {MODELS_DIR}")
    print(f"  Experiments logged to: {EXPERIMENTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    run_full_pipeline()
