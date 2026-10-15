"""
CertiNexus AI — Unit Tests for NER & Structured Extraction
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.extraction.rule_ner import RuleBasedNER
from ml.extraction.skills import SkillDatabase
from ml.extraction.certificate_fields import CategoryFieldExtractor
from ml.extraction.duplicate_detector import DuplicateDetector


class TestNERAndExtraction(unittest.TestCase):
    """Test Named Entity Recognition and category-specific field structuring."""

    def setUp(self):
        self.ner = RuleBasedNER()
        self.skill_db = SkillDatabase()
        self.field_extractor = CategoryFieldExtractor()
        self.duplicate_detector = DuplicateDetector()

        self.sample_text = (
            "Certificate of Completion. This is to certify that Alex Mercer has "
            "successfully completed the Machine Learning Specialization with Grade A (Score: 95%) "
            "issued by Stanford Online on October 10, 2024. "
            "Certificate ID: CERT-STANFORD-2024-9988. "
            "Key skills covered: Python, PyTorch, Docker, Kubernetes."
        )

    def test_rule_based_ner_entities(self):
        """Verify extraction of standard certificate entities."""
        res = self.ner.extract(self.sample_text)
        self.assertGreater(res.num_entities, 0)

        # Check person name or certificate ID or date
        types = [e.entity_type for e in res.entities]
        self.assertIn("PERSON_NAME", types)
        self.assertIn("DATE", types)
        self.assertIn("CERTIFICATE_ID", types)

    def test_skill_database_extraction(self):
        """Verify multi-category technology and skill extraction."""
        skills = self.skill_db.extract_skills(self.sample_text)
        skill_names = [s.text for s in skills]
        self.assertIn("Python", skill_names)
        self.assertIn("PyTorch", skill_names)
        self.assertIn("Docker", skill_names)

    def test_category_field_extractor(self):
        """Verify structured certificate fields by category."""
        fields = self.field_extractor.extract(self.sample_text, category="Course Completion")
        self.assertIsNotNone(fields.holder_name)
        self.assertIn("Alex", fields.holder_name)
        self.assertGreater(fields.completeness_score, 0.0)

    def test_duplicate_detector(self):
        """Verify duplicate hash generation and comparison."""
        h1 = self.duplicate_detector.compute_text_hash(self.sample_text)
        h2 = self.duplicate_detector.compute_text_hash(self.sample_text)
        h3 = self.duplicate_detector.compute_text_hash("Different certificate content")
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)


if __name__ == "__main__":
    unittest.main()
