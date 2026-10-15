"""
CertiNexus AI — CAPCC-v1 Project Dataset Adapter
Source: dataset/raw/certificates.csv & dataset/processed/cleaned_dataset.csv
Contains 606 certificate samples with synthetic/simulated OCR noise across 11 accredited categories.
"""

import csv
import os
from typing import Dict, Iterator, List, Optional

from .base import BaseDatasetAdapter, DatasetMetadata, DatasetSample


class CAPCCAdapter(BaseDatasetAdapter):
    """Adapter for the project CAPCC-v1 certificate dataset."""

    CATEGORIES = [
        "Academic Achievement",
        "Certification",
        "Conference",
        "Cultural Activity",
        "Hackathon",
        "Internship",
        "Seminar",
        "Sports",
        "Technical Competition",
        "Volunteer Activity",
        "Workshop",
    ]

    def __init__(self, csv_path: Optional[str] = None):
        super().__init__()
        if csv_path is None:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            cand1 = os.path.join(root, "dataset", "processed", "cleaned_dataset.csv")
            cand2 = os.path.join(root, "dataset", "raw", "certificates.csv")
            self.csv_path = cand1 if os.path.exists(cand1) else cand2
        else:
            self.csv_path = csv_path

        self.metadata = DatasetMetadata(
            name="CAPCC-v1",
            source_url="project://dataset/raw/certificates.csv",
            license_id="Internal Project / MIT",
            version="v1.0",
            tasks=["certificate_classification", "field_extraction"],
            languages=["en"],
            supports_streaming=True,
            auth_required=False,
            estimated_size_mb=0.68,
            storage_type="local",
            description="Project certificate dataset with 605+ samples across 11 accredited student achievement categories with simulated OCR noise.",
            notes="Evaluated using stratified 70/15/15 split without data leakage across augmentation variants.",
        )

    def get_metadata(self) -> DatasetMetadata:
        return self.metadata

    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream samples from CAPCC-v1 CSV."""
        if not os.path.exists(self.csv_path):
            return

        yielded = 0
        with open(self.csv_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc_id = row.get("document_id") or row.get("id") or f"capcc_{yielded}"
                raw_text = row.get("raw_text") or row.get("text", "")
                category = row.get("category", "").strip()

                if not raw_text or not category:
                    continue

                sample = DatasetSample(
                    sample_id=str(doc_id),
                    source_dataset=self.metadata.name,
                    source_revision=row.get("source", "synthetic_v1"),
                    task="certificate_classification",
                    document_type="certificate",
                    certificate_category=category,
                    language="en",
                    ground_truth_text=raw_text,
                    ground_truth_fields={
                        "title": row.get("certificate_title", ""),
                        "organization": row.get("organization", ""),
                        "event": row.get("event", ""),
                        "date": row.get("date", ""),
                        "category": category,
                    },
                    split_group=split,
                    license_id=self.metadata.license_id,
                    synthetic=True,
                )
                yield sample
                yielded += 1
                if limit is not None and yielded >= limit:
                    break

    def get_sample_count(self, split: str = "train") -> Optional[int]:
        if not os.path.exists(self.csv_path):
            return 0
        with open(self.csv_path, mode="r", encoding="utf-8", errors="replace") as f:
            return max(0, sum(1 for _ in f) - 1)
