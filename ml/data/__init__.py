"""
CertiNexus AI — Data Pipeline Module

Provides dataset loading, validation, splitting, and integrity checks.
"""
from .loaders import load_capcc_v1, load_rvl_cdip, DatasetInfo
from .validation import DatasetValidator, ValidationReport
from .splits import create_stratified_splits, SplitResult
