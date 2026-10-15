# CertiNexus AI — Data Storage & 10 GB Budget Report

**Audit Status**: ✅ WITHIN BUDGET
- **Configured Budget**: 10.0 GB
- **Current Total Used**: 0.97 GB (993.66 MB)
- **Remaining Budget Headroom**: 9.03 GB
- **Budget Utilization**: 9.7%

## Storage Category Breakdown

| Directory / Resource Path | Size (MB) | Size (GB) | Status |
| :--- | :--- | :--- | :--- |
| `dataset` | 992.48 MB | 0.969 GB | Managed |
| `storage` | 0.31 MB | 0.0 GB | Managed |
| `backend\storage` | 0.17 MB | 0.0 GB | Managed |
| `ml\artifacts` | 0.0 MB | 0.0 GB | Managed |
| `ml\models` | 0.48 MB | 0.0 GB | Managed |
| `C:\Users\HP/.cache/huggingface` | 0.22 MB | 0.0 GB | Managed |

## Streaming Ingestion Strategy
- **Remote Direct Ingestion**: Datasets such as HuggingFace KYC and BhartiOCR are consumed via streaming iterators (`streaming=True`) with bounded batch limits rather than bulk-downloading full multi-gigabyte archives.
- **Zero Unnecessary Duplication**: Extracted samples are streamed in memory directly into normalization pipelines, preventing archive + extracted duplicates.
- **Separation of Concerns**: Model checkpoints (`ml/models/production`) are tracked separately from streaming cache, ensuring deterministic reproducibility.