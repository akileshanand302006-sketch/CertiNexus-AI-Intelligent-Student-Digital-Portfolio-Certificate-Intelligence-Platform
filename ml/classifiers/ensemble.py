"""
CertiNexus AI — Ensemble Classifier Evaluation

Implements soft-voting ensemble from the best models of each type,
with model disagreement tracking.

The ensemble is only retained if it genuinely improves held-out
Macro-F1 over the single best model.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple

from sklearn.metrics import f1_score, accuracy_score


class EnsembleEvaluator:
    """
    Evaluate ensemble combinations of trained models.

    Implements:
    - Soft voting (average predicted probabilities)
    - Hard voting (majority class)
    - Model disagreement tracking
    - Performance comparison vs single best model

    Parameters
    ----------
    models : dict
        Dict of {name: (model, feature_pipeline)} pairs.
        Each model must support predict_proba or decision_function.
    """

    def __init__(self, models: Optional[Dict] = None):
        self.models = models or {}
        self.ensemble_result = None

    def add_model(self, name: str, model, feature_pipeline=None):
        """Add a model to the ensemble candidates."""
        self.models[name] = (model, feature_pipeline)

    def soft_vote_predict(
        self, X, models_to_use: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict using soft voting (averaged probabilities).

        Parameters
        ----------
        X : array-like
            Input features (raw text if using feature pipelines).
        models_to_use : list of str, optional
            Subset of models to use. Uses all if None.

        Returns
        -------
        predictions : np.ndarray
            Predicted class indices.
        avg_probas : np.ndarray
            Averaged probability matrix.
        """
        names = models_to_use or list(self.models.keys())
        all_probas = []

        for name in names:
            model, pipeline = self.models[name]
            if pipeline is not None:
                X_transformed = pipeline.transform(X)
            else:
                X_transformed = X

            if hasattr(model, "predict_proba"):
                probas = model.predict_proba(X_transformed)
            elif hasattr(model, "decision_function"):
                decision = model.decision_function(X_transformed)
                if decision.ndim == 1:
                    decision = np.column_stack([-decision, decision])
                # Softmax normalization
                exp_d = np.exp(decision - decision.max(axis=1, keepdims=True))
                probas = exp_d / exp_d.sum(axis=1, keepdims=True)
            else:
                continue

            all_probas.append(probas)

        if not all_probas:
            raise ValueError("No models with probability support")

        avg_probas = np.mean(all_probas, axis=0)
        predictions = np.argmax(avg_probas, axis=1)

        return predictions, avg_probas

    def hard_vote_predict(
        self, X, models_to_use: Optional[List[str]] = None
    ) -> np.ndarray:
        """Predict using hard voting (majority class)."""
        names = models_to_use or list(self.models.keys())
        all_preds = []

        for name in names:
            model, pipeline = self.models[name]
            if pipeline is not None:
                X_transformed = pipeline.transform(X)
            else:
                X_transformed = X
            preds = model.predict(X_transformed)
            all_preds.append(preds)

        # Majority vote
        all_preds = np.array(all_preds)  # (n_models, n_samples)
        from scipy.stats import mode
        majority, _ = mode(all_preds, axis=0, keepdims=False)
        return majority.flatten()

    def compute_disagreement(
        self, X, models_to_use: Optional[List[str]] = None
    ) -> Dict:
        """
        Compute model disagreement metrics.

        Returns
        -------
        dict with:
            - disagreement_rate: fraction of samples where models disagree
            - per_sample_agreement: list of agreement scores per sample
            - disagreement_indices: indices where models disagree
        """
        names = models_to_use or list(self.models.keys())
        all_preds = []

        for name in names:
            model, pipeline = self.models[name]
            if pipeline is not None:
                X_transformed = pipeline.transform(X)
            else:
                X_transformed = X
            preds = model.predict(X_transformed)
            all_preds.append(preds)

        all_preds = np.array(all_preds)
        n_models = len(all_preds)
        n_samples = all_preds.shape[1]

        # Agreement: fraction of models that agree with the majority
        agreements = []
        disagreement_indices = []

        for i in range(n_samples):
            sample_preds = all_preds[:, i]
            unique, counts = np.unique(sample_preds, return_counts=True)
            max_agreement = counts.max() / n_models
            agreements.append(max_agreement)
            if max_agreement < 1.0:
                disagreement_indices.append(i)

        disagreement_rate = len(disagreement_indices) / n_samples

        return {
            "disagreement_rate": round(disagreement_rate, 4),
            "num_disagreements": len(disagreement_indices),
            "num_samples": n_samples,
            "disagreement_indices": disagreement_indices,
            "mean_agreement": round(float(np.mean(agreements)), 4),
        }

    def evaluate_ensemble(
        self,
        X, y,
        single_best_f1: float,
        models_to_use: Optional[List[str]] = None,
    ) -> Dict:
        """
        Evaluate the ensemble and compare against single best model.

        Parameters
        ----------
        X : array-like
            Test features.
        y : array-like
            True labels.
        single_best_f1 : float
            Macro-F1 of the single best model.
        models_to_use : list of str, optional
            Models to include in ensemble.

        Returns
        -------
        dict with evaluation results and retain recommendation.
        """
        # Soft voting
        soft_preds, soft_probas = self.soft_vote_predict(
            X, models_to_use
        )
        soft_f1 = f1_score(y, soft_preds, average="macro")
        soft_acc = accuracy_score(y, soft_preds)

        # Hard voting
        hard_preds = self.hard_vote_predict(X, models_to_use)
        hard_f1 = f1_score(y, hard_preds, average="macro")
        hard_acc = accuracy_score(y, hard_preds)

        # Disagreement
        disagreement = self.compute_disagreement(X, models_to_use)

        # Best ensemble strategy
        best_strategy = "soft" if soft_f1 >= hard_f1 else "hard"
        best_f1 = max(soft_f1, hard_f1)

        # Should we retain the ensemble?
        improvement = best_f1 - single_best_f1
        retain = improvement > 0.005  # Must improve by > 0.5%

        result = {
            "soft_voting": {
                "macro_f1": round(soft_f1, 4),
                "accuracy": round(soft_acc, 4),
            },
            "hard_voting": {
                "macro_f1": round(hard_f1, 4),
                "accuracy": round(hard_acc, 4),
            },
            "best_strategy": best_strategy,
            "best_f1": round(best_f1, 4),
            "single_best_f1": round(single_best_f1, 4),
            "improvement": round(improvement, 4),
            "retain_ensemble": retain,
            "disagreement": disagreement,
            "models_used": models_to_use or list(self.models.keys()),
        }

        self.ensemble_result = result
        return result
