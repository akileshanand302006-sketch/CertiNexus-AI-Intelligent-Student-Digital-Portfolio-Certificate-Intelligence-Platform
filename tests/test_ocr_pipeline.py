"""
CertiNexus AI — Unit Tests for OCR Preprocessing & Postprocessing
"""

import os
import sys
import unittest
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.ocr.preprocessing import ImagePreprocessor
from ml.ocr.postprocessor import OCRPostProcessor


class TestOCRPipeline(unittest.TestCase):
    """Test OCR preprocessing and intelligent postprocessing."""

    def setUp(self):
        self.preprocessor = ImagePreprocessor()
        self.postprocessor = OCRPostProcessor()

    def test_image_quality_scoring(self):
        """Verify quality metric computation on synthetic image array."""
        fake_img = np.random.randint(40, 220, (300, 400, 3), dtype=np.uint8)
        metrics = self.preprocessor.compute_quality_score(fake_img)
        self.assertIn("quality_score", metrics)
        self.assertIn("brightness", metrics)
        self.assertIn("contrast", metrics)
        self.assertIn("sharpness", metrics)
        self.assertGreaterEqual(metrics["quality_score"], 0.0)
        self.assertLessEqual(metrics["quality_score"], 100.0)


    def test_image_preprocessing_steps(self):
        """Verify image preprocessing pipeline execution."""
        fake_img = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        res = self.preprocessor.preprocess(fake_img, steps=["grayscale", "denoise"])
        self.assertIsNotNone(res.processed_image)
        self.assertEqual(len(res.steps_applied), 2)

    def test_postprocessor_corrections(self):
        """Verify domain OCR error correction (digits, dates, keywords)."""
        noisy_text = "Certif1cate of Complet1on awarded for Pyth0n programming on l2/O5/2O23. CERT-O12345 |||"
        res = self.postprocessor.process(noisy_text)
        cleaned = res.cleaned_text

        # Verify artifact removal
        self.assertNotIn("|||", cleaned)
        # Verify OCR typo corrections
        self.assertIn("certificate", cleaned.lower())
        self.assertIn("completion", cleaned.lower())
        self.assertIn("2023", cleaned)
        self.assertGreater(res.num_corrections, 0)


if __name__ == "__main__":
    unittest.main()
