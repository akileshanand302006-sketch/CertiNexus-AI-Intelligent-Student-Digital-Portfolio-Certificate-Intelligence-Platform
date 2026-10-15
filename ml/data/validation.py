"""
CertiNexus AI — Dataset Validation

Comprehensive data integrity checks: duplicate detection, label verification,
text quality assessment, and data leakage prevention.
"""

import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

from .loaders import DatasetInfo


@dataclass
class ValidationIssue:
    """A single validation issue found in the dataset."""
    severity: str  # "error", "warning", "info"
    category: str  # "duplicate", "missing", "label", "text_quality", "leakage"
    message: str
    affected_rows: List[int] = field(default_factory=list)
    details: Dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Complete validation report for a dataset."""
    dataset_name: str
    timestamp: str
    num_checks_run: int = 0
    num_errors: int = 0
    num_warnings: int = 0
    num_info: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True
    summary: Dict = field(default_factory=dict)

    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)
        if issue.severity == "error":
            self.num_errors += 1
            self.passed = False
        elif issue.severity == "warning":
            self.num_warnings += 1
        else:
            self.num_info += 1

    def to_dict(self) -> Dict:
        return {
            "dataset_name": self.dataset_name,
            "timestamp": self.timestamp,
            "passed": self.passed,
            "num_checks_run": self.num_checks_run,
            "num_errors": self.num_errors,
            "num_warnings": self.num_warnings,
            "num_info": self.num_info,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "affected_rows_count": len(i.affected_rows),
                    "details": i.details,
                }
                for i in self.issues
            ],
            "summary": self.summary,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def print_report(self):
        print(f"\n{'=' * 60}")
        print(f"VALIDATION REPORT — {self.dataset_name}")
        print(f"{'=' * 60}")
        print(f"  Timestamp: {self.timestamp}")
        print(f"  Checks run: {self.num_checks_run}")
        print(f"  Errors: {self.num_errors}")
        print(f"  Warnings: {self.num_warnings}")
        print(f"  Info: {self.num_info}")
        status = "PASSED" if self.passed else "FAILED"
        print(f"  Status: {status}")

        if self.issues:
            print(f"\n  Issues:")
            for issue in self.issues:
                icon = {
                    "error": "[ERROR]",
                    "warning": "[WARN]",
                    "info": "[INFO]"
                }.get(issue.severity, "[?]")
                rows_info = ""
                if issue.affected_rows:
                    rows_info = (
                        f" (rows: {issue.affected_rows[:5]}"
                        f"{'...' if len(issue.affected_rows) > 5 else ''})"
                    )
                print(f"    {icon} [{issue.category}] "
                      f"{issue.message}{rows_info}")
        print(f"{'=' * 60}")


class DatasetValidator:
    """
    Comprehensive dataset validator for the CertiNexus AI pipeline.

    Runs the following checks:
    1. Missing values detection
    2. Exact text duplicate detection
    3. Near-duplicate detection (text hash-based)
    4. Label consistency verification
    5. Text quality checks (minimum length, suspicious patterns)
    6. Class balance assessment
    7. Data leakage detection between splits
    """

    # Minimum acceptable text length (characters)
    MIN_TEXT_LENGTH = 20

    # Maximum class imbalance ratio (largest / smallest)
    MAX_IMBALANCE_RATIO = 3.0

    # Near-duplicate similarity threshold (Jaccard on word sets)
    NEAR_DUP_THRESHOLD = 0.90

    def __init__(self, text_column: str = "clean_text",
                 label_column: str = "category"):
        self.text_column = text_column
        self.label_column = label_column

    def validate(self, df: pd.DataFrame,
                 dataset_info: Optional[DatasetInfo] = None,
                 dataset_name: str = "unknown") -> ValidationReport:
        """
        Run all validation checks on the dataset.

        Parameters
        ----------
        df : pd.DataFrame
            The dataset to validate.
        dataset_info : DatasetInfo, optional
            Pre-computed dataset info.
        dataset_name : str
            Name for the report.

        Returns
        -------
        report : ValidationReport
        """
        name = dataset_info.name if dataset_info else dataset_name
        report = ValidationReport(
            dataset_name=name,
            timestamp=datetime.now().isoformat(),
        )

        # Run all checks
        self._check_missing_values(df, report)
        self._check_exact_duplicates(df, report)
        self._check_near_duplicates(df, report)
        self._check_label_consistency(df, report)
        self._check_text_quality(df, report)
        self._check_class_balance(df, report)

        # Build summary
        report.summary = {
            "total_samples": len(df),
            "unique_labels": df[self.label_column].nunique(),
            "avg_text_length": float(
                df[self.text_column].fillna("").str.len().mean()
            ),
        }

        return report

    def check_leakage(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        report: Optional[ValidationReport] = None,
    ) -> ValidationReport:
        """
        Check for data leakage between train/val/test splits.

        Parameters
        ----------
        train_df, val_df, test_df : pd.DataFrame
            The three splits.
        report : ValidationReport, optional
            Append to an existing report.

        Returns
        -------
        report : ValidationReport
        """
        if report is None:
            report = ValidationReport(
                dataset_name="leakage_check",
                timestamp=datetime.now().isoformat(),
            )

        report.num_checks_run += 1

        # Check text overlap using normalized hashes
        def text_hashes(df):
            return set(
                hashlib.md5(
                    str(t).strip().lower().encode()
                ).hexdigest()
                for t in df[self.text_column].fillna("")
            )

        train_h = text_hashes(train_df)
        val_h = text_hashes(val_df)
        test_h = text_hashes(test_df)

        tv_overlap = train_h & val_h
        tt_overlap = train_h & test_h
        vt_overlap = val_h & test_h

        if tv_overlap:
            report.add_issue(ValidationIssue(
                severity="error",
                category="leakage",
                message=(
                    f"Train-Validation text overlap: "
                    f"{len(tv_overlap)} identical texts"
                ),
                details={"overlap_count": len(tv_overlap)},
            ))

        if tt_overlap:
            report.add_issue(ValidationIssue(
                severity="error",
                category="leakage",
                message=(
                    f"Train-Test text overlap: "
                    f"{len(tt_overlap)} identical texts"
                ),
                details={"overlap_count": len(tt_overlap)},
            ))

        if vt_overlap:
            report.add_issue(ValidationIssue(
                severity="error",
                category="leakage",
                message=(
                    f"Validation-Test text overlap: "
                    f"{len(vt_overlap)} identical texts"
                ),
                details={"overlap_count": len(vt_overlap)},
            ))

        if not (tv_overlap or tt_overlap or vt_overlap):
            report.add_issue(ValidationIssue(
                severity="info",
                category="leakage",
                message="No data leakage detected between splits",
            ))

        return report

    # ---- Individual check methods ----

    def _check_missing_values(self, df: pd.DataFrame,
                              report: ValidationReport):
        report.num_checks_run += 1
        missing_text = df[self.text_column].isna().sum()
        missing_labels = df[self.label_column].isna().sum()

        if missing_text > 0:
            rows = df[df[self.text_column].isna()].index.tolist()
            report.add_issue(ValidationIssue(
                severity="error",
                category="missing",
                message=f"{missing_text} rows with missing text",
                affected_rows=rows,
            ))

        if missing_labels > 0:
            rows = df[df[self.label_column].isna()].index.tolist()
            report.add_issue(ValidationIssue(
                severity="error",
                category="missing",
                message=f"{missing_labels} rows with missing labels",
                affected_rows=rows,
            ))

        if missing_text == 0 and missing_labels == 0:
            report.add_issue(ValidationIssue(
                severity="info",
                category="missing",
                message="No missing values in text or label columns",
            ))

    def _check_exact_duplicates(self, df: pd.DataFrame,
                                report: ValidationReport):
        report.num_checks_run += 1
        dup_mask = df[self.text_column].duplicated(keep=False)
        num_dups = dup_mask.sum()

        if num_dups > 0:
            dup_rows = df[dup_mask].index.tolist()
            # Find groups
            dup_groups = (
                df[dup_mask]
                .groupby(self.text_column)
                .apply(lambda g: g.index.tolist())
                .tolist()
            )
            report.add_issue(ValidationIssue(
                severity="warning",
                category="duplicate",
                message=(
                    f"{num_dups} rows are exact text duplicates "
                    f"({len(dup_groups)} groups)"
                ),
                affected_rows=dup_rows,
                details={"num_groups": len(dup_groups)},
            ))
        else:
            report.add_issue(ValidationIssue(
                severity="info",
                category="duplicate",
                message="No exact text duplicates found",
            ))

    def _check_near_duplicates(self, df: pd.DataFrame,
                               report: ValidationReport):
        """Check for near-duplicate texts using word-set Jaccard similarity."""
        report.num_checks_run += 1

        texts = df[self.text_column].fillna("").tolist()
        n = len(texts)

        # Only run for small datasets (O(n^2) comparison)
        if n > 2000:
            report.add_issue(ValidationIssue(
                severity="info",
                category="duplicate",
                message=(
                    f"Skipping near-duplicate check: "
                    f"dataset too large ({n} samples)"
                ),
            ))
            return

        word_sets = [set(str(t).lower().split()) for t in texts]
        near_dups = []

        for i in range(n):
            for j in range(i + 1, n):
                if not word_sets[i] or not word_sets[j]:
                    continue
                intersection = len(word_sets[i] & word_sets[j])
                union = len(word_sets[i] | word_sets[j])
                jaccard = intersection / union if union > 0 else 0

                if jaccard >= self.NEAR_DUP_THRESHOLD:
                    near_dups.append((i, j, round(jaccard, 3)))

        if near_dups:
            affected = list(set(
                r for pair in near_dups for r in [pair[0], pair[1]]
            ))
            report.add_issue(ValidationIssue(
                severity="warning",
                category="duplicate",
                message=(
                    f"{len(near_dups)} near-duplicate pairs "
                    f"found (Jaccard >= {self.NEAR_DUP_THRESHOLD})"
                ),
                affected_rows=affected,
                details={
                    "pairs_count": len(near_dups),
                    "sample_pairs": near_dups[:10],
                },
            ))
        else:
            report.add_issue(ValidationIssue(
                severity="info",
                category="duplicate",
                message="No near-duplicate texts found",
            ))

    def _check_label_consistency(self, df: pd.DataFrame,
                                 report: ValidationReport):
        report.num_checks_run += 1
        labels = df[self.label_column].unique()

        # Check for whitespace issues in labels
        stripped = [str(l).strip() for l in labels]
        originals = [str(l) for l in labels]

        mismatches = [
            (orig, strip)
            for orig, strip in zip(originals, stripped)
            if orig != strip
        ]
        if mismatches:
            report.add_issue(ValidationIssue(
                severity="warning",
                category="label",
                message=(
                    f"Labels with whitespace issues: "
                    f"{[m[0] for m in mismatches]}"
                ),
            ))

        # Check for very similar labels (potential typos)
        from difflib import SequenceMatcher
        similar_pairs = []
        label_list = sorted(stripped)
        for i in range(len(label_list)):
            for j in range(i + 1, len(label_list)):
                ratio = SequenceMatcher(
                    None,
                    label_list[i].lower(),
                    label_list[j].lower(),
                ).ratio()
                if ratio > 0.8:
                    similar_pairs.append(
                        (label_list[i], label_list[j], round(ratio, 3))
                    )

        if similar_pairs:
            report.add_issue(ValidationIssue(
                severity="warning",
                category="label",
                message=(
                    f"Potentially similar labels (possible typos): "
                    f"{similar_pairs}"
                ),
            ))
        else:
            report.add_issue(ValidationIssue(
                severity="info",
                category="label",
                message=(
                    f"All {len(labels)} labels are distinct and clean"
                ),
            ))

    def _check_text_quality(self, df: pd.DataFrame,
                            report: ValidationReport):
        report.num_checks_run += 1
        texts = df[self.text_column].fillna("")
        lengths = texts.str.len()

        # Short texts
        short_mask = lengths < self.MIN_TEXT_LENGTH
        if short_mask.any():
            short_rows = df[short_mask].index.tolist()
            report.add_issue(ValidationIssue(
                severity="warning",
                category="text_quality",
                message=(
                    f"{short_mask.sum()} texts shorter than "
                    f"{self.MIN_TEXT_LENGTH} characters"
                ),
                affected_rows=short_rows,
            ))

        # Empty texts
        empty_mask = texts.str.strip() == ""
        if empty_mask.any():
            empty_rows = df[empty_mask].index.tolist()
            report.add_issue(ValidationIssue(
                severity="error",
                category="text_quality",
                message=f"{empty_mask.sum()} empty texts",
                affected_rows=empty_rows,
            ))

        # Check for very long texts (potential data issues)
        p99 = lengths.quantile(0.99)
        outlier_mask = lengths > p99 * 3
        if outlier_mask.any():
            outlier_rows = df[outlier_mask].index.tolist()
            report.add_issue(ValidationIssue(
                severity="info",
                category="text_quality",
                message=(
                    f"{outlier_mask.sum()} texts are extreme outliers "
                    f"in length (> 3x the 99th percentile)"
                ),
                affected_rows=outlier_rows,
            ))

        if not short_mask.any() and not empty_mask.any():
            report.add_issue(ValidationIssue(
                severity="info",
                category="text_quality",
                message="All texts pass quality checks",
            ))

    def _check_class_balance(self, df: pd.DataFrame,
                             report: ValidationReport):
        report.num_checks_run += 1
        counts = df[self.label_column].value_counts()
        ratio = counts.max() / counts.min() if counts.min() > 0 else float("inf")

        if ratio > self.MAX_IMBALANCE_RATIO:
            report.add_issue(ValidationIssue(
                severity="warning",
                category="label",
                message=(
                    f"Class imbalance detected: ratio "
                    f"{ratio:.1f}x (max acceptable: "
                    f"{self.MAX_IMBALANCE_RATIO}x). "
                    f"Largest: {counts.idxmax()} ({counts.max()}), "
                    f"Smallest: {counts.idxmin()} ({counts.min()})"
                ),
            ))
        else:
            report.add_issue(ValidationIssue(
                severity="info",
                category="label",
                message=(
                    f"Class balance is acceptable "
                    f"(ratio: {ratio:.1f}x)"
                ),
            ))


if __name__ == "__main__":
    from .loaders import load_capcc_v1

    df, info = load_capcc_v1()
    validator = DatasetValidator()
    report = validator.validate(df, dataset_info=info)
    report.print_report()
