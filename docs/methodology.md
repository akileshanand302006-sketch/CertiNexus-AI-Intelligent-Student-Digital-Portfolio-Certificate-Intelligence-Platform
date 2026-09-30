# CertiNexus AI — Machine Learning Methodology

**Course**: 20MSSL12 Machine Learning Lab  
**Specialization**: Natural Language Processing & Document Classification  

---

## 1. Problem Formulation & Workflow

CertiNexus AI categorizes unstructured certificate text into 11 distinct achievement classes. The complete ML operational pipeline adheres strictly to academic engineering principles:

```
[Raw Document / OCR Text]
          │
          ▼
┌──────────────────────────────────────┐
│  Phase 1: Preprocessing Pipeline     │
│  - Lowercase normalization           │
│  - Non-ASCII / Artifact filtering    │
│  - Whitespace & Token normalization  │
│  - Selective stopword removal        │
└──────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────┐
│  Phase 2: Feature Engineering        │
│  - Sublinear TF-IDF (1, 2)-grams     │
│  - Min/Max document frequency cuts   │
│  - Character n-gram exploration      │
│  - Metadata density features         │
└──────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────┐
│  Phase 3: Model Architecture & Tuning│
│  - Baseline: MultinomialNB           │
│  - Candidate 1: Logistic Regression  │
│  - Candidate 2: Linear SVM           │
│  - Stratified 5-Fold GridSearchCV    │
└──────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────┐
│  Phase 4: Confidence & Explainability│
│  - Softmax Probability Calibration   │
│  - Feature Weight Term Attribution   │
│  - Uncertainty Threshold Routing     │
└──────────────────────────────────────┘
```

---

## 2. Text Preprocessing Pipeline

Implemented in `ml/preprocessing/text_preprocessor.py` as an scikit-learn compatible `BaseEstimator` and `TransformerMixin`, guaranteeing identical transformation across training and real-time production inference:

1. **Case Normalization**: Converts all text to lowercase to collapse identical lexical tokens (`"CERTIFICATE"` $\rightarrow$ `"certificate"`).
2. **OCR Noise Cleansing**: Regular expressions eliminate stray non-alphanumeric noise patterns while preserving punctuation critical to dates (`YYYY-MM-DD`, `DD/MM/YYYY`) and credential IDs.
3. **Whitespace Standardization**: Replaces arbitrary newline breaks, tabs, and multi-space sequences with single spaces.
4. **Tokenization & Stopword Pruning**: Applies English stopword filtering while retaining directional terms (`"first"`, `"second"`, `"third"`, `"best"`) essential for distinguishing competition rank.

---

## 3. Feature Engineering Variants

Three distinct feature representation strategies were formally implemented and evaluated:

### Experiment A: Word-level N-gram TF-IDF (`tfidf_word`)
Computes term frequency with sublinear scaling $1 + \log(\text{tf})$ and smooth inverse document frequency:

$$\text{tf-idf}(t, d) = (1 + \log \text{tf}(t, d)) \times \left(\log \frac{1 + N}{1 + \text{df}(t)} + 1\right)$$

- **N-gram range**: Unigrams and Bigrams $(1, 2)$
- **Min document frequency**: $\text{min\_df} = 2$ (pruning unique typos)
- **Sublinear TF**: Enabled (dampening excessive term repetition)

### Experiment B: Word + Character N-grams (`tfidf_word_char`)
Combines word $(1, 2)$-grams with character $(2, 4)$-grams via `FeatureUnion`.
- **Purpose**: Evaluates robustness against character-level OCR distortions (e.g., misspelled `"partic1pated"` matches `"part"` and `"tici"` character n-grams).

### Experiment C: Enriched Metadata Hybrid (`tfidf_enriched`)
Augments the TF-IDF matrix with dense statistical features:
- Normalized document length (character & token count)
- Numeric and date density ratios
- Technical keyword frequency density

---

## 4. Model Selection & Theoretical Justification

### 4.1 Baseline: Multinomial Naive Bayes
- **Formula**:
  $$P(c \mid \mathbf{x}) \propto P(c) \prod_{i=1}^{d} P(w_i \mid c)^{x_i}$$
- **Laplace Smoothing**:
  $$\hat{P}(w_i \mid c) = \frac{N_{ci} + \alpha}{N_c + \alpha |V|}$$
- **Role**: Serves as the initial empirical benchmark. Ultra-fast training ($<5\text{ms}$), but sensitive to correlated n-grams.

### 4.2 Candidate Model 1: Logistic Regression
- **Optimization**:
  $$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{i=1}^n \log\left(1 + \exp(-y_i (\mathbf{w}^T \mathbf{x}_i + b))\right)$$
- **Multi-Class Strategy**: Multinomial softmax cross-entropy loss with L2 regularization.
- **Advantage**: Generates naturally calibrated posterior class probabilities, critical for computing confidence scores.

### 4.3 Candidate Model 2: Linear Support Vector Machine (LinearSVC)
- **Optimization**:
  $$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{i=1}^n \max\left(0, 1 - y_i (\mathbf{w}^T \mathbf{x}_i + b)\right)^2$$
- **Multi-Class Strategy**: One-vs-Rest (OvR) hinge loss minimization.
- **Advantage**: Maximum margin hyperplane separation in high-dimensional sparse vector spaces.

---

## 5. Hyperparameter Tuning Protocol

Tuning was executed strictly within the training split using `GridSearchCV` with **Stratified 5-Fold Cross Validation** to preserve class balances:

| Model | Hyperparameter Grid | Optimal Setting Found |
| :--- | :--- | :--- |
| **MultinomialNB** | `alpha`: $[0.001, 0.01, 0.1, 0.5, 1.0]$ | $\alpha = 0.01$ |
| **Logistic Regression** | `C`: $[0.01, 0.1, 1.0, 10.0]$, `class_weight`: $[\text{None}, \text{'balanced'}]$ | $C = 10.0$, `class_weight` = None |
| **Linear SVM** | `C`: $[0.01, 0.1, 1.0, 10.0]$, `class_weight`: $[\text{None}, \text{'balanced'}]$ | $C = 1.0$, `class_weight` = None |

---

## 6. Evaluation Metrics

Because the test corpus exhibits class balance across all 11 categories, the primary evaluation criterion is **Macro-Averaged F1-Score**:

$$\text{Macro-F1} = \frac{1}{|\mathcal{C}|} \sum_{c \in \mathcal{C}} \frac{2 \times P_c \times R_c}{P_c + R_c}$$

Where:
- $P_c = \frac{\text{TP}_c}{\text{TP}_c + \text{FP}_c}$ (Precision for class $c$)
- $R_c = \frac{\text{TP}_c}{\text{TP}_c + \text{FN}_c}$ (Recall for class $c$)

Supplemental metrics tracked include **Weighted-F1**, **Macro-Precision**, **Macro-Recall**, **Overall Accuracy**, **Training Wall Time**, and **Per-Sample Inference Latency**.

---

## 7. Confidence Routing & Active Learning Feedback

In the production inference pipeline (`ml/inference/predictor.py`):
1. **Confidence Score**: $p_{\max} = \max_{c \in \mathcal{C}} P(y = c \mid \mathbf{x})$.
2. **Decision Bands**:
   - **High Confidence** ($p \ge 0.85$): Automatically tagged, marked verified.
   - **Medium Confidence** ($0.70 \le p < 0.85$): Tagged with cautionary indicator.
   - **Low Confidence** ($p < 0.70$): Marked `review_required`. User prompt triggers manual label review.
3. **Model Feedback Loop**: Any user corrections are captured in the `model_feedback` table for scheduled offline model retraining.
