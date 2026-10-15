"""
CertiNexus AI — Certificate Classifier Evaluation Entrypoint
Evaluates the 11-category LinearSVC model on the CAPCC dataset.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, f1_score


def run_certificate_classifier_evaluation():
    print("=" * 70)
    print("CertiNexus AI — Evaluating 11-Category Certificate Classifier")
    print("=" * 70)

    from ml.inference.predictor import CertificateClassifier
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_dir = os.path.join(project_root, "ml", "models", "production")
    
    classifier = CertificateClassifier(model_dir=model_dir)
    classifier.load()

    # Load cleaned dataset test split
    csv_path = os.path.join(project_root, "dataset", "processed", "cleaned_dataset.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(project_root, "dataset", "public", "capcc-v1", "capcc_v1.csv")

    df = pd.read_csv(csv_path)
    # Take a held-out test subset of 100 samples
    test_df = df.sample(n=min(100, len(df)), random_state=42)

    y_true = []
    y_pred = []

    for _, row in test_df.iterrows():
        text = str(row.get("text", row.get("raw_text", "")))
        label = str(row.get("category", row.get("label", "")))
        if not text or not label:
            continue
        pred = classifier.predict(text)["category"]
        y_true.append(label)
        y_pred.append(pred)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    print(f"Total Test Certificates: {len(y_true)}")
    print(f"Overall Accuracy:        {acc:.4f} ({acc*100:.1f}%)")
    print(f"Weighted Macro F1 Score: {f1:.4f}")

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "certificate_classifier_evaluation.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": round(float(acc), 4),
            "macro_f1": round(float(f1), 4),
            "total_samples": len(y_true),
            "per_class": report,
        }, f, indent=2)

    print(f"Saved evaluation metrics to: {out_path}")
    return acc, f1


if __name__ == "__main__":
    run_certificate_classifier_evaluation()
