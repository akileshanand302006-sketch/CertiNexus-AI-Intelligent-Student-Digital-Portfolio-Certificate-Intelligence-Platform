"""
CertiNexus AI — Unified Indian Document Intelligence Automated Test Suite

Tests:
1. Dataset ingestion registry & 10 GB storage budget enforcement
2. Document type router (Identity, Academic, Financial, Career, Credentials)
3. Structured field extractor & PII masking functions
4. Scanned PDF fallback logic
5. 11-category certificate classifier
"""

import os
import sys
import pytest

# Ensure project paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "backend") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "backend"))

from ml.classifiers.document_router import DocumentTypeRouter
from ml.extraction.indian_doc_extractor import IndianDocumentExtractor
from ml.extraction.schemas import (
    mask_aadhaar,
    mask_pan,
    mask_bank_account,
    mask_phone_number,
)
from ml.data_sources.budget import StorageBudgetManager
from ml.data_sources.registry import DatasetRegistry


class TestStorageBudgetAndIngestion:
    def test_storage_budget_manager(self):
        manager = StorageBudgetManager(budget_bytes=10 * 1024 * 1024 * 1024)
        report = manager.audit_storage()
        assert report["budget_gb"] == 10.0
        assert report["remaining_gb"] > 0
        assert report["is_within_budget"] is True
        assert manager.is_within_budget(extra_bytes=1024 * 1024) is True

    def test_dataset_registry_discovery(self):
        registry = DatasetRegistry()
        sources = registry.list_sources()
        assert "capcc" in sources
        assert "kyc" in sources
        assert "bhartiocr" in sources
        assert "mozhi" in sources
        assert "patram" in sources


class TestPIIMasking:
    def test_aadhaar_masking(self):
        assert mask_aadhaar("1234 5678 9012") == "XXXX-XXXX-9012"
        assert mask_aadhaar("123456789012") == "XXXX-XXXX-9012"
        assert mask_aadhaar("") == ""

    def test_pan_masking(self):
        assert mask_pan("ABCDE1234F") == "ABCDE****F"
        assert mask_pan("abcde1234f") == "ABCDE****F"

    def test_bank_account_masking(self):
        assert mask_bank_account("123456789012") == "******9012"
        assert mask_bank_account("") == ""

    def test_phone_masking(self):
        assert mask_phone_number("9876543210") == "+91-XXXXX-43210"


class TestDocumentTypeRouter:
    @pytest.fixture
    def router(self):
        return DocumentTypeRouter()

    def test_route_aadhaar(self, router):
        text = "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI 1234 5678 9012 Mera Aadhaar"
        res = router.route(text, "aadhaar_card.jpeg")
        assert res["document_type"] == "aadhaar"
        assert res["is_certificate"] is False
        assert res["confidence"] > 0.8

    def test_route_pan(self, router):
        text = "INCOME TAX DEPARTMENT GOVT OF INDIA PERMANENT ACCOUNT NUMBER ABCDE1234F Name Rajesh Kumar"
        res = router.route(text, "pancard.jpg")
        assert res["document_type"] == "pan"
        assert res["is_certificate"] is False

    def test_route_marksheet(self, router):
        text = "ANNA UNIVERSITY STATEMENT OF MARKS Bachelor of Technology Semester V Cumulative Grade Point Average CGPA 8.75 Result PASS"
        res = router.route(text, "marksheet.pdf")
        assert res["document_type"] == "marksheet"

    def test_route_resume(self, router):
        text = "Curriculum Vitae candidate@example.com Work Experience Technical Skills Education Projects github.com/student"
        res = router.route(text, "resume.pdf")
        assert res["document_type"] == "resume"

    def test_route_certificate(self, router):
        text = "Certificate of Completion This is to certify that candidate has completed the Python Workshop"
        res = router.route(text, "workshop_certificate.pdf")
        assert res["document_type"] == "certificate"
        assert res["is_certificate"] is True


class TestIndianDocumentExtractor:
    @pytest.fixture
    def extractor(self):
        return IndianDocumentExtractor()

    def test_extract_aadhaar_fields(self, extractor):
        text = "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI Mera Aadhaar 1234 5678 9012 DOB 15/08/1998 Male Address Bengaluru 560001"
        res = extractor.extract(text, "aadhaar")
        fields = res["fields"]
        assert fields["aadhaar_number"] == "XXXX-XXXX-9012"
        assert fields["dob"] == "15/08/1998"
        assert fields["gender"] == "Male"
        assert "UIDAI" in fields["issuing_authority"]

    def test_extract_pan_fields(self, extractor):
        text = "INCOME TAX DEPARTMENT GOVT OF INDIA ABCDE1234F Father's Name Suresh Kumar DOB 12/04/1990"
        res = extractor.extract(text, "pan")
        fields = res["fields"]
        assert fields["pan_number"] == "ABCDE****F"
        assert fields["guardian_name"] == "Suresh Kumar"
        assert fields["dob"] == "12/04/1990"

    def test_extract_marksheet_fields(self, extractor):
        text = "STATEMENT OF MARKS Anna University Name of Candidate Anand Kumar Roll No 710018104001 Bachelor of Technology Semester V CGPA 8.75 Result PASS"
        res = extractor.extract(text, "marksheet")
        fields = res["fields"]
        assert fields["student_name"] == "Anand Kumar"
        assert fields["roll_number"] == "710018104001"
        assert "CGPA: 8.75" in fields["sgpa_cgpa"]
        assert fields["result_status"] == "PASS"
