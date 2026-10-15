"""
CertiNexus AI — Comprehensive API Tests
Tests all core certificate endpoints, new intelligence routes, and ML endpoints.
"""

import os
import sys
import unittest
import uuid
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app


class TestCertiNexusAPI(unittest.TestCase):
    """Test suite for FastAPI endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        unique_id = str(uuid.uuid4())[:8]
        reg_payload = {
            "email": f"tester_{unique_id}@example.com",
            "username": f"user_{unique_id}",
            "password": "SecurePassword123!",
            "full_name": "API Tester",
        }
        res = cls.client.post("/api/auth/register", json=reg_payload)
        token = res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {token}"}

    def test_health_check(self):
        """Verify API health status."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertIn(res.json()["status"], ["healthy", "ok", "degraded"])

    def test_ml_models_endpoint(self):
        """Verify GET /api/ml/models returns production model information."""
        res = self.client.get("/api/ml/models", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("production_model", data)
        self.assertIn("pipeline_version", data)

    def test_ml_experiments_endpoint(self):
        """Verify GET /api/ml/experiments returns benchmark logs."""
        res = self.client.get("/api/ml/experiments", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("experiments", data)
        self.assertGreater(len(data["experiments"]), 0)

    def test_certificates_list_empty_or_valid(self):
        """Verify GET /api/certificates returns user certificates."""
        res = self.client.get("/api/certificates", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_nonexistent_certificate_404(self):
        """Verify proper error handling for invalid certificate IDs."""
        bad_id = str(uuid.uuid4())
        for path in ["", "/extraction", "/explanation", "/ocr"]:
            res = self.client.get(f"/api/certificates/{bad_id}{path}", headers=self.headers)
            self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
