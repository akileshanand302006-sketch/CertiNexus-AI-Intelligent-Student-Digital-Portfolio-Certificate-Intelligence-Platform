"""
CertiNexus AI — Automated Unit & Pipeline Tests
Uses Python's standard unittest framework for universal test execution.
"""

import os
import sys
import unittest
import uuid

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestTextPreprocessor(unittest.TestCase):
    """Verify that CertificateTextPreprocessor correctly cleans and normalizes text."""

    def setUp(self):
        from ml.preprocessing.text_preprocessor import CertificateTextPreprocessor
        self.preprocessor = CertificateTextPreprocessor()

    def test_lowercase_and_whitespace(self):
        raw = "  THIS IS A CERTIFICATE   OF COMPLETION \n\n FOR HACKATHON 2026   "
        result = self.preprocessor.transform([raw])[0]
        self.assertIn("certificate", result)
        self.assertIn("hackathon", result)
        self.assertNotIn("  ", result)

    def test_noise_removal(self):
        raw = "Certified by Google Cloud ###$$$*** 2026-09-16"
        result = self.preprocessor.transform([raw])[0]
        self.assertIn("certified", result)
        self.assertIn("google", result)
        self.assertIn("cloud", result)


class TestMLPredictor(unittest.TestCase):
    """Verify that the production ML model loads and predicts expected categories."""

    def setUp(self):
        from ml.inference.predictor import CertificateClassifier
        model_dir = os.path.join(PROJECT_ROOT, "ml", "models", "production")
        self.classifier = CertificateClassifier(model_dir=model_dir)
        self.classifier.load()

    def test_hackathon_prediction(self):
        text = "Certificate of Achievement awarded to John Doe for winning First Prize in the 24-hour National Hackathon and Codefest 2026."
        pred = self.classifier.predict(text)
        self.assertEqual(pred["category"], "Hackathon")
        self.assertGreater(pred["confidence"], 0.30)
        self.assertTrue(len(pred.get("important_terms", [])) > 0)

    def test_internship_prediction(self):
        text = "This is to certify that Jane Doe successfully completed a summer software engineering internship as a trainee at Microsoft."
        pred = self.classifier.predict(text)
        self.assertEqual(pred["category"], "Internship")
        self.assertGreater(pred["confidence"], 0.30)

    def test_workshop_prediction(self):
        text = "Certificate of Participation presented to student for completing hands-on practical workshop and bootcamp on Deep Learning."
        pred = self.classifier.predict(text)
        self.assertEqual(pred["category"], "Workshop")
        self.assertGreater(pred["confidence"], 0.30)


class TestBackendAPI(unittest.TestCase):
    """Verify FastAPI application routes and startup."""

    def get_auth_headers(self, client):
        """Helper to register and login a test user to get a bearer token."""
        unique_id = str(uuid.uuid4())[:8]
        reg_payload = {
            "email": f"test_{unique_id}@example.com",
            "username": f"user_{unique_id}",
            "password": "TestPassword123!",
            "full_name": "Test Student"
        }
        res = client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 200)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_health_check(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app

        with TestClient(app) as client:
            res = client.get("/api/health")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "healthy")

    def test_admin_dataset_statistics(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app

        with TestClient(app) as client:
            headers = self.get_auth_headers(client)
            res = client.get("/api/admin/dataset-statistics", headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertGreater(data.get("total_samples", 0), 0)
            self.assertEqual(data.get("total_categories", 0), 11)

    def test_admin_model_performance(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app

        with TestClient(app) as client:
            headers = self.get_auth_headers(client)
            res = client.get("/api/admin/model-performance", headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("metrics", data)
            self.assertIn("accuracy", data["metrics"])

    def test_resume_data_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app

        with TestClient(app) as client:
            headers = self.get_auth_headers(client)
            res = client.get("/api/resume/data", headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("headline", data)
            self.assertIn("skills", data)
            self.assertIn("certificates", data)


if __name__ == "__main__":
    unittest.main()
