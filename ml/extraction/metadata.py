"""
CertiNexus AI — Extraction Metadata

Structured metadata schema for certificate extraction results.
Aggregates NER entities, category fields, duplicate info, and
quality metrics into a single unified result.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .rule_ner import NERResult
from .certificate_fields import CertificateFields
from .duplicate_detector import DuplicateResult


@dataclass
class ExtractionMetadata:
    """
    Unified extraction metadata for a certificate document.

    Combines NER entities, structured fields, duplicate detection,
    and quality metrics.
    """
    document_id: str
    category: str
    confidence: float

    # NER results
    ner_result: Optional[NERResult] = None

    # Structured fields
    fields: Optional[CertificateFields] = None

    # Duplicate detection
    duplicate_result: Optional[DuplicateResult] = None

    # Quality metrics
    ocr_confidence: float = 0.0
    image_quality_score: float = 0.0
    text_quality_score: float = 0.0
    extraction_completeness: float = 0.0

    # Processing info
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "document_id": self.document_id,
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "entities": self.ner_result.to_dict() if self.ner_result else {},
            "fields": self.fields.to_dict() if self.fields else {},
            "duplicate": (
                self.duplicate_result.to_dict()
                if self.duplicate_result else {}
            ),
            "quality": {
                "ocr_confidence": round(self.ocr_confidence, 2),
                "image_quality": round(self.image_quality_score, 1),
                "text_quality": round(self.text_quality_score, 1),
                "extraction_completeness": round(
                    self.extraction_completeness, 1
                ),
            },
            "processing_time_ms": round(self.processing_time_ms, 2),
        }
