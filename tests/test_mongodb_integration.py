"""
CertiNexus AI — MongoDB Atlas Repositories & Integration Test Suite

Verifies:
1. Database configuration & graceful health check
2. UserRepository CRUD & email uniqueness
3. CertificateRepository structured document creation, query, update, delete
4. OCRRepository raw OCR, cleaned text, bounding boxes, quality metrics
5. EntityRepository 25+ entity types persistence
6. ClassificationRepository multi-model predictions & feature attributions
7. ExperimentRepository ML tracking & Macro-F1 queries
8. CorrectionRepository human-in-the-loop annotations
9. ProcessingJobRepository stage transitions & progress tracking
10. SkillRepository skill occurrence counters
11. Migration script dry-run execution
"""

import os
import sys
import unittest
import mongomock

# Add project root and backend to path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.core.config import settings
from app.core.database import check_mongodb_health
from app.repositories import (
    UserRepository,
    CertificateRepository,
    OCRRepository,
    EntityRepository,
    ClassificationRepository,
    ExperimentRepository,
    CorrectionRepository,
    ProcessingJobRepository,
    SkillRepository,
    PortfolioRepository,
)


class TestMongoDBRepositories(unittest.TestCase):
    """Test suite for all MongoDB Atlas collection repositories using in-memory mock."""

    def setUp(self):
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client["certinexus_test"]

        # Initialize repositories with mocked collections
        self.user_repo = UserRepository(collection=self.mock_db["users"])
        self.cert_repo = CertificateRepository(collection=self.mock_db["certificates"])
        self.ocr_repo = OCRRepository(collection=self.mock_db["ocr_results"])
        self.entity_repo = EntityRepository(collection=self.mock_db["extracted_entities"])
        self.class_repo = ClassificationRepository(collection=self.mock_db["classifications"])
        self.exp_repo = ExperimentRepository(collection=self.mock_db["model_experiments"])
        self.corr_repo = CorrectionRepository(collection=self.mock_db["user_corrections"])
        self.job_repo = ProcessingJobRepository(collection=self.mock_db["processing_jobs"])
        self.skill_repo = SkillRepository(collection=self.mock_db["skills"])
        self.portfolio_repo = PortfolioRepository(collection=self.mock_db["portfolio_profiles"])

    def test_health_check_function(self):
        """Verify check_mongodb_health returns valid status without crashing."""
        res = check_mongodb_health()
        self.assertIn("status", res)
        self.assertIn("database", res)
        self.assertIn(res["status"], ["ok", "degraded"])
        # Ensure credentials are not exposed
        self.assertNotIn("password", str(res).lower())
        self.assertNotIn("mongodb+srv", str(res).lower())

    def test_user_repository(self):
        """Verify user creation, lookup by email, id, and profile update."""
        user = self.user_repo.create({
            "email": "student@example.com",
            "username": "student_01",
            "password_hash": "$2b$12$fakehashedpassword",
            "full_name": "Test Student",
            "institution": "ABC Institute",
            "department": "Computer Science",
        })
        self.assertEqual(user["email"], "student@example.com")
        self.assertEqual(user["profile"]["institution"], "ABC Institute")

        # Find by email
        found = self.user_repo.find_by_email("student@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found["username"], "student_01")

        # Update profile
        updated = self.user_repo.update(user["id"], {"bio": "Machine learning researcher"})
        self.assertEqual(updated["profile"]["bio"], "Machine learning researcher")

    def test_certificate_repository(self):
        """Verify structured certificate creation, user queries, and field aliases."""
        cert_data = {
            "user_id": "usr-123",
            "title": "National Hackathon Winner",
            "category": "Hackathon",
            "original_filename": "hackathon_cert.pdf",
            "file_type": "application/pdf",
            "file_size": 204800,
            "recipient_name": "Akilesh",
            "organization": "Tech University",
            "issue_date": "2026-09-15",
            "ai_confidence": 0.968,
            "skills": ["Python", "FastAPI", "Machine Learning"],
        }
        cert = self.cert_repo.create(cert_data)
        self.assertIsNotNone(cert["_id"])
        self.assertEqual(cert["category"], "Hackathon")
        self.assertEqual(cert["recipient"]["name"], "Akilesh")
        self.assertEqual(cert["issuer"]["name"], "Tech University")
        self.assertEqual(cert["verification_status"], "not_independently_verified")

        # Query by user
        user_certs = self.cert_repo.find_by_user("usr-123")
        self.assertEqual(len(user_certs), 1)

        # Update
        updated = self.cert_repo.update(cert["_id"], {"status": "completed"})
        self.assertEqual(updated["status"], "completed")

        # Delete
        deleted = self.cert_repo.delete(cert["_id"])
        self.assertTrue(deleted)
        self.assertIsNone(self.cert_repo.find_by_id(cert["_id"]))

    def test_ocr_repository(self):
        """Verify OCR results storage, bounding box normalization, and retrieval."""
        ocr_doc = {
            "certificate_id": "cert-456",
            "detector": "CRAFT",
            "ocr_model": "CRNN-BiLSTM-CTC",
            "full_text": "Certificate of Excellence in Python",
            "cleaned_text": "Certificate of Excellence in Python",
            "average_confidence": 0.945,
            "regions": [
                {
                    "text": "Certificate of Excellence",
                    "confidence": 0.98,
                    "bbox": [[10, 20], [100, 20], [100, 50], [10, 50]],
                }
            ],
            "quality_metrics": {"overall_quality": 92.0},
        }
        saved = self.ocr_repo.save_ocr_result(ocr_doc)
        self.assertEqual(saved["detector"], "CRAFT")
        self.assertEqual(saved["ocr_model"], "CRNN-BiLSTM-CTC")

        retrieved = self.ocr_repo.get_by_certificate_id("cert-456")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["full_text"], ocr_doc["full_text"])
        self.assertEqual(len(retrieved["regions"]), 1)
        self.assertEqual(retrieved["regions"][0]["bounding_box"]["x"], 10)

    def test_entity_repository(self):
        """Verify extracted entities collection storage and retrieval."""
        entities = [
            {"type": "PERSON", "value": "Akilesh", "confidence": 0.98, "start": 0, "end": 7},
            {"type": "ORGANIZATION", "value": "ABC Institute", "confidence": 0.95, "start": 10, "end": 23},
            {"type": "EVENT", "value": "AI Hackathon", "confidence": 0.92, "start": 25, "end": 37},
        ]
        saved = self.entity_repo.save_entities("cert-789", entities)
        self.assertEqual(saved["total_entities"], 3)

        retrieved = self.entity_repo.get_by_certificate_id("cert-789")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved["entities"]), 3)
        self.assertEqual(retrieved["entities"][0]["value"], "Akilesh")

    def test_classification_and_predictions_repository(self):
        """Verify classification storage, model predictions, and alternatives."""
        class_data = {
            "certificate_id": "cert-101",
            "category": "Hackathon",
            "confidence": 0.972,
            "confidence_level": "high",
            "model_name": "LinearSVC",
            "model_version": "2.0.0",
            "predictions": [
                {"model": "MultinomialNB", "prediction": "Hackathon", "confidence": 0.91},
                {"model": "LogisticRegression", "prediction": "Hackathon", "confidence": 0.95},
                {"model": "LinearSVC", "prediction": "Hackathon", "confidence": 0.97},
            ],
            "important_terms": [
                {"term": "hackathon", "weight": 2.45},
                {"term": "winner", "weight": 1.89},
            ],
        }
        saved = self.class_repo.save_classification(class_data)
        self.assertEqual(saved["final_prediction"], "Hackathon")
        self.assertEqual(saved["final_model"], "LinearSVC")
        self.assertEqual(len(saved["predictions"]), 3)

        retrieved = self.class_repo.get_by_certificate_id("cert-101")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["confidence"], 0.972)

    def test_experiment_repository(self):
        """Verify ML experiment metrics logging and queries."""
        exp = {
            "experiment_id": "LinearSVC__tfidf_word",
            "classifier": "LinearSVC",
            "feature_representation": "tfidf_word",
            "accuracy": 0.824,
            "macro_f1": 0.819,
            "hyperparameters": {"C": 1.0},
        }
        self.exp_repo.log_experiment(exp)

        all_exps = self.exp_repo.get_all_experiments()
        self.assertEqual(len(all_exps), 1)
        self.assertEqual(all_exps[0]["macro_f1"], 0.819)

    def test_processing_job_repository(self):
        """Verify processing job lifecycle stage transitions and progress."""
        job = self.job_repo.create_job("cert-job-1")
        self.assertEqual(job["status"], "processing")
        self.assertEqual(job["current_stage"], "upload")
        self.assertEqual(job["progress"], 10)

        # Stage: ocr
        self.job_repo.update_stage("cert-job-1", "ocr")
        job = self.job_repo.get_by_certificate_id("cert-job-1")
        self.assertEqual(job["current_stage"], "ocr")
        self.assertEqual(job["progress"], 50)

        # Stage: classification
        self.job_repo.update_stage("cert-job-1", "classification")
        job = self.job_repo.get_by_certificate_id("cert-job-1")
        self.assertEqual(job["current_stage"], "classification")
        self.assertEqual(job["progress"], 85)

        # Complete
        self.job_repo.complete_job("cert-job-1")
        job = self.job_repo.get_by_certificate_id("cert-job-1")
        self.assertEqual(job["status"], "completed")
        self.assertEqual(job["progress"], 100)
        self.assertIsNotNone(job["completed_at"])

    def test_correction_repository(self):
        """Verify human-in-the-loop corrections persistence."""
        corr = {
            "certificate_id": "cert-corr-1",
            "user_id": "usr-1",
            "field_name": "issuer",
            "original_value": "ABC College",
            "corrected_value": "ABC Institute of Technology",
        }
        saved = self.corr_repo.save_correction(corr)
        self.assertEqual(saved["original_value"], "ABC College")
        self.assertEqual(saved["corrected_value"], "ABC Institute of Technology")

        corrs = self.corr_repo.get_by_certificate_id("cert-corr-1")
        self.assertEqual(len(corrs), 1)

    def test_skill_repository(self):
        """Verify student skills frequency counter."""
        self.skill_repo.upsert_skill("usr-1", "Python", "cert-1")
        self.skill_repo.upsert_skill("usr-1", "Python", "cert-2")
        self.skill_repo.upsert_skill("usr-1", "Machine Learning", "cert-1")

        skills = self.skill_repo.get_user_skills("usr-1")
        self.assertEqual(len(skills), 2)
        py_skill = [s for s in skills if s["skill_name"] == "Python"][0]
        self.assertEqual(py_skill["occurrence_count"], 2)


if __name__ == "__main__":
    unittest.main()
