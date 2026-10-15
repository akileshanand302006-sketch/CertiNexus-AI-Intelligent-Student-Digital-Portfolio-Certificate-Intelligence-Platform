"""
CertiNexus AI — Feature Attribution

Per-prediction feature importance analysis showing which
words/features contributed most to the classification decision.
"""

import numpy as np
from typing import Dict, List, Optional

from sklearn.base import BaseEstimator


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am",
    "an", "and", "any", "are", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "could", "did", "do", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having",
    "he", "her", "here", "hers", "him", "his", "how", "i", "if", "in",
    "into", "is", "it", "its", "me", "more", "most", "my", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "our",
    "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "them", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "would", "you", "your",
}


class FeatureAttributor:
    """
    Compute per-prediction feature attributions for linear classifiers.

    Shows which words/features had the strongest positive and negative
    influence on the classification decision.

    Parameters
    ----------
    top_n : int
        Number of top features to return per prediction.
    filter_stopwords : bool
        Whether to filter out stopword features.
    """

    def __init__(self, top_n: int = 10, filter_stopwords: bool = True):
        self.top_n = top_n
        self.filter_stopwords = filter_stopwords

    def explain(
        self,
        text: str,
        classifier,
        vectorizer,
        predicted_class: int,
        class_names: Optional[List[str]] = None,
    ) -> Dict:
        """
        Explain a single prediction.

        Parameters
        ----------
        text : str
            Input text.
        classifier : estimator
            Fitted classifier with coef_ or feature_log_prob_.
        vectorizer : transformer
            Fitted vectorizer with get_feature_names_out().
        predicted_class : int
            Index of the predicted class.
        class_names : list of str, optional
            Human-readable class names.

        Returns
        -------
        dict with positive_features, negative_features, and summary.
        """
        # Transform text
        X = vectorizer.transform([text])

        # Get feature names
        if hasattr(vectorizer, "get_feature_names_out"):
            feature_names = vectorizer.get_feature_names_out()
        else:
            return {"error": "Vectorizer has no feature names"}

        # Get weights for predicted class
        if hasattr(classifier, "coef_"):
            if classifier.coef_.ndim == 2:
                weights = classifier.coef_[predicted_class]
            else:
                weights = classifier.coef_[0]
        elif hasattr(classifier, "feature_log_prob_"):
            weights = classifier.feature_log_prob_[predicted_class]
        else:
            return {"error": "Classifier has no feature weights"}

        # Get non-zero features in input
        nonzero_indices = X.nonzero()[1]
        feature_contributions = []

        for idx in nonzero_indices:
            if idx >= len(feature_names) or idx >= len(weights):
                continue
            term = str(feature_names[idx]).strip()

            # Filter stopwords
            if self.filter_stopwords:
                tokens = term.split()
                if all(t in STOPWORDS for t in tokens):
                    continue
                if len(term) < 2:
                    continue

            w = float(weights[idx])
            tfidf_value = float(X[0, idx])
            contribution = w * tfidf_value

            feature_contributions.append({
                "term": term,
                "weight": round(w, 4),
                "tfidf": round(tfidf_value, 4),
                "contribution": round(contribution, 4),
                "direction": "positive" if w > 0 else "negative",
            })

        # Sort by contribution magnitude
        feature_contributions.sort(
            key=lambda x: abs(x["contribution"]), reverse=True
        )

        positive = [
            f for f in feature_contributions
            if f["direction"] == "positive"
        ][:self.top_n]

        negative = [
            f for f in feature_contributions
            if f["direction"] == "negative"
        ][:self.top_n]

        # Normalize importance percentages
        max_contrib = max(
            (abs(f["contribution"]) for f in feature_contributions),
            default=1.0,
        )
        for f in positive + negative:
            f["importance_pct"] = round(
                abs(f["contribution"]) / max_contrib * 100, 1
            )

        class_name = (
            class_names[predicted_class]
            if class_names else str(predicted_class)
        )

        return {
            "predicted_class": class_name,
            "predicted_class_idx": predicted_class,
            "positive_features": positive,
            "negative_features": negative,
            "positive_terms": positive,
            "negative_terms": negative,
            "num_active_features": len(feature_contributions),
            "confidence_indicator": (
                "high" if positive and positive[0]["contribution"] > 1.0
                else "medium" if positive
                else "low"
            ),
        }

