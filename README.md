# 🧠 CertiNexus AI

### Intelligent Student Digital Portfolio & Certificate Intelligence Platform

**Five-Year Integrated M.Sc. (Software Systems)**
**20MSSL12 — Machine Learning Laboratory | 2026–2027**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/) [![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/) [![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/) [![Vite](https://img.shields.io/badge/Vite-5.0%2B-646CFF.svg)](https://vitejs.dev/) [![License](https://img.shields.io/badge/License-CC--BY--SA--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## 📌 Overview

**CertiNexus AI** is a machine-learning-based student achievement intelligence platform that transforms unstructured certificates and achievement documents into structured, searchable, and meaningful student profiles.

Students often accumulate certificates from academic activities, internships, workshops, hackathons, competitions, seminars, sports, volunteering, and other activities. However, these documents are usually stored as isolated files, making it difficult to organize achievements, identify demonstrated skills, and understand overall activity patterns.

CertiNexus AI addresses this problem by combining:

* 📄 Document and text processing
* 🔎 OCR-based text extraction
* 🧹 Text preprocessing
* 🧠 TF-IDF feature engineering
* 🤖 Supervised machine learning
* 📊 Multi-class certificate classification
* 🎯 Confidence estimation
* 🔍 Explainable term attribution
* 🧩 Skill and achievement organization
* 📈 Analytics
* 🌐 Digital portfolio generation

The system converts a certificate from a simple document into structured information that can contribute to a student's digital academic and professional profile.

---

# 🎯 Problem Statement

Students participate in numerous academic and extracurricular activities throughout their academic journey, resulting in a growing collection of certificates and achievement documents.

Manually organizing these documents creates several problems:

* Certificates are difficult to categorize consistently.
* Important information is buried inside document text.
* Students may not have a clear view of their accumulated skills.
* Achievement trends are difficult to analyze.
* Creating a professional portfolio requires repetitive manual work.
* Searching across a large certificate collection is inefficient.

**CertiNexus AI** applies machine learning to automatically classify certificate content and organize achievement information into a structured digital portfolio.

---

# 💡 Proposed Solution

The system follows an intelligent document-to-profile workflow:

```text
Certificate / Achievement Document
              │
              ▼
        Document Processing
              │
              ▼
             OCR
              │
              ▼
       Extracted Certificate Text
              │
              ▼
       Text Preprocessing
              │
              ▼
           TF-IDF
              │
              ▼
     ┌────────┼─────────┐
     │        │         │
     ▼        ▼         ▼
  Naive   Logistic   Linear SVM
  Bayes   Regression
     │        │         │
     └────────┼─────────┘
              ▼
      Certificate Category
              │
              ▼
     Confidence & Explanation
              │
              ▼
     Structured Achievement
              │
              ▼
      Student Digital Profile
              │
       ┌──────┼───────┐
       ▼      ▼       ▼
    Skills  Analytics Portfolio
```

---

# 🔬 Machine Learning Component

The central ML task is formulated as an **11-class supervised text classification problem**.

Given certificate text represented as a feature vector:

$$
\mathbf{x} = \text{TF-IDF}(\text{certificate text})
$$

the classifier predicts:

$$
\hat{y} = \arg\max_{c \in C} P(y=c|\mathbf{x})
$$

where \(C\) represents the set of certificate categories.

---

## 🏷️ Classification Categories

The current dataset contains **11 achievement categories**:

| Category                 | Description                            |
| ------------------------ | -------------------------------------- |
| 🎓 Academic Achievement  | Academic awards and accomplishments    |
| 📜 Certification         | Course and certification achievements  |
| 🎤 Conference            | Conference participation               |
| 🎭 Cultural Activity     | Cultural and creative activities       |
| 💻 Hackathon             | Hackathon participation or achievement |
| 🏢 Internship            | Internship-related certificates        |
| 📚 Seminar               | Seminar participation                  |
| 🏅 Sports                | Sports-related achievements            |
| 🏆 Technical Competition | Technical contests and competitions    |
| 🤝 Volunteer Activity    | Volunteering and community activities  |
| 🛠️ Workshop             | Workshop participation                 |

---

# 🤖 Machine Learning Models

Three traditional supervised learning algorithms are evaluated.

### 1. Multinomial Naive Bayes

Used as the **baseline classifier**.

It provides a simple probabilistic reference point against which the other classification algorithms can be evaluated.

---

### 2. Logistic Regression

Used as a supervised multi-class text classification model.

The model learns relationships between TF-IDF features and certificate categories and produces class probabilities that can contribute to confidence estimation.

---

### 3. Linear Support Vector Machine

Implemented using `LinearSVC`.

The model learns separating hyperplanes between certificate categories and is evaluated against the baseline and Logistic Regression model.

---

# 🧮 Feature Engineering

The certificate text is transformed into numerical representations before being provided to the ML algorithms.

## TF-IDF Word Features

Uses:

```text
Word n-grams: (1, 2)
```

This captures:

* Individual words
* Two-word phrases

Example:

```text
machine
learning
machine learning
certificate
achievement
```

---

## Word + Character Features

The combined representation uses:

```text
Word n-grams:  (1, 2)
Character n-grams: (2, 4)
```

Character features help capture variations caused by:

* OCR errors
* Spelling variations
* Partial words
* Formatting differences

---

## Enriched Features

The enriched representation combines TF-IDF features with engineered document-level and numerical density features.

This allows the model to use both textual information and additional characteristics of the extracted document content.

---

# 📚 Dataset

The project uses **CAPCC-v1**, a structured certificate classification corpus containing:

**605 samples**

distributed across:

**11 classes**

The dataset is designed to represent certificate text and includes simulated OCR noise to make the classification problem more representative of imperfect document extraction.

### Dataset Split

| Split         | Samples | Percentage |
| ------------- | ------: | ---------: |
| Training      |     423 |        70% |
| Validation    |      91 |        15% |
| Held-out Test |      91 |        15% |
| **Total**     | **605** |   **100%** |

The dataset uses **stratified splitting** so that the class distribution is maintained across the partitions.

---

# 🧪 Model Training & Evaluation

The training pipeline evaluates the classifiers systematically rather than relying on a single model.

### Training workflow

```text
Dataset
   ↓
Data Validation
   ↓
Text Preprocessing
   ↓
Feature Engineering
   ↓
Train / Validation / Test Split
   ↓
Baseline Model
   ↓
Candidate Models
   ↓
Hyperparameter Optimization
   ↓
Cross-Validation
   ↓
Held-Out Test Evaluation
   ↓
Model Selection
   ↓
Production Pipeline
```

---

# ⚙️ Hyperparameter Optimization

The project uses:

**Stratified 5-Fold GridSearchCV**

for model and feature configuration tuning on the training data.

The held-out test set remains separate for final evaluation.

This prevents the final benchmark from being used during model optimization.

---

# 📊 Evaluation Metrics

The models are evaluated using:

* Accuracy
* Precision
* Recall
* Macro-F1
* Confusion Matrix
* Cross-validation performance
* Per-class performance
* Inference latency

Macro-F1 is particularly useful because it evaluates performance across all classes rather than allowing large classes to dominate the metric.

---

# 🏆 Current Benchmark Result

The current experimental pipeline achieved:

```text
Macro-F1: 1.0000
CPU inference latency: < 1 ms
```

on the held-out benchmark used in the project.

> **Important:** These results apply to the current CAPCC-v1 benchmark and its simulated OCR-noise setting. They should not be interpreted as guaranteed real-world performance on unseen certificates from external sources.

---

# 🎯 Confidence & Explainability

CertiNexus AI does not only produce a predicted category.

The system also provides information about the prediction.

### Confidence

The classification pipeline supports calibrated confidence estimation using temperature scaling.

Example:

```text
Prediction:
Internship

Confidence:
94.2%
```

### Explainability

The system can identify influential terms contributing to the classification.

Example:

```text
Predicted Category: Internship

Influential Terms:
• intern
• company
• training
• industry
• completed
```

The system supports **Top-5 influential term attribution** for model interpretation.

---

# 📄 Certificate Intelligence

After document processing, the platform can organize certificate information such as:

```text
Student Name
Certificate Title
Issuing Organization
Issue Date
Credential ID
Category
Skills
Classification Confidence
```

This transforms raw certificate documents into structured achievement records.

---

# 🧩 Skill Intelligence

Certificate information can be organized into a skill-oriented profile.

Example:

```text
Technical Skills
├── Python
├── Machine Learning
├── Java
└── Web Development

Professional Skills
├── Leadership
├── Communication
└── Teamwork
```

This provides a clearer representation of what skills are demonstrated across a student's achievements.

---

# 📈 Achievement Analytics

The platform provides analytical views of student achievements, including:

* Certificates by category
* Achievement distribution
* Activity timeline
* Skill distribution
* Portfolio statistics
* Achievement trends

Example:

```text
Certificates          24
Achievements          31
Skills                18
Portfolio Completion  86%
```

---

# 🌐 Digital Portfolio

CertiNexus AI transforms structured achievements into a digital portfolio.

The portfolio can organize:

* Profile
* Education
* Skills
* Certificates
* Achievements
* Projects
* Activities
* Experience

This reduces the effort required to manually maintain a separate portfolio of academic achievements.

---

# 📄 Resume Generation

The platform also supports an interactive resume-building workflow.

Student information can be assembled from the structured profile to generate a professional resume.

Supported concepts include:

* Profile information
* Education
* Skills
* Certificates
* Achievements
* Projects
* Experience

The web application provides an interactive resume builder with multiple visual templates.

---

# 🎨 Liquid Glass AI Interface

The web application follows a custom **Liquid Glass AI** design system.

### Design characteristics

* Frosted glass surfaces
* Backdrop blur
* Translucent panels
* Subtle borders
* Aurora-style background effects
* Soft glow
* Layered depth
* Smooth animations
* Responsive layouts

The design is intended to give the ML platform a modern AI-product identity while keeping the data and analytics readable.

---

# 🖥️ Application Architecture

CertiNexus AI follows a decoupled architecture:

```text
                 ┌─────────────────────┐
                 │    React Web App    │
                 │     React 19        │
                 └──────────┬──────────┘
                            │
                            │ REST API
                            ▼
                 ┌─────────────────────┐
                 │   FastAPI Backend   │
                 │   Python / REST     │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Database │  │ ML Engine│  │  Storage │
        └──────────┘  └──────────┘  └──────────┘
                            │
                            ▼
                     ML Classification
                            │
                  ┌─────────┼─────────┐
                  ▼         ▼         ▼
                 NB        LR        SVM
```

This separation allows the machine-learning pipeline, backend services, and frontend interface to evolve independently.

---

# 🛠️ Technology Stack

## Machine Learning

* Python
* NumPy
* Pandas
* Scikit-learn
* TF-IDF
* GridSearchCV
* Cross-validation
* Joblib

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* REST APIs

## Frontend

* React 19
* Vite
* JavaScript
* CSS
* Liquid Glass UI

## Database

* SQL database architecture
* SQLAlchemy ORM

## Document Processing

* OCR pipeline
* Text preprocessing
* Certificate information extraction

## Development

* Git
* GitHub
* VS Code
* Unittest

---

# 📁 Repository Structure

```text
certinexus/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── auth/
│       │   ├── certificates/
│       │   ├── analytics/
│       │   ├── portfolio/
│       │   ├── resume/
│       │   └── admin/
│       │
│       ├── database/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── dataset/
│   ├── generate_dataset.py
│   ├── raw/
│   ├── processed/
│   │   └── cleaned_dataset.csv
│   └── README.md
│
├── docs/
│   ├── proposal.md
│   ├── literature-review.md
│   ├── dataset.md
│   ├── methodology.md
│   ├── architecture.md
│   ├── ml-experiments.md
│   ├── user-stories.md
│   └── deployment.md
│
├── ml/
│   ├── preprocessing/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   └── models/
│       └── production/
│
├── tests/
│   └── test_ml_pipeline.py
│
├── web/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   ├── styles/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── experiments.csv
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/your-org/certinexus.git
cd certinexus
```

---

## 2. Create Python Environment

### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# 🧠 Run the ML Pipeline

The machine-learning components are located under:

```text
ml/
```

The training pipeline performs:

```text
Preprocessing
→ Feature Engineering
→ Baseline Training
→ Model Training
→ Hyperparameter Search
→ Evaluation
→ Model Serialization
```

The trained production artifact is stored under:

```text
ml/models/production/
```

---

# ⚡ Start FastAPI Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 🌐 Start React Frontend

```bash
cd web
npm install
npm run dev
```

The development application will be available through the Vite development server.

---

# 🧪 Run Tests

From the project root:

```bash
python -m unittest tests/test_ml_pipeline.py
```

Also verify:

```bash
python -m unittest discover
```

---

# 📚 Documentation

The `docs/` directory contains the complete technical and academic documentation for the project.

### 📋 Project Proposal

Defines the problem, objectives, scope, and academic alignment.

### 📖 Literature Review

Provides background research, related work, research gap, and comparative analysis.

### 🗃️ Dataset Documentation

Documents CAPCC-v1, its structure, generation methodology, preprocessing, and split strategy.

### 🧠 ML Methodology

Explains:

* Problem formulation
* Text preprocessing
* TF-IDF
* Feature engineering
* Classification algorithms
* Hyperparameter optimization
* Evaluation methodology

### 🧪 ML Experiments

Contains experimental results for:

```text
EXP-001 → EXP-009
```

including:

* Model comparison
* Feature comparison
* Evaluation metrics
* Confusion matrix
* Failure analysis

### 🏗️ System Architecture

Documents:

* Application architecture
* API communication
* Database entities
* ML integration
* System workflows

### 👤 User Stories

Defines user interactions and acceptance criteria.

### 🚀 Deployment Guide

Contains environment configuration, deployment requirements, production builds, and Docker orchestration.

---

# 🔬 Research & Experimentation

CertiNexus AI is structured not only as an application but also as an **ML experimentation platform**.

The project allows systematic comparison of:

```text
Feature Representation
        ×
Machine Learning Algorithm
        ×
Hyperparameter Configuration
        ↓
Evaluation Metrics
```

This makes it possible to study how different text representations and traditional classification algorithms affect certificate classification performance.

---

# 📊 Experiment Tracking

Experimental configurations and results are maintained in:

```text
experiments.csv
```

This provides a persistent record of model experiments and enables reproducibility of the ML workflow.

---

# 🧪 Reproducibility

The project follows a reproducible ML workflow:

```text
Dataset
   ↓
Preprocessing
   ↓
Feature Engineering
   ↓
Train / Validation / Test Split
   ↓
Cross-Validation
   ↓
Hyperparameter Optimization
   ↓
Final Evaluation
   ↓
Serialized Model
```

The held-out test set is kept separate from model optimization.

---

# 🔐 Data & Model Considerations

The current dataset is a **project-specific synthetic corpus** designed for controlled experimentation.

Therefore:

* Benchmark results are specific to CAPCC-v1.
* Simulated OCR noise does not represent every real-world OCR condition.
* Real-world certificates may contain different layouts, languages, fonts, terminology, and noise patterns.
* Classification confidence should not be interpreted as certificate authenticity.
* A classification prediction indicates the category inferred by the model, not the validity of the underlying credential.

---

# 🌟 Key Features

### 🤖 Machine Learning

* 11-class certificate classification
* Naive Bayes baseline
* Logistic Regression
* Linear SVM
* TF-IDF feature engineering
* Word and character n-grams
* GridSearchCV
* Stratified 5-fold cross-validation
* Macro-F1 evaluation
* Confusion matrix
* Confidence estimation
* Explainable term attribution

### 📄 Certificate Intelligence

* Certificate text processing
* Information extraction
* Automatic categorization
* Achievement organization
* Skill mapping
* Duplicate detection architecture

### 📊 Analytics

* Achievement statistics
* Category distribution
* Skill distribution
* Activity timeline
* Portfolio insights

### 🌐 Digital Portfolio

* Student profile
* Certificate showcase
* Achievement timeline
* Skills
* Resume generation
* Portfolio presentation

### 🎨 User Experience

* Liquid Glass interface
* Responsive dashboard
* Interactive analytics
* Modern AI-inspired visual design
* Smooth micro-interactions

---

# 🗺️ Future Scope

Possible future extensions include:

* Larger real-world certificate datasets
* Multilingual certificate processing
* Improved OCR robustness
* Deep-learning-based document understanding
* Advanced named-entity extraction
* Semantic similarity-based certificate matching
* Automated skill taxonomy expansion
* External credential verification
* Mobile application integration
* Career-oriented recommendation systems

These are future extensions and are not part of the current core ML benchmark unless explicitly implemented.

---

# 🎓 Academic Context

**Project:** CertiNexus AI
**Course:** 20MSSL12 — Machine Learning Laboratory
**Programme:** Five-Year Integrated M.Sc. in Software Systems
**Academic Year:** 2026–2027

The project demonstrates the practical application of machine-learning concepts including:

* Supervised learning
* Text classification
* Feature engineering
* TF-IDF
* Model comparison
* Hyperparameter optimization
* Cross-validation
* Performance evaluation
* Model interpretation
* ML deployment through an application interface

---

# 👥 Authors & Academic Attribution

**Programme:**
Five-Year Integrated M.Sc. in Software Systems

**Course:**
20MSSL12 — Machine Learning Laboratory

**Academic Year:**
2026–2027

---

# 📜 License

This project is released under the:

**Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**

See the license documentation for complete terms.

---

## ⭐ CertiNexus AI

> **From certificates to intelligence.
> From achievements to a digital identity.**

CertiNexus AI demonstrates how machine learning can transform unstructured student achievement documents into structured, searchable, analyzable, and professionally presentable information.
