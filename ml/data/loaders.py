"""
CertiNexus AI — Dataset Loaders

Load and inspect CAPCC-v1 (primary) and RVL-CDIP (supplementary) datasets.
Provides structured DatasetInfo for downstream validation.
"""

import os
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List

import pandas as pd
import numpy as np


@dataclass
class DatasetInfo:
    """Structured dataset metadata for validation and reporting."""
    name: str
    path: str
    num_samples: int
    num_classes: int
    class_names: List[str]
    class_distribution: Dict[str, int]
    columns: List[str]
    sha256_hash: str
    text_column: str
    label_column: str
    has_missing_text: bool = False
    has_missing_labels: bool = False
    num_missing_text: int = 0
    num_missing_labels: int = 0
    avg_text_length: float = 0.0
    min_text_length: int = 0
    max_text_length: int = 0
    extra: Dict = field(default_factory=dict)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Dataset: {self.name}",
            f"  Path: {self.path}",
            f"  Samples: {self.num_samples}",
            f"  Classes: {self.num_classes} — {self.class_names}",
            f"  Columns: {self.columns}",
            f"  SHA-256: {self.sha256_hash[:16]}...",
            f"  Text column: \'{self.text_column}\' "
            f"(missing: {self.num_missing_text})",
            f"  Label column: \'{self.label_column}\' "
            f"(missing: {self.num_missing_labels})",
            f"  Text length — avg: {self.avg_text_length:.1f}, "
            f"min: {self.min_text_length}, max: {self.max_text_length}",
            f"  Class distribution:",
        ]
        for cls_name, count in sorted(
            self.class_distribution.items(), key=lambda x: -x[1]
        ):
            pct = count / self.num_samples * 100
            lines.append(f"    {cls_name}: {count} ({pct:.1f}%)")
        return "\n".join(lines)


def _file_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_capcc_v1(
    base_dir: Optional[str] = None,
    text_column: str = "clean_text",
    label_column: str = "category",
) -> Tuple[pd.DataFrame, DatasetInfo]:
    """
    Load the CAPCC-v1 (Certificate & Achievement Portfolio Classification
    Corpus) primary dataset.

    Parameters
    ----------
    base_dir : str, optional
        Project root directory. Auto-detected if None.
    text_column : str
        Column containing preprocessed text.
    label_column : str
        Column containing category labels.

    Returns
    -------
    df : pd.DataFrame
        The loaded dataset.
    info : DatasetInfo
        Structured metadata about the dataset.
    """
    if base_dir is None:
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    dataset_path = os.path.join(
        base_dir, "dataset", "processed", "cleaned_dataset.csv"
    )
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"CAPCC-v1 dataset not found at {dataset_path}"
        )

    df = pd.read_csv(dataset_path)

    # Compute text stats
    text_lengths = df[text_column].fillna("").str.len()
    missing_text = df[text_column].isna().sum()
    missing_labels = df[label_column].isna().sum()
    class_dist = df[label_column].value_counts().to_dict()

    info = DatasetInfo(
        name="CAPCC-v1",
        path=dataset_path,
        num_samples=len(df),
        num_classes=df[label_column].nunique(),
        class_names=sorted(df[label_column].unique().tolist()),
        class_distribution=class_dist,
        columns=list(df.columns),
        sha256_hash=_file_sha256(dataset_path),
        text_column=text_column,
        label_column=label_column,
        has_missing_text=missing_text > 0,
        has_missing_labels=missing_labels > 0,
        num_missing_text=int(missing_text),
        num_missing_labels=int(missing_labels),
        avg_text_length=float(text_lengths.mean()),
        min_text_length=int(text_lengths.min()),
        max_text_length=int(text_lengths.max()),
    )

    return df, info


def load_rvl_cdip(
    base_dir: Optional[str] = None,
    split: str = "train",
    max_samples: Optional[int] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[DatasetInfo]]:
    """
    Load the RVL-CDIP supplementary dataset (parquet format).

    This is a large document classification dataset used for supplementary
    evaluation. Returns None if the dataset is not available locally.

    Parameters
    ----------
    base_dir : str, optional
        Project root directory. Auto-detected if None.
    split : str
        \'train\' or \'test\'.
    max_samples : int, optional
        Limit number of samples loaded (for memory efficiency).

    Returns
    -------
    df : pd.DataFrame or None
        The loaded dataset, or None if not available.
    info : DatasetInfo or None
        Structured metadata, or None if not available.
    """
    if base_dir is None:
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    data_dir = os.path.join(
        base_dir, "dataset", "public", "rvl-cdip", "data"
    )
    if not os.path.exists(data_dir):
        return None, None

    # Find parquet files for the given split
    parquet_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.endswith(".parquet") and split in f
    ]

    if not parquet_files:
        return None, None

    try:
        dfs = []
        for pf in sorted(parquet_files):
            chunk = pd.read_parquet(pf)
            dfs.append(chunk)
            if max_samples and sum(len(d) for d in dfs) >= max_samples:
                break

        df = pd.concat(dfs, ignore_index=True)
        if max_samples:
            df = df.head(max_samples)

        label_col = "label" if "label" in df.columns else df.columns[-1]
        text_col = "text" if "text" in df.columns else None

        if text_col is None and "image" in df.columns:
            text_col = "image"

        class_dist = df[label_col].value_counts().to_dict()

        info = DatasetInfo(
            name=f"RVL-CDIP ({split})",
            path=data_dir,
            num_samples=len(df),
            num_classes=df[label_col].nunique(),
            class_names=sorted(
                [str(c) for c in df[label_col].unique().tolist()]
            ),
            class_distribution={str(k): v for k, v in class_dist.items()},
            columns=list(df.columns),
            sha256_hash="parquet-multi-file",
            text_column=text_col or "",
            label_column=label_col,
            extra={"split": split, "num_files": len(parquet_files)},
        )

        return df, info

    except Exception as e:
        print(f"Warning: Could not load RVL-CDIP ({split}): {e}")
        return None, None


if __name__ == "__main__":
    print("=" * 60)
    print("CertiNexus AI — Dataset Loader Test")
    print("=" * 60)

    df, info = load_capcc_v1()
    print(info.summary())
    sample = df["clean_text"].iloc[0][:100]
    print(f"First sample text (truncated): {sample}...")

    print()
    print("=" * 60)
    rvl_df, rvl_info = load_rvl_cdip(max_samples=100)
    if rvl_info:
        print(rvl_info.summary())
    else:
        print("RVL-CDIP dataset not available locally (optional).")
