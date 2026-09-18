# CertiNexus AI

### Intelligent Student Digital Portfolio & Certificate Intelligence Platform
**Five-Year Integrated M.Sc. (Software Systems) — 20MSSL12 Machine Learning Lab Project**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0%2B-646CFF.svg)](https://vitejs.dev/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## 📌 Project Overview

**CertiNexus AI** is a production-grade machine learning platform designed to ingest, process, categorize, and verify student academic credentials and extra-curricular achievements. Combining optical character recognition (OCR), natural language processing (NLP), multi-class supervised classification, skill taxonomy mapping, and a reactive glassmorphic digital portfolio, the platform transforms unstructured certificate documents into cryptographically and structurally verifiable student portfolios.

---

## 🔬 Machine Learning Architecture

- **Formal ML Problem**: 11-Class Supervised Text Classification ($\hat{y} = \arg\max_{c \in \mathcal{C}} P(y=c \mid \mathbf{x})$).
- **Target Categories**: Academic Achievement, Certification, Conference, Cultural Activity, Hackathon, Internship, Seminar, Sports, Technical Competition, Volunteer Activity, Workshop.
- **Corpus**: CAPCC-v1 (605 samples, balanced across 11 classes, simulated OCR noise).
- **Partitioning**: Strict stratified 70% Train (423), 15% Validation (91), 15% Held-out Test (91).
- **Feature Representations**:
  - `tfidf_word`: Sublinear TF-IDF $(1, 2)$-word n-grams.
  - `tfidf_word_char`: Combined word $(1, 2)$-grams and character $(2, 4)$-grams.
  - `tfidf_enriched`: TF-IDF with engineered document and numerical density features.
- **Algorithms Evaluated**:
  1. **Baseline**: Multinomial Naive Bayes (`alpha=1.0`)
  2. **Candidate 1**: Logistic Regression (L2 regularization, softmax probabilities)
  3. **Candidate 2**: Linear Support Vector Machine (`LinearSVC`, OvR hinge loss)
- **Hyperparameter Optimization**: Stratified 5-Fold `GridSearchCV` on the training split.
- **Production Performance**: **1.0000 Macro-F1** on held-out test benchmark with **< 1.0 ms CPU inference latency**.
- **Confidence & Explainability**: Temperature-scaled confidence scores + Top-5 influential term attribution.

---

## 📚 Complete Academic Documentation

The complete documentation suite mandated by the department is available in the [`docs/`](file:///c:/My%20Projects/certinexus/docs/) directory:

1. **[Project Proposal](file:///c:/My%20Projects/certinexus/docs/proposal.md)** — Problem definition, objectives, academic alignment, and timeline.
2. **[Literature Review](file:///c:/My%20Projects/certinexus/docs/literature-review.md)** — In-depth background study with 10 peer-reviewed references, research gap, and comparative matrix.
3. **[Dataset Documentation](file:///c:/My%20Projects/certinexus/docs/dataset.md)** — Data card, synthesis methodology, noise modeling, and split verification.
4. **[ML Methodology](file:///c:/My%20Projects/certinexus/docs/methodology.md)** — Formal pipeline formulation, feature engineering, model derivations, and tuning protocol.
5. **[ML Experiments Report](file:///c:/My%20Projects/certinexus/docs/ml-experiments.md)** — Full empirical results for EXP-001 through EXP-009, confusion matrix, and failure analysis.
6. **[System Architecture](file:///c:/My%20Projects/certinexus/docs/architecture.md)** — 3-tier decoupled architecture, sequence diagrams, and database entity schemas.
7. **[User Stories](file:///c:/My%20Projects/certinexus/docs/user-stories.md)** — 5 comprehensive user stories with acceptance criteria and ML task mappings.
8. **[Deployment Guide](file:///c:/My%20Projects/certinexus/docs/deployment.md)** — Setup, environment configuration, production builds, and Docker orchestration.

---

## 📁 Repository Structure

```
certinexus/
├── backend/                  # FastAPI Application Layer
│   └── app/
│       ├── api/              # REST Endpoints (auth, certs, analytics, portfolio, resume, admin)
│       ├── database/         # SQLAlchemy connection & session manager
│       ├── models/           # Database ORM models (User, Certificate, StudentSkill, etc.)
│       ├── schemas/          # Pydantic validation & response schemas
│       └── main.py           # FastAPI ASGI entrypoint
├── dataset/                  # Dataset Generation & Storage
│   ├── generate_dataset.py   # Stochastic synthetic corpus generator with OCR noise
│   ├── raw/                  # Raw simulated certificate records
│   ├── processed/            # Preprocessed, cleaned dataset (cleaned_dataset.csv)
│   └── README.md             # Dataset card & schema
├── docs/                     # Academic Lab Deliverables & Specifications
│   ├── proposal.md
│   ├── literature-review.md
│   ├── dataset.md
│   ├── methodology.md
│   ├── architecture.md
│   ├── ml-experiments.md
│   ├── user-stories.md
│   └── deployment.md
├── ml/                       # Machine Learning Core
│   ├── preprocessing/        # Sklearn-compatible CertificateTextPreprocessor
│   ├── training/             # train_pipeline.py (EDA, Baseline, GridSearch, Evaluation)
│   ├── inference/            # predictor.py (Production CertificateClassifier)
│   ├── evaluation/           # Evaluation metrics, confusion matrix, error analysis
│   └── models/production/    # Serialized model artifacts (pipeline.joblib, metadata)
├── tests/                    # Automated Test Suite (Unittest)
│   └── test_ml_pipeline.py   # Unit tests for preprocessor, inference, and API endpoints
├── web/                      # React 19 Web Frontend (Liquid Glass AI)
│   ├── src/
│   │   ├── components/       # Glassmorphic layout and UI components
│   │   ├── pages/            # 12 Core pages (Dashboard, Upload, Resume, Analytics, etc.)
│   │   ├── lib/              # API client, JWT auth context
│   │   ├── styles/           # Liquid Glass design system tokens
│   │   └── App.jsx           # Client router & providers
│   ├── package.json
│   └── vite.config.js
├── experiments.csv           # Persistent ML Experiment Tracking Log
├── requirements.txt          # Python runtime dependencies
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Server Setup
```bash
# Clone the repository
git clone https://github.com/your-org/certinexus.git
cd certinexus

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate      # On Windows
# source venv/bin/activate   # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
uvicorn backend.app.main:app --reload --port 8000
```
- API Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd web
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

### 3. Run Automated Tests
```bash
python -m unittest tests/test_ml_pipeline.py
```

---

## 🎨 Liquid Glass AI Design System

The web frontend features a custom **Liquid Glass AI** design aesthetic:
- **Dark Glassmorphism**: Translucent frosted surfaces with dynamic backdrop blur (`backdrop-filter: blur(16px)`).
- **Aurora Glows**: Subtle floating radial gradient blobs (electric blue `#4f46e5`, violet `#7c3aed`, cyan `#06b6d4`).
- **Interactive Resume Builder**: ATS-compatible resume generator with live template preview (Modern Tech, Academic CV, Minimalist, Executive) and one-click PDF printing.
- **ML Research Dashboard**: Live inspection of training experiments, per-class metrics, interactive confusion matrix, and error analysis.

---

## 👥 Authors & Academic Attribution

- **Degree**: Five-Year Integrated M.Sc. in Software Systems
- **Course**: 20MSSL12 — Machine Learning Laboratory
- **Year**: 2026–2027
