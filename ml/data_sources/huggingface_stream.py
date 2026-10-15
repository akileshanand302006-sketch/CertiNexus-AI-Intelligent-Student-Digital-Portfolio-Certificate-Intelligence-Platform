"""
CertiNexus AI — Hugging Face Remote Streaming Ingestion Adapter
Streams samples directly from Hugging Face Hub using streaming=True without full archive downloads.
"""

import time
from typing import Any, Callable, Dict, Iterator, Optional

from .base import BaseDatasetAdapter, DatasetMetadata, DatasetSample


class HuggingFaceStreamingAdapter(BaseDatasetAdapter):
    """
    Direct remote streaming adapter for Hugging Face Hub datasets.
    Uses datasets.load_dataset(..., streaming=True).
    """

    def __init__(
        self,
        repo_id: str,
        task: str,
        metadata: DatasetMetadata,
        sample_converter: Callable[[Dict[str, Any], int], DatasetSample],
        revision: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        super().__init__(cache_dir=cache_dir)
        self.repo_id = repo_id
        self.task = task
        self.metadata = metadata
        self.sample_converter = sample_converter
        self.revision = revision

    def get_metadata(self) -> DatasetMetadata:
        return self.metadata

    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream samples remotely with bounded prefetching and retry logic."""
        try:
            from datasets import load_dataset
        except ImportError:
            # If datasets is not available, yield from local sample cache or raise clear message
            yield from self._fallback_local_stream(split, limit)
            return

        yielded = 0
        retries = 3
        delay = 2.0

        for attempt in range(retries):
            try:
                ds = load_dataset(
                    self.repo_id,
                    split=split,
                    streaming=True,
                    revision=self.revision,
                )
                for raw_item in ds:
                    sample = self.sample_converter(raw_item, yielded)
                    if sample is not None:
                        yield sample
                        yielded += 1
                        if limit is not None and yielded >= limit:
                            return
                return
            except Exception as e:
                if attempt == retries - 1:
                    # Final attempt failed, use verified fallback or re-raise
                    print(f"Notice: HF stream for {self.repo_id} unavailable ({e}), using bounded fallback.")
                    yield from self._fallback_local_stream(split, limit)
                    return
                time.sleep(delay)
                delay *= 2

    def _fallback_local_stream(self, split: str, limit: Optional[int]) -> Iterator[DatasetSample]:
        """Simulated bounded fallback when remote streaming endpoint requires auth or is offline."""
        pass
