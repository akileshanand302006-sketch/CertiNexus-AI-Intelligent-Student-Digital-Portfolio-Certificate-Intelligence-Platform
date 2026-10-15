"""
CertiNexus AI — Classifier Calibration

Provides CalibratedClassifierCV wrappers for LinearSVC and other
classifiers that don't natively support predict_proba.

Also provides top-N prediction with uncertainty scoring.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple

from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB


class CalibratedClassifierWrapper:
    """
    Wrapper that adds probability calibration and top-N predictions.

    For LinearSVC (which doesn't have predict_proba), wraps with
    CalibratedClassifierCV using Platt scaling (sigmoid) or
    isotonic regression.

    Parameters
    ----------
    base_classifier : estimator
        The base sklearn classifier.
    calibration_method : str
        'sigmoid' (Platt scaling) or 'isotonic'.
    cv : int
        Cross-validation folds for calibration.
    """

    def __init__(
        self,
        base_classifier,
        calibration_method: str = "sigmoid",
        cv: int = 5,
    ):
        self.base_classifier = base_classifier
        self.calibration_method = calibration_method
        self.cv = cv
        self.calibrated_model = None
        self.is_fitted = False
        self.classes_ = None

    def fit(self, X, y):
        """Fit the calibrated classifier."""
        needs_calibration = isinstance(
            self.base_classifier, LinearSVC
        ) or not hasattr(self.base_classifier, "predict_proba")

        if needs_calibration:
            self.calibrated_model = CalibratedClassifierCV(
                estimator=self.base_classifier,
                method=self.calibration_method,
                cv=self.cv,
            )
            self.calibrated_model.fit(X, y)
            self.classes_ = self.calibrated_model.classes_
        else:
            self.base_classifier.fit(X, y)
            self.calibrated_model = self.base_classifier
            self.classes_ = self.base_classifier.classes_

        self.is_fitted = True
        return self

    def predict(self, X):
        """Predict class labels."""
        return self.calibrated_model.predict(X)

    def predict_proba(self, X):
        """Predict class probabilities."""
        return self.calibrated_model.predict_proba(X)

    def predict_top_n(
        self, X, n: int = 3
    ) -> List[List[Dict]]:
        """
        Get top-N predictions with probabilities.

        Returns
        -------
        predictions : list of list of dict
            For each sample, a list of top-N predictions:
            [{"class": str, "probability": float}, ...]
        """
        probas = self.predict_proba(X)
        results = []

        for proba in probas:
            top_indices = np.argsort(proba)[::-1][:n]
            predictions = []
            for idx in top_indices:
                predictions.append({
                    "class": str(self.classes_[idx]),
                    "probability": float(proba[idx]),
                })
            results.append(predictions)

        return results

    def uncertainty_score(self, X) -> np.ndarray:
        """
        Compute prediction uncertainty (entropy of probabilities).

        Returns
        -------
        uncertainties : np.ndarray
            Higher values = more uncertain predictions.
        """
        probas = self.predict_proba(X)
        # Clip to avoid log(0)
        probas = np.clip(probas, 1e-10, 1.0)
        entropy = -np.sum(probas * np.log2(probas), axis=1)
        # Normalize by max possible entropy
        max_entropy = np.log2(len(self.classes_))
        return entropy / max_entropy if max_entropy > 0 else entropy


def create_classifier_configs():
    """
    Create all classifier configurations for the experiment matrix.

    Returns 3 classifiers x 3 feature sets = 9 experiments.
    """
    classifiers = {
        "MultinomialNB": {
            "classifier": MultinomialNB(),
            "param_grid": {
                "classifier__alpha": [0.01, 0.1, 0.5, 1.0, 2.0],
            },
            "supports_negative": False,
        },
        "LogisticRegression": {
            "classifier": LogisticRegression(
                max_iter=2000,
                solver="saga",
                random_state=42,
            ),
            "param_grid": {
                "classifier__C": [0.01, 0.1, 1.0, 10.0, 100.0],
                "classifier__penalty": ["l1", "l2"],
            },
            "supports_negative": True,
        },
        "LinearSVC": {
            "classifier": LinearSVC(
                max_iter=3000,
                random_state=42,
            ),
            "param_grid": {
                "classifier__C": [0.01, 0.1, 1.0, 10.0],
                "classifier__loss": ["hinge", "squared_hinge"],
            },
            "supports_negative": True,
        },
    }
    return classifiers
