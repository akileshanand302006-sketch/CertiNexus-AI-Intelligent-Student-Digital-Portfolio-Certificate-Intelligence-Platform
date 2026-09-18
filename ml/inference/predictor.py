"""
CertiNexus AI — Production ML Inference

Provides the production prediction API used by the FastAPI backend.
Loads the serialized pipeline and provides predict/predict_proba.
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np


class CertificateClassifier:
    """
    Production certificate classifier.

    Loads the trained sklearn pipeline and provides prediction
    with confidence scores and explainability.
    """

    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "ml", "models", "production"
            )

        self.model_dir = model_dir
        self.pipeline = None
        self.label_encoder = None
        self.metadata = None
        self.is_loaded = False

    def load(self):
        """Load the production model artifacts."""
        pipeline_path = os.path.join(self.model_dir, "certificate_classifier.joblib")
        le_path = os.path.join(self.model_dir, "label_encoder.joblib")
        meta_path = os.path.join(self.model_dir, "model_metadata.json")

        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Model not found at {pipeline_path}")

        self.pipeline = joblib.load(pipeline_path)
        self.label_encoder = joblib.load(le_path)

        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)

        self.is_loaded = True
        return self

    def predict(self, text: str) -> Dict:
        """
        Predict the category of a certificate text.

        Returns dict with category, confidence, processing_time,
        and important features.
        """
        if not self.is_loaded:
            self.load()

        start_time = time.time()

        # Predict class
        y_pred = self.pipeline.predict([text])
        category = self.label_encoder.inverse_transform(y_pred)[0]

        # Get confidence (probability or decision function)
        confidence = self._get_confidence(text)

        # Get important features
        important_terms = self._get_important_features(text, y_pred[0])

        processing_time = time.time() - start_time

        return {
            "category": category,
            "confidence": float(confidence),
            "confidence_level": self._confidence_level(confidence),
            "important_terms": important_terms,
            "processing_time_ms": round(processing_time * 1000, 2),
            "model_version": self.metadata.get("version", "unknown") if self.metadata else "unknown",
        }

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Predict categories for a batch of texts."""
        return [self.predict(text) for text in texts]

    def _get_confidence(self, text: str) -> float:
        """Extract prediction confidence."""
        classifier = self.pipeline.named_steps.get("classifier")
        vectorizer = self.pipeline.named_steps.get("vectorizer")

        if vectorizer is None:
            # Try FeatureUnion-based pipeline
            for name, step in self.pipeline.steps:
                if name == "vectorizer":
                    vectorizer = step
                    break

        if vectorizer is None:
            return 0.0

        X_transformed = vectorizer.transform([text])

        # Use decision_function with temperature scaling for well-calibrated multi-class confidence
        if hasattr(classifier, 'decision_function'):
            decision = classifier.decision_function(X_transformed)
            if decision.ndim == 2:
                # Temperature scaling calibrated for L2 regularized multi-class classifier
                T = 0.10
                scaled = decision / T
                exp_scores = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))
                proba = exp_scores / exp_scores.sum(axis=1, keepdims=True)
                return float(np.max(proba))
            else:
                return float(1 / (1 + np.exp(-abs(decision[0]))))

        # Fall back to predict_proba (Naive Bayes)
        if hasattr(classifier, 'predict_proba'):
            proba = classifier.predict_proba(X_transformed)
            return float(np.max(proba))

        return 0.0

    def _confidence_level(self, confidence: float) -> str:
        """Map confidence to a human-readable level."""
        if confidence >= 0.80:
            return "high"
        elif confidence >= 0.50:
            return "medium"
        else:
            return "low"

    def _get_important_features(self, text: str, predicted_class: int,
                                top_n: int = 8) -> List[Dict]:
        """Extract the most influential features for the prediction."""
        try:
            classifier = self.pipeline.named_steps.get("classifier")
            vectorizer = self.pipeline.named_steps.get("vectorizer")

            if vectorizer is None or classifier is None:
                return []

            X_transformed = vectorizer.transform([text])

            # Get feature names
            if hasattr(vectorizer, 'get_feature_names_out'):
                feature_names = vectorizer.get_feature_names_out()
            else:
                return []

            # Get feature weights for predicted class
            if hasattr(classifier, 'coef_'):
                if classifier.coef_.ndim == 2:
                    weights = classifier.coef_[predicted_class]
                else:
                    weights = classifier.coef_[0]
            elif hasattr(classifier, 'feature_log_prob_'):
                weights = classifier.feature_log_prob_[predicted_class]
            else:
                return []

            # Find non-zero features in input
            nonzero_indices = X_transformed.nonzero()[1]
            feature_weights = []

            for idx in nonzero_indices:
                if idx < len(feature_names) and idx < len(weights):
                    feature_weights.append({
                        "term": str(feature_names[idx]),
                        "weight": float(weights[idx]),
                    })

            # Sort by absolute weight and return top N
            feature_weights.sort(key=lambda x: abs(x["weight"]), reverse=True)
            return feature_weights[:top_n]

        except Exception:
            return []

    def get_model_info(self) -> Dict:
        """Return model metadata."""
        if not self.is_loaded:
            self.load()
        return self.metadata or {}


# Singleton instance for the application
_classifier_instance = None

def get_classifier() -> CertificateClassifier:
    """Get or create the singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CertificateClassifier()
        _classifier_instance.load()
    return _classifier_instance


if __name__ == "__main__":
    # Test inference
    classifier = CertificateClassifier()
    classifier.load()

    test_texts = [
        "This certificate is awarded to John for participating in the Smart India Hackathon organized by AICTE. The team developed an innovative solution for healthcare.",
        "Certificate of completion. Sarah has successfully completed the AWS Cloud Practitioner certification examination. Score: 850/1000.",
        "This is to certify that Rahul has completed an internship at Google as a Software Development Intern for 3 months.",
        "Certificate of participation in the Annual Sports Day. Priya participated in badminton and secured First Place.",
    ]

    print("=" * 60)
    print("CertiNexus AI — Inference Test")
    print("=" * 60)

    for text in test_texts:
        result = classifier.predict(text)
        print(f"\n  Text: {text[:80]}...")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Level: {result['confidence_level']}")
        print(f"  Time: {result['processing_time_ms']}ms")
        if result['important_terms']:
            terms = ', '.join(t['term'] for t in result['important_terms'][:5])
            print(f"  Key terms: {terms}")
