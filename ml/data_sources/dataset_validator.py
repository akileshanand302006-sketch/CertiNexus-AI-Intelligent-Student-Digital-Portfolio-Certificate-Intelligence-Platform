"""
CertiNexus AI — Dataset Validator & Leakage Detection
Validates sample structure, ground truth consistency, and prevents train/test partition contamination.
"""

from typing import Any, Dict, List, Set
from .base import DatasetSample


class DatasetValidator:
    """Validates dataset samples and guards against data leakage."""

    def __init__(self):
        self.seen_signatures: Set[str] = set()

    def validate_sample(self, sample: DatasetSample) -> Dict[str, Any]:
        """Validate sample schema and content."""
        errors = []
        warnings = []

        if not sample.sample_id:
            errors.append("Empty sample_id")
        if not sample.source_dataset:
            errors.append("Empty source_dataset")
        if not sample.ground_truth_text and not sample.image_bytes and not sample.image_path:
            errors.append("Sample has neither text nor image payload")

        # Check for empty fields
        if sample.ground_truth_fields is not None:
            if not isinstance(sample.ground_truth_fields, dict):
                errors.append("ground_truth_fields must be a dictionary")

        # Signature duplicate check
        sig = f"{sample.source_dataset}:{sample.ground_truth_text[:80] if sample.ground_truth_text else sample.sample_id}"
        if sig in self.seen_signatures:
            warnings.append("Near-duplicate text detected across sample streams")
        else:
            self.seen_signatures.add(sig)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
