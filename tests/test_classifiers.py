"""
CertiNexus AI — Unit Tests for Feature Pipelines, Classifiers & Explainability
"""

import os
import sys
import unittest
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.data.loaders import load_capcc_v1
from ml.data.splits import create_stratified_splits
from ml.features.feature_pipeline import FeaturePipelineBuilder
from ml.classifiers.calibration import CalibratedClassifierWrapper
from ml.classifiers.ensemble import EnsembleEvaluator


class TestClassifiersAndFeatures(unittest.TestCase):
    """Test feature engineering pipelines, model calibration, and voting."""

    @classmethod
    def setUpClass(cls):
        df, _ = load_capcc_v1()
        splits = create_stratified_splits(df, test_size=0.2, val_size=0.1, random_seed=42)
        cls.X_train_raw = splits.X_train
        cls.y_train = splits.y_train
        cls.X_test_raw = splits.X_test
        cls.y_test = splits.y_test
        cls.classes = list(splits.label_encoder.classes_)

    def test_feature_pipeline_builder(self):
        """Verify all three feature set configurations."""
        configs = ["tfidf_word", "tfidf_word_char", "tfidf_enriched"]
        for cfg in configs:
            builder = FeaturePipelineBuilder.build(cfg)
            X = builder.fit_transform(self.X_train_raw[:20])
            self.assertGreater(X.shape[0], 0)
            self.assertGreater(X.shape[1], 100)

    def test_calibrated_linear_svc(self):
        """Verify CalibratedClassifierWrapper outputs calibrated probabilities and top-N."""
        pipe = FeaturePipelineBuilder.build("tfidf_word")
        X_tr = pipe.fit_transform(self.X_train_raw)
        X_te = pipe.transform(self.X_test_raw[:5])

        base_svc = LinearSVC(C=1.0, random_state=42)
        calibrated = CalibratedClassifierWrapper(base_svc, calibration_method="sigmoid", cv=3)
        calibrated.fit(X_tr, self.y_train)

        probas = calibrated.predict_proba(X_te)
        self.assertEqual(probas.shape[0], 5)
        self.assertEqual(probas.shape[1], len(self.classes))

        top_n = calibrated.predict_top_n(X_te, n=3)
        self.assertEqual(len(top_n), 5)
        self.assertEqual(len(top_n[0]), 3)
        self.assertIn("probability", top_n[0][0])

    def test_ensemble_evaluator(self):
        """Verify soft-voting ensemble mechanism."""
        pipe = FeaturePipelineBuilder.build("tfidf_word")
        X_tr = pipe.fit_transform(self.X_train_raw)
        X_te = pipe.transform(self.X_test_raw[:5])

        m1 = MultinomialNB()
        m1.fit(X_tr, self.y_train)

        m2 = CalibratedClassifierWrapper(LinearSVC(random_state=42), cv=2)
        m2.fit(X_tr, self.y_train)

        ensemble = EnsembleEvaluator()
        ensemble.add_model("nb", m1)
        ensemble.add_model("svc", m2)

        preds, avg_prob = ensemble.soft_vote_predict(X_te)
        self.assertEqual(len(preds), 5)
        self.assertEqual(avg_prob.shape[0], 5)


if __name__ == "__main__":
    unittest.main()
