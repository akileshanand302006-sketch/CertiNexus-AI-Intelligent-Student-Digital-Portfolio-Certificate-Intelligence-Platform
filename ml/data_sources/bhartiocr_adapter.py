"""
CertiNexus AI — BhartiOCR Indic OCR Streaming Adapter
Candidate Source: https://huggingface.co/datasets/Faizaniqbal/BhartiOCR
Provides Indic-script OCR recognition streaming (Hindi, Tamil, Devanagari, English).
"""

from typing import Any, Dict, Iterator, Optional

from .base import DatasetMetadata, DatasetSample
from .huggingface_stream import HuggingFaceStreamingAdapter


class BhartiOCRAdapter(HuggingFaceStreamingAdapter):
    """Adapter for BhartiOCR Indic OCR dataset."""

    REPO_ID = "Faizaniqbal/BhartiOCR"

    def __init__(self, cache_dir: Optional[str] = None):
        meta = DatasetMetadata(
            name="BhartiOCR",
            source_url="https://huggingface.co/datasets/Faizaniqbal/BhartiOCR",
            license_id="CC-BY-4.0",
            version="v1.0",
            tasks=["ocr"],
            languages=["hi", "en", "ta", "te", "bn"],
            supports_streaming=True,
            auth_required=False,
            estimated_size_mb=3200.0,
            storage_type="stream",
            description="Large-scale Indic script OCR document and text-line dataset covering official Indian languages.",
            notes="Streams remote shards in bounded iterations without full local staging.",
        )
        super().__init__(
            repo_id=self.REPO_ID,
            task="ocr",
            metadata=meta,
            sample_converter=self._convert_sample,
            cache_dir=cache_dir,
        )

    def _convert_sample(self, raw_item: Dict[str, Any], index: int) -> DatasetSample:
        """Parse BhartiOCR sample into canonical DatasetSample."""
        sample_id = raw_item.get("id", f"bharti_ocr_{index}")
        text = raw_item.get("text", raw_item.get("label", ""))

        image = raw_item.get("image")
        image_bytes = None
        if hasattr(image, "tobytes"):
            import io
            buf = io.BytesIO()
            try:
                image.save(buf, format="PNG")
                image_bytes = buf.getvalue()
            except Exception:
                pass

        return DatasetSample(
            sample_id=str(sample_id),
            source_dataset=self.metadata.name,
            source_revision="main",
            task="ocr",
            document_type="indic_document",
            language=raw_item.get("language", "hi"),
            image_bytes=image_bytes,
            ground_truth_text=str(text).strip(),
            license_id=self.metadata.license_id,
            synthetic=False,
        )

    def _fallback_local_stream(self, split: str, limit: Optional[int]) -> Iterator[DatasetSample]:
        """Bounded mock Indic samples for offline evaluation."""
        mock_items = [
            ("bharti_mock_001", "भारत गणराज्य पहचान पत्र", "hi"),
            ("bharti_mock_002", "தமிழ்நாடு அரசு வருவாய்த் துறை சான்றிதழ்", "ta"),
            ("bharti_mock_003", "Government of India Official Document Certification", "en"),
        ]
        for idx, (sid, txt, lang) in enumerate(mock_items):
            if limit is not None and idx >= limit:
                break
            yield DatasetSample(
                sample_id=sid,
                source_dataset=self.metadata.name,
                source_revision="mock-bounded",
                task="ocr",
                document_type="indic_document",
                language=lang,
                ground_truth_text=txt,
                license_id=self.metadata.license_id,
                synthetic=True,
            )
