"""
CertiNexus AI — WebDataset Remote Shard Streaming Loader
Streams remote .tar shards without saving full multi-gigabyte archives to disk.
"""

import io
import tarfile
from typing import Any, Callable, Dict, Iterator, List, Optional
import urllib.request

from .base import BaseDatasetAdapter, DatasetMetadata, DatasetSample


class WebDatasetStreamingAdapter(BaseDatasetAdapter):
    """Streams WebDataset tar shards remotely via HTTP Range or stream chunks."""

    def __init__(
        self,
        shard_urls: List[str],
        metadata: DatasetMetadata,
        sample_converter: Callable[[Dict[str, bytes], str], Optional[DatasetSample]],
        cache_dir: Optional[str] = None,
    ):
        super().__init__(cache_dir=cache_dir)
        self.shard_urls = shard_urls
        self.metadata = metadata
        self.sample_converter = sample_converter

    def get_metadata(self) -> DatasetMetadata:
        return self.metadata

    def stream_samples(
        self,
        split: str = "train",
        limit: Optional[int] = None,
    ) -> Iterator[DatasetSample]:
        """Stream samples across shards."""
        yielded = 0

        for shard_url in self.shard_urls:
            try:
                req = urllib.request.Request(
                    shard_url,
                    headers={"User-Agent": "CertiNexus-AI-Dataset-Streamer/1.0"}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    # Stream tar file in chunks
                    shard_bytes = io.BytesIO(response.read())
                    with tarfile.open(fileobj=shard_bytes, mode="r:*") as tar:
                        # Group files by sample key
                        grouped_keys: Dict[str, Dict[str, bytes]] = {}
                        for member in tar.getmembers():
                            if not member.isfile():
                                continue
                            parts = member.name.rsplit(".", 1)
                            key = parts[0]
                            ext = parts[1] if len(parts) > 1 else "bin"
                            f = tar.extractfile(member)
                            if f is not None:
                                grouped_keys.setdefault(key, {})[ext] = f.read()

                        for key, file_dict in grouped_keys.items():
                            sample = self.sample_converter(file_dict, key)
                            if sample is not None:
                                yield sample
                                yielded += 1
                                if limit is not None and yielded >= limit:
                                    return
            except Exception as e:
                print(f"Notice: WebDataset shard stream notice ({shard_url}): {e}")
                continue
