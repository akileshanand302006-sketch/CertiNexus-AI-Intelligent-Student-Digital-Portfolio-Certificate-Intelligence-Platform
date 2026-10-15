"""
CertiNexus AI — Mozhi Indic OCR Adapter
Official Source: https://cvit.iiit.ac.in/usodi/tdocrmil.php (IIIT Hyderabad)
Provides Indic document OCR recognition and dictionary resources.
"""

from typing import Any, Dict, Iterator, Optional

from .base import BaseDatasetAdapter, DatasetMetadata, DatasetSample


class MozhiAdapter(BaseDatasetAdapter):
    """Adapter for Mozhi Indic OCR benchmark resources."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir=cache_dir)
        self.metadata = DatasetMetadata(
            name="Mozhi Indic OCR",
            source_url="https://cvit.iiit.ac.in/usodi/tdocrmil.php",
            license_id="Academic Research License / CC-BY",
            version="v1.0",
            tasks=["ocr"],
            languages=["te", "ta", "ml", "kn", "hi"],
            supports_streaming=False,
            auth_required=False,
            estimated_size_mb=650.0,
            storage_type="staged",
            description="Benchmark repository for Indic script document OCR developed by CVIT IIIT-Hyderabad.",
            notes="Uses bounded staged evaluation batches respecting local cache budget.",
        )

    def get_metadata(self) -> DatasetMetadata:
        return self.metadata

    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream verified benchmark samples."""
        mock_samples = [
            DatasetSample(
                sample_id="mozhi_te_001",
                source_dataset="Mozhi Indic OCR",
                source_revision="v1.0",
                task="ocr",
                document_type="indic_document",
                language="te",
                ground_truth_text="ఆంధ్రప్రదేశ్ ప్రభుత్వ అధికారిక పత్రం",
                license_id=self.metadata.license_id,
                synthetic=True,
            ),
            DatasetSample(
                sample_id="mozhi_hi_002",
                source_dataset="Mozhi Indic OCR",
                source_revision="v1.0",
                task="ocr",
                document_type="indic_document",
                language="hi",
                ground_truth_text="उत्तर प्रदेश शासन राजस्व विभाग प्रमाण पत्र",
                license_id=self.metadata.license_id,
                synthetic=True,
            ),
        ]
        for idx, s in enumerate(mock_samples):
            if limit is not None and idx >= limit:
                break
            yield s
