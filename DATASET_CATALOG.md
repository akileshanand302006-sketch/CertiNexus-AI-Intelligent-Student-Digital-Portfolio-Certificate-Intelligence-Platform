# CertiNexus AI — Master Dataset Catalog & Governance Inventory

## Overview
This catalog records every public, project-created, and streaming dataset integrated into **CertiNexus AI**. Direct remote streaming and bounded sampling are used to enforce a **10 GB local storage budget** while supporting Indian document intelligence across Identity, Academic, Financial, and Professional domains.

---

## 1. Dataset Inventory Matrix

| Dataset Identifier | Source URL / Repository | Primary Task | Languages | Format & Delivery | License | Auth Required | Cache / Disk Footprint |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAPCC-v1** | `dataset/raw/certificates.csv` | 11-Category Certificate Classification | English | CSV / Tabular with OCR noise | Internal / MIT | No | 0.68 MB (Local) |
| **Indian KYC Document Extraction VLM** | [HuggingFace: Jwalit/kyc-document-extraction-vlm](https://huggingface.co/datasets/Jwalit/kyc-document-extraction-vlm) | Identity Field Extraction (Aadhaar, PAN, Passport) | English, Hindi | Parquet / Streamed VLM QA | Apache-2.0 / CC-BY-4.0 | No | Remote Streamed (~450 MB virtual) |
| **BhartiOCR** | [HuggingFace: Faizaniqbal/BhartiOCR](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR) | Indic Script OCR (Hindi, Tamil, Telugu, etc.) | Indic Scripts & English | WebDataset Shards (`.tar`) / Streamed | CC-BY-4.0 | No | Remote Streamed (~3.2 GB virtual) |
| **Patram-Bench** | [patrambench.github.io](https://patrambench.github.io/) | Indian Layout Analysis & Table Extraction | English, Hindi | Bounded Benchmark Samples | CC-BY-NC-SA-4.0 | No | Remote / Bounded Staged |
| **Mozhi Indic OCR** | [cvit.iiit.ac.in/usodi/tdocrmil.php](https://cvit.iiit.ac.in/usodi/tdocrmil.php) | Indic Document OCR Recognition | Telugu, Tamil, Hindi, Kannada, Malayalam | Bounded Evaluation Batches | Academic Research License | No | Staged Bounded (<650 MB) |
| **RVL-CDIP (Supplementary)** | `dataset/public/rvl-cdip/` | Multi-class Document Type Baseline | English | Document Images / TIF | CC0 / Public Domain | No | 992.4 MB (Staged) |

---

## 2. Ingestion & Streaming Mechanisms

### 2.1 Hugging Face Direct Streaming (`streaming=True`)
- Uses `HuggingFaceStreamingAdapter` in `ml/data_sources/huggingface_stream.py`.
- Consumes remote samples without downloading full multi-gigabyte shard archives.
- Iterators yield samples on-the-fly directly to the preprocessor or training loop.

### 2.2 WebDataset Shard Streaming
- Implemented in `ml/data_sources/webdataset_stream.py`.
- Streams remote `.tar` shard buffers with key-based extraction (`.jpg`, `.txt`, `.json`), enforcing in-memory buffer clearing after each batch.

### 2.3 Storage Budget Enforcement
- Tracked by `StorageBudgetManager` in `ml/data_sources/budget.py`.
- Strict budget threshold: **10.0 GB**.
- Current disk footprint: **0.97 GB** (9.03 GB remaining headroom).
- Automatically clears unneeded temporary shards while preserving model checkpoints and user records.

---

## 3. Data Governance & Privacy Safeguards
- **Sensitive Identity Masking**:
  - Aadhaar 12-digit numbers are masked to `XXXX-XXXX-1234`.
  - PAN cards are masked to `ABCDE****F`.
  - Driving Licences and Bank Accounts have sensitive sequences protected.
- **No Unconsented Data Retention**: Private identity documents are never published to public datasets or committed to Git.
- **Separation of Tasks**:
  - Document-type routing is evaluated independently from certificate classification.
  - OCR recognition is evaluated using Character Error Rate (CER) and Word Error Rate (WER).
