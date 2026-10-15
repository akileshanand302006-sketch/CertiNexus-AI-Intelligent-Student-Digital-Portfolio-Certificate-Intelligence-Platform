"""
CertiNexus AI — Storage Budget Manager (10 GB Enforcement)
Monitors local dataset cache, temporary shards, model weights, and generates DATA_STORAGE_REPORT.md.
"""

import os
import shutil
from typing import Any, Dict, List, Optional


class StorageBudgetManager:
    """Enforces 10 GB storage budget for datasets and caching."""

    DEFAULT_BUDGET_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB

    def __init__(self, root_dir: Optional[str] = None, budget_bytes: Optional[int] = None):
        self.root_dir = root_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.budget_bytes = budget_bytes or self.DEFAULT_BUDGET_BYTES
        self.tracked_directories = [
            os.path.join(self.root_dir, "dataset"),
            os.path.join(self.root_dir, "storage"),
            os.path.join(self.root_dir, "backend", "storage"),
            os.path.join(self.root_dir, "ml", "artifacts"),
            os.path.join(self.root_dir, "ml", "models"),
        ]
        # Include huggingface cache if inside user profile
        hf_cache = os.path.expanduser("~/.cache/huggingface")
        if os.path.exists(hf_cache):
            self.tracked_directories.append(hf_cache)

    def get_directory_size(self, path: str) -> int:
        """Calculate total directory size in bytes."""
        total = 0
        if not os.path.exists(path):
            return 0
        if os.path.isfile(path):
            return os.path.getsize(path)
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
        return total

    def audit_storage(self) -> Dict[str, Any]:
        """Audit disk usage across tracked directories."""
        details = {}
        total_used = 0

        for path in self.tracked_directories:
            if os.path.exists(path):
                sz = self.get_directory_size(path)
                details[path] = {
                    "bytes": sz,
                    "mb": round(sz / (1024 * 1024), 2),
                    "gb": round(sz / (1024 * 1024 * 1024), 3),
                }
                total_used += sz

        remaining = max(0, self.budget_bytes - total_used)
        pct_used = (total_used / self.budget_bytes) * 100

        return {
            "budget_bytes": self.budget_bytes,
            "budget_gb": round(self.budget_bytes / (1024 * 1024 * 1024), 2),
            "total_used_bytes": total_used,
            "total_used_mb": round(total_used / (1024 * 1024), 2),
            "total_used_gb": round(total_used / (1024 * 1024 * 1024), 3),
            "remaining_bytes": remaining,
            "remaining_gb": round(remaining / (1024 * 1024 * 1024), 3),
            "percent_used": round(pct_used, 2),
            "is_within_budget": total_used <= self.budget_bytes,
            "breakdown": details,
        }

    def is_within_budget(self, extra_bytes: int = 0) -> bool:
        """Check if current usage plus optional extra bytes is within budget."""
        audit = self.audit_storage()
        return (audit["total_used_bytes"] + extra_bytes) <= self.budget_bytes

    def cleanup_temp_cache(self) -> int:
        """Safely clean temporary files and shards without deleting user files or model checkpoints."""
        freed = 0
        temp_dirs = [
            os.path.join(self.root_dir, "storage", "temp_shards"),
            os.path.join(self.root_dir, "dataset", "temp"),
            os.path.join(self.root_dir, ".pytest_cache"),
        ]
        for td in temp_dirs:
            if os.path.exists(td):
                sz = self.get_directory_size(td)
                shutil.rmtree(td, ignore_errors=True)
                freed += sz
        return freed

    def generate_storage_report(self, output_file: Optional[str] = None) -> str:
        """Generate DATA_STORAGE_REPORT.md."""
        audit = self.audit_storage()
        out_path = output_file or os.path.join(self.root_dir, "DATA_STORAGE_REPORT.md")

        lines = [
            "# CertiNexus AI — Data Storage & 10 GB Budget Report",
            "",
            f"**Audit Status**: {'✅ WITHIN BUDGET' if audit['is_within_budget'] else '⚠️ OVER BUDGET'}",
            f"- **Configured Budget**: {audit['budget_gb']} GB",
            f"- **Current Total Used**: {audit['total_used_gb']} GB ({audit['total_used_mb']} MB)",
            f"- **Remaining Budget Headroom**: {audit['remaining_gb']} GB",
            f"- **Budget Utilization**: {audit['percent_used']}%",
            "",
            "## Storage Category Breakdown",
            "",
            "| Directory / Resource Path | Size (MB) | Size (GB) | Status |",
            "| :--- | :--- | :--- | :--- |",
        ]

        for p, d in audit["breakdown"].items():
            rel_name = os.path.relpath(p, self.root_dir) if p.startswith(self.root_dir) else p
            lines.append(f"| `{rel_name}` | {d['mb']} MB | {d['gb']} GB | Managed |")

        lines.extend([
            "",
            "## Streaming Ingestion Strategy",
            "- **Remote Direct Ingestion**: Datasets such as HuggingFace KYC and BhartiOCR are consumed via streaming iterators (`streaming=True`) with bounded batch limits rather than bulk-downloading full multi-gigabyte archives.",
            "- **Zero Unnecessary Duplication**: Extracted samples are streamed in memory directly into normalization pipelines, preventing archive + extracted duplicates.",
            "- **Separation of Concerns**: Model checkpoints (`ml/models/production`) are tracked separately from streaming cache, ensuring deterministic reproducibility.",
        ])

        content = "\n".join(lines)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        return content
