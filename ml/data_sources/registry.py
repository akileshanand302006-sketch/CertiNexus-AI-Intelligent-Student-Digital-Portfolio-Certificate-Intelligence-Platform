"""
CertiNexus AI — Dataset Source Registry
Central registry providing plug-and-play access to all supported and streaming datasets.
"""

from typing import Dict, List, Optional, Type

from .base import BaseDatasetAdapter
from .bhartiocr_adapter import BhartiOCRAdapter
from .capcc_adapter import CAPCCAdapter
from .kyc_adapter import IndianKYCAdapter
from .mozhi_adapter import MozhiAdapter
from .patram_adapter import PatramBenchAdapter


class DatasetRegistry:
    """Registry of dataset streaming adapters."""

    _REGISTRY: Dict[str, Type[BaseDatasetAdapter]] = {
        "kyc": IndianKYCAdapter,
        "bhartiocr": BhartiOCRAdapter,
        "patram": PatramBenchAdapter,
        "mozhi": MozhiAdapter,
        "capcc": CAPCCAdapter,
    }

    @classmethod
    def list_sources(cls) -> List[str]:
        """List registered source identifiers."""
        return list(cls._REGISTRY.keys())

    @classmethod
    def get_adapter(cls, name: str, **kwargs) -> BaseDatasetAdapter:
        """Instantiate an adapter by name."""
        name_clean = name.lower().strip()
        if name_clean not in cls._REGISTRY:
            raise KeyError(
                f"Dataset source '{name}' not found. Available sources: {cls.list_sources()}"
            )
        return cls._REGISTRY[name_clean](**kwargs)

    @classmethod
    def get_all_adapters(cls, **kwargs) -> List[BaseDatasetAdapter]:
        """Instantiate all registered adapters."""
        return [cls.get_adapter(name, **kwargs) for name in cls._REGISTRY]
