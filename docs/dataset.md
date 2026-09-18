# CertiNexus AI — Dataset Documentation & Data Card

**Course**: 20MSSL12 Machine Learning Lab  
**Corpus Title**: CertiNexus Academic & Professional Certificate Corpus (CAPCC-v1)  
**Task**: 11-Class Supervised Text Classification  
**License**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  

---

## 1. Dataset Overview

The CertiNexus Academic & Professional Certificate Corpus (CAPCC-v1) is a specialized dataset constructed to train, validate, and benchmark supervised NLP models for automated certificate intelligence.

| Metric | Value |
| :--- | :--- |
| **Total Samples ($N$)** | 605 records |
| **Target Classes ($|\mathcal{C}|$)** | 11 mutually exclusive categories |
| **Class Distribution** | Balanced (~55 samples per class) |
| **Language** | English (en-US / en-IN academic domain) |
| **Primary Data Modality** | Textual corpus simulating raw OCR extractions |
| **Feature Formats** | Raw OCR text, cleaned text, token counts, metadata fields |
| **Split Strategy** | Stratified 70% Train (423), 15% Val (91), 15% Held-out Test (91) |

---

## 2. Category Taxonomy & Distribution

The 11 categories represent the full spectrum of collegiate and early-career student achievements:

| Category | Description | Primary Keyword Indicators | Sample Count | Train / Val / Test |
| :--- | :--- | :--- | :--- | :--- |
| **Academic Achievement** | Dean's list, rank certificates, GPA honors, academic merit | `merit`, `distinction`, `scholarship`, `grade`, `academic excellence` | 55 | 39 / 8 / 8 |
| **Certification** | Industry & vendor technical credentials | `certified`, `accredited`, `credential`, `examination`, `professional` | 55 | 39 / 8 / 8 |
| **Conference** | Paper presentation, academic proceedings, delegate attendance | `proceedings`, `presented`, `research`, `author`, `symposium` | 55 | 39 / 8 / 8 |
| **Cultural Activity** | Arts, music, theater, literary, dance competitions | `dance`, `music`, `drama`, `fest`, `performance`, `cultural` | 55 | 39 / 8 / 8 |
| **Hackathon** | 24–48h sprint competitions, prototyping hackathons | `hackathon`, `sprint`, `hack`, `codefest`, `prototype`, `24-hour` | 55 | 39 / 8 / 8 |
| **Internship** | Industrial training, summer internships, apprentice completion | `internship`, `trainee`, `tenure`, `stipend`, `mentorship`, `industry` | 55 | 39 / 8 / 8 |
| **Seminar** | Guest lectures, symposiums, tech talks, panel attendances | `seminar`, `lecture`, `talk`, `speaker`, `keynote`, `session` | 55 | 39 / 8 / 8 |
| **Sports** | Athletic tournaments, inter-collegiate leagues, championships | `tournament`, `championship`, `athletic`, `runner-up`, `match`, `goals` | 55 | 39 / 8 / 8 |
| **Technical Competition** | Coding contests, robotics challenges, algorithmic events | `coding`, `algorithmic`, `debug`, `robotics`, `contest`, `quiz` | 55 | 39 / 8 / 8 |
| **Volunteer Activity** | Community service, NSS, NCC, NGO outreach, philanthropy | `volunteer`, `community service`, `outreach`, `ngo`, `social welfare` | 55 | 39 / 8 / 8 |
| **Workshop** | Hands-on bootcamps, technical training workshops | `hands-on`, `workshop`, `bootcamp`, `practical`, `laboratory` | 55 | 39 / 8 / 8 |

---

## 3. Synthetic Corpus Generation Methodology

### 3.1 Design Motivation & PII Protection
Real university certificates contain sensitive Personally Identifiable Information (PII), such as:
- Student permanent registration numbers
- Legal names and signatures of university chancellors/deans
- Security QR codes and cryptographic hashes

Collecting real student credentials without institutional review board (IRB) clearance introduces severe GDPR and privacy liability. To establish a legally sound, reproducible, and ethically unencumbered benchmark, a parameterized corpus generator was authored in `dataset/generate_dataset.py`.

### 3.2 Combinatorial Template Generation
For each of the 11 classes:
1. Multiple realistic document formats were engineered mirroring standard corporate, university, and IEEE/ACM certificates.
2. Parameter spaces incorporate stochastic substitution of:
   - **Issuing Organizations**: Renowned tech companies (Google, Microsoft, Amazon), universities (Stanford, MIT, IIT, PSG Tech), sports bodies, and NGOs.
   - **Event & Project Titles**: Diverse domains (Cloud Computing, Full Stack Web, Neural Networks, Embedded Systems).
   - **Recipient Designations**: Fictionalized participant identities.
   - **Formal Phrases**: "has actively participated in", "is hereby recognized for outstanding performance", "completed the requirements of".

### 3.3 OCR Noise Modeling
To simulate the degradation introduced by physical document scanning and mobile camera OCR, a stochastic noise model $T_\epsilon(\text{text})$ was implemented:
- **Character Inversion / Substitution**: Substituting visually ambiguous glyphs (e.g., `l` $\leftrightarrow$ `1`, `O` $\leftrightarrow$ `0`, `S` $\leftrightarrow$ `5`, `c` $\leftrightarrow$ `e`) with probability $p_\text{sub} = 0.03$.
- **Token Fusion & Fission**: Randomly deleting spaces between adjacent tokens or inserting whitespace within compound words.
- **Punctuation Stripping**: Random deletion of colons, hyphens, and periods.

---

## 4. Dataset Splits & Leakage Prevention

A strict three-way stratified split was applied:
- **Train Set (70%, $N=423$)**: Used exclusively for feature vocabulary construction, cross-validation, and model parameter estimation.
- **Validation Set (15%, $N=91$)**: Used exclusively for hyperparameter tuning and model selection via grid search.
- **Held-Out Test Set (15%, $N=91$)**: Sealed during all exploratory feature engineering and tuning. Evaluated strictly once on the final production candidate.

No data points from the validation or test splits were exposed to the TF-IDF vectorizer vocabulary fitting, eliminating feature leakage.
