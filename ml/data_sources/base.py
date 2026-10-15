"""
CertiNexus AI — Base Dataset Ingestion Classes & Normalized Schema
Provides typed data structures and abstract adapter interfaces for direct dataset streaming.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class DatasetMetadata:
    """Metadata describing a dataset source."""
    name: str
    source_url: str
    license_id: str
    version: str = "1.0"
    tasks: List[str] = field(default_factory=list)  # e.g., ["ocr", "kyc_extraction", "classification"]
    languages: List[str] = field(default_factory=lambda: ["en"])
    supports_streaming: bool = True
    auth_required: bool = False
    estimated_size_mb: float = 0.0
    storage_type: str = "stream"  # "stream" | "staged" | "local"
    description: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source_url": self.source_url,
            "license_id": self.license_id,
            "version": self.version,
            "tasks": self.tasks,
            "languages": self.languages,
            "supports_streaming": self.supports_streaming,
            "auth_required": self.auth_required,
            "estimated_size_mb": self.estimated_size_mb,
            "storage_type": self.storage_type,
            "description": self.description,
            "notes": self.notes,
        }


@dataclass
class DatasetSample:
    """Canonical normalized sample across all ingestion sources."""
    sample_id: str
    source_dataset: str
    source_revision: str
    task: str  # "ocr" | "document_type" | "field_extraction" | "certificate_classification"
    document_type: Optional[str] = None  # e.g. "aadhaar", "pan", "marksheet", "resume", "certificate"
    certificate_category: Optional[str] = None  # For 11-class certs
    language: Optional[str] = "en"
    image_bytes: Optional[bytes] = None
    image_path: Optional[str] = None
    ground_truth_text: Optional[str] = None
    ground_truth_fields: Optional[Dict[str, Any]] = None
    layout_annotations: Optional[List[Dict[str, Any]]] = None
    split_group: Optional[str] = "train"  # "train" | "val" | "test"
    license_id: str = "unknown"
    synthetic: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_image_bytes: bool = False) -> Dict[str, Any]:
        res = {
            "sample_id": self.sample_id,
            "source_dataset": self.source_dataset,
            "source_revision": self.source_revision,
            "task": self.task,
            "document_type": self.document_type,
            "certificate_category": self.certificate_category,
            "language": self.language,
            "image_path": self.image_path,
            "ground_truth_text": self.ground_truth_text,
            "ground_truth_fields": self.ground_truth_fields,
            "layout_annotations": self.layout_annotations,
            "split_group": self.split_group,
            "license_id": self.license_id,
            "synthetic": self.synthetic,
            "metadata": self.metadata,
        }
        if include_image_bytes and self.image_bytes is not None:
            res["image_bytes_length"] = len(self.image_bytes)
        return res


class BaseDatasetAdapter(ABC):
    """Abstract base adapter for datasets."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir

    @abstractmethod
    def get_metadata(self) -> DatasetMetadata:
        """Return dataset metadata."""
        pass

    @abstractmethod
    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream normalized samples without exhausting memory."""
        pass

    def get_sample_count(self, split: str = "train") -> Optional[int]:
        """Return sample count if known without exhausting remote stream."""
        return None

    def validate(self, num_samples: int = 5) -> Dict[str, Any]:
        """Quick self-test of the adapter."""
        samples_yielded = 0
        errors = []
        try:
            for s in self.stream_samples(limit=num_samples):
                samples_yielded += 1
                if not s.sample_id:
                    errors.append("Sample missing sample_id")
                if not s.source_dataset:
                    errors.append("Sample missing source_dataset")
        except Exception as e:
            errors.append(f"Streaming error: {str(e)}")

        return {
            "dataset": self.get_metadata().name,
            "success": len(errors) == 0 and samples_yielded > 0,
            "samples_checked": samples_yielded,
            "errors": errors,
        }
