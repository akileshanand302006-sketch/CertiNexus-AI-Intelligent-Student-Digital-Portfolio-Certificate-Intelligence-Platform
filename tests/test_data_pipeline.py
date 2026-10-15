"""
CertiNexus AI — Unit Tests for Data Pipeline
Validates data loaders, integrity validation, stratified splitting, and leakage prevention.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.data.loaders import load_capcc_v1
from ml.data.validation import DatasetValidator
from ml.data.splits import create_stratified_splits


class TestDataPipeline(unittest.TestCase):
    """Test dataset loading, validation, and splitting."""

    @classmethod
    def setUpClass(cls):
        cls.df, cls.info = load_capcc_v1()

    def test_load_capcc_v1(self):
        """Verify CAPCC-v1 loads correctly and contains expected columns."""
        self.assertIsNotNone(self.df)
        self.assertEqual(len(self.df), 605)
        self.assertIn("clean_text", self.df.columns)
        self.assertIn("category", self.df.columns)
        self.assertEqual(len(self.df["category"].unique()), 11)

    def test_dataset_validator(self):
        """Verify DatasetValidator runs all integrity checks without critical errors."""
        validator = DatasetValidator()
        report = validator.validate(self.df, dataset_info=self.info)
        self.assertTrue(report.passed)
        self.assertEqual(report.num_errors, 0)


    def test_stratified_splits_distribution(self):
        """Verify stratified split maintains class balance and sizes."""
        splits = create_stratified_splits(self.df, test_size=0.15, val_size=0.15, random_seed=42)
        total = len(splits.X_train) + len(splits.X_val) + len(splits.X_test)
        self.assertEqual(total, 605)

        # Check all 11 classes are present in train, val, and test
        self.assertEqual(len(set(splits.y_train)), 11)
        self.assertEqual(len(set(splits.y_val)), 11)
        self.assertEqual(len(set(splits.y_test)), 11)

    def test_no_data_leakage(self):
        """Verify that train, val, and test index sets are strictly disjoint."""
        splits = create_stratified_splits(self.df, test_size=0.15, val_size=0.15, random_seed=42)
        train_set = set(splits.train_indices)
        val_set = set(splits.val_indices)
        test_set = set(splits.test_indices)

        self.assertEqual(len(train_set.intersection(val_set)), 0)
        self.assertEqual(len(train_set.intersection(test_set)), 0)
        self.assertEqual(len(val_set.intersection(test_set)), 0)


if __name__ == "__main__":
    unittest.main()
