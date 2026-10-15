"""
CertiNexus AI — Integration Tests for Intelligence API Endpoints
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


class TestAPIIntelligenceEndpoints(unittest.TestCase):
    """Test new intelligence endpoints on FastAPI backend."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        unique_id = str(uuid.uuid4())[:8]
        reg_payload = {
            "email": f"test_intel_{unique_id}@example.com",
            "username": f"intel_user_{unique_id}",
            "password": "Password123!",
            "full_name": "Intelligence Tester",
        }
        res = cls.client.post("/api/auth/register", json=reg_payload)
        token = res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {token}"}

    def test_health_check(self):
        """Verify API is healthy."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)

    def test_admin_models_endpoint(self):
        """Verify GET /api/admin/models returns metadata and classes."""
        res = self.client.get("/api/admin/models", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("production_model", data)
        self.assertIn("supported_categories", data)

    def test_certificate_not_found_handling(self):
        """Verify appropriate 404 response on nonexistent certificate endpoints."""
        fake_id = str(uuid.uuid4())
        res = self.client.get(f"/api/certificates/{fake_id}/extraction", headers=self.headers)
        self.assertEqual(res.status_code, 404)

        res = self.client.get(f"/api/certificates/{fake_id}/explanation", headers=self.headers)
        self.assertEqual(res.status_code, 404)

        res = self.client.get(f"/api/certificates/{fake_id}/ocr", headers=self.headers)
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
