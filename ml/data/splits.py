"""
CertiNexus AI — Stratified Data Splitting

Provides reproducible stratified train/validation/test splits
with leakage prevention checks.
"""

import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


@dataclass
class SplitResult:
    """Result of a stratified split operation."""
    X_train: np.ndarray
    X_val: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_val: np.ndarray
    y_test: np.ndarray
    label_encoder: LabelEncoder
    train_indices: np.ndarray
    val_indices: np.ndarray
    test_indices: np.ndarray
    split_config: Dict = field(default_factory=dict)

    def summary(self) -> str:
        classes = list(self.label_encoder.classes_)
        lines = [
            "Split Summary:",
            f"  Train: {len(self.X_train)} samples",
            f"  Validation: {len(self.X_val)} samples",
            f"  Test: {len(self.X_test)} samples",
            f"  Classes: {len(classes)}",
            f"  Random seed: {self.split_config.get('random_seed', '?')}",
        ]
        # Per-class counts in train
        lines.append("  Train class distribution:")
        for i, cls_name in enumerate(classes):
            count = (self.y_train == i).sum()
            lines.append(f"    {cls_name}: {count}")
        return "\n".join(lines)


def create_stratified_splits(
    df: pd.DataFrame,
    text_column: str = "clean_text",
    label_column: str = "category",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_seed: int = 42,
) -> SplitResult:
    """
    Create reproducible stratified train/validation/test splits.

    Uses two-stage stratified splitting:
    1. Separate test set (test_size % of total)
    2. Split remaining into train and validation

    Parameters
    ----------
    df : pd.DataFrame
        The dataset.
    text_column : str
        Column containing text features.
    label_column : str
        Column containing category labels.
    test_size : float
        Fraction of data for test set (0.15 = 15%).
    val_size : float
        Fraction of data for validation set (0.15 = 15%).
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    result : SplitResult
        Contains all splits, label encoder, and metadata.
    """
    X = df[text_column].values
    y = df[label_column].values
    indices = np.arange(len(df))

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Stage 1: Separate test set
    X_temp, X_test, y_temp, y_test, idx_temp, idx_test = train_test_split(
        X, y_encoded, indices,
        test_size=test_size,
        stratify=y_encoded,
        random_state=random_seed,
    )

    # Stage 2: Split remaining into train and validation
    val_fraction = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val, idx_train, idx_val = train_test_split(
        X_temp, y_temp, idx_temp,
        test_size=val_fraction,
        stratify=y_temp,
        random_state=random_seed,
    )

    # Verify no leakage
    train_set = set(idx_train)
    val_set = set(idx_val)
    test_set = set(idx_test)
    assert len(train_set & val_set) == 0, "Train-Val index overlap!"
    assert len(train_set & test_set) == 0, "Train-Test index overlap!"
    assert len(val_set & test_set) == 0, "Val-Test index overlap!"

    total = len(X_train) + len(X_val) + len(X_test)
    assert total == len(df), f"Split sizes don't sum to total: {total} != {len(df)}"

    result = SplitResult(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
        label_encoder=le,
        train_indices=idx_train,
        val_indices=idx_val,
        test_indices=idx_test,
        split_config={
            "test_size": test_size,
            "val_size": val_size,
            "random_seed": random_seed,
            "text_column": text_column,
            "label_column": label_column,
            "total_samples": len(df),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
        },
    )

    return result


if __name__ == "__main__":
    from .loaders import load_capcc_v1

    df, info = load_capcc_v1()
    result = create_stratified_splits(df)
    print(result.summary())
