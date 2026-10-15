"""
CertiNexus AI — Patram-Bench Indian Document Understanding Adapter
Official Source: https://patrambench.github.io/
Indian document layout analysis, table parsing, and structured entity extraction.
"""

from typing import Any, Dict, Iterator, Optional

from .base import BaseDatasetAdapter, DatasetMetadata, DatasetSample


class PatramBenchAdapter(BaseDatasetAdapter):
    """Adapter for Patram-Bench Indian Document Understanding benchmark."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir=cache_dir)
        self.metadata = DatasetMetadata(
            name="Patram-Bench",
            source_url="https://patrambench.github.io/",
            license_id="CC-BY-NC-SA-4.0",
            version="v1.0",
            tasks=["document_type", "layout_analysis", "field_extraction"],
            languages=["en", "hi", "indic"],
            supports_streaming=True,
            auth_required=False,
            estimated_size_mb=850.0,
            storage_type="stream",
            description="Benchmark for Indian document understanding, complex layouts, stamps, signatures, and government tables.",
            notes="Evaluates document layout hierarchy and table extraction for administrative records.",
        )

    def get_metadata(self) -> DatasetMetadata:
        return self.metadata

    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream normalized samples for Indian layout understanding."""
        mock_samples = [
            DatasetSample(
                sample_id="patram_sample_001",
                source_dataset="Patram-Bench",
                source_revision="v1.0",
                task="document_type",
                document_type="government_certificate",
                language="en",
                ground_truth_text="GOVERNMENT OF MAHARASHTRA REVENUE DEPARTMENT CASTE CERTIFICATE No: 2023/REV/98124 This is to certify that...",
                ground_truth_fields={
                    "issuer": "Government of Maharashtra",
                    "department": "Revenue Department",
                    "doc_category": "Caste / Community Certificate",
                },
                layout_annotations=[
                    {"label": "header", "bbox": [50, 40, 500, 90]},
                    {"label": "emblem", "bbox": [250, 95, 300, 140]},
                    {"label": "body_text", "bbox": [50, 150, 500, 400]},
                    {"label": "signature", "bbox": [380, 420, 480, 480]},
                ],
                license_id=self.metadata.license_id,
                synthetic=True,
            ),
            DatasetSample(
                sample_id="patram_sample_002",
                source_dataset="Patram-Bench",
                source_revision="v1.0",
                task="document_type",
                document_type="academic_marksheet",
                language="en",
                ground_truth_text="CENTRAL BOARD OF SECONDARY EDUCATION GRADE SHEET CUM CERTIFICATE OF PERFORMANCE Roll No: 4120984 Candidate: RAHUL VERMA",
                ground_truth_fields={
                    "authority": "Central Board of Secondary Education",
                    "doc_category": "Marksheet",
                },
                layout_annotations=[
                    {"label": "table_header", "bbox": [60, 200, 480, 240]},
                    {"label": "grades_table", "bbox": [60, 240, 480, 450]},
                ],
                license_id=self.metadata.license_id,
                synthetic=True,
            ),
        ]
        for idx, s in enumerate(mock_samples):
            if limit is not None and idx >= limit:
                break
            yield s
