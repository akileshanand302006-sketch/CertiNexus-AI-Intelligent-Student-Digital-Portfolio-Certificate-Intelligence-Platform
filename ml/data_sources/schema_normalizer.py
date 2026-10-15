"""
CertiNexus AI — Dataset Schema Normalizer
Transforms raw heterogeneous annotations into canonical versioned schemas.
"""

from typing import Any, Dict, Optional
from .base import DatasetSample


class SchemaNormalizer:
    """Normalizes sample fields across datasets."""

    DOCUMENT_TYPE_ALIASES = {
        "aadhaar": "aadhaar",
        "aadhar": "aadhaar",
        "uidai": "aadhaar",
        "pan": "pan",
        "pancard": "pan",
        "dl": "driving_licence",
        "driving_license": "driving_licence",
        "driving_licence": "driving_licence",
        "rc": "vehicle_rc",
        "registration_certificate": "vehicle_rc",
        "marksheet": "marksheet",
        "grade_sheet": "marksheet",
        "transcript": "transcript",
        "timetable": "timetable",
        "fee_receipt": "fee_receipt",
        "receipt": "fee_receipt",
        "passbook": "passbook",
        "bank_passbook": "passbook",
        "patta": "patta",
        "land_record": "patta",
        "income_certificate": "income_certificate",
        "residence_certificate": "residence_certificate",
        "domicile": "residence_certificate",
        "resume": "resume",
        "cv": "resume",
        "curriculum_vitae": "resume",
        "certificate": "certificate",
    }

    @classmethod
    def canonical_document_type(cls, raw_type: Optional[str]) -> str:
        if not raw_type:
            return "general_document"
        norm = raw_type.lower().strip().replace("-", "_").replace(" ", "_")
        return cls.DOCUMENT_TYPE_ALIASES.get(norm, "general_document")

    @classmethod
    def normalize_sample(cls, sample: DatasetSample) -> DatasetSample:
        """Apply canonical normalization to a dataset sample."""
        sample.document_type = cls.canonical_document_type(sample.document_type)

        if sample.ground_truth_text:
            # Normalize whitespace without altering meaningful content
            sample.ground_truth_text = " ".join(sample.ground_truth_text.split())

        return sample
