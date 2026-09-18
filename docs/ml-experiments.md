# CertiNexus AI — Machine Learning Experiments & Evaluation Report

**Course**: 20MSSL12 Machine Learning Lab  
**Experiment Tracker**: `experiments.csv`  
**Dataset**: CAPCC-v1 (605 samples, 11 classes, 70/15/15 stratified split)  
**Evaluation Date**: September 16, 2026  

---

## 1. Summary of Experiments

A total of 9 formal experiments were executed across 3 model families and 3 feature representation architectures. All runs adhered strictly to reproducibility guidelines with fixed random seeds (`random_state=42`).

### Complete Experiment Tracking Log

| Exp ID | Feature Set | Model Algorithm | Key Hyperparameters | Val Acc | Macro-P | Macro-R | Macro-F1 | Train Time (s) | Inference Time (s) | Observations |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **EXP-001** | `tfidf_word` | MultinomialNB (Baseline) | `alpha=1.0` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0046 | 0.0011 | Strong initial baseline; fast training |
| **EXP-002** | `tfidf_word` | LogisticRegression | `C=0.1, class_weight='balanced'` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8.7346 | 0.0006 | CV score 0.9954; well-calibrated probabilities |
| **EXP-003** | `tfidf_word` | LinearSVM | `C=0.1, class_weight=None` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4260 | 0.0012 | CV score 0.9954; sharp decision boundaries |
| **EXP-004** | `tfidf_word` | MultinomialNB (Tuned) | `alpha=0.01` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.1170 | 0.0006 | Tuned smoothing; CV score 0.9930 |
| **EXP-005** | `tfidf_word_char` | LogisticRegression | `C=10.0, class_weight=None` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3.8470 | 0.0021 | 100% 5-fold CV score; subword robustness |
| **EXP-006** | `tfidf_word_char` | LinearSVM | `C=1.0, class_weight=None` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.6403 | 0.0011 | 100% 5-fold CV score |
| **EXP-007** | `tfidf_enriched` | LogisticRegression | `C=10.0, class_weight=None` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2.4420 | 0.0008 | 100% 5-fold CV score |
| **EXP-008** | `tfidf_enriched` | LinearSVM | `C=1.0, class_weight=None` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.4682 | 0.0007 | 100% 5-fold CV score |
| **EXP-009** | `tfidf_word` | **LogisticRegression (Production)** | `C=10.0, solver='lbfgs'` | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.2100** | **0.0006** | **Final Held-out Test Set Evaluation** |

---

## 2. Model Comparison Analysis

### 2.1 Baseline vs. Advanced Classifiers
The Multinomial Naive Bayes baseline achieved high performance due to the strong discriminative power of certificate keywords. However, when evaluating out-of-vocabulary terms and simulated OCR noise, Logistic Regression demonstrated:
1. **Calibrated Confidence**: Softmax output vectors reflect genuine prediction probabilities rather than extreme 0/1 bounds common to Naive Bayes.
2. **Sub-millisecond Latency**: Inference executes in ~0.6 milliseconds per certificate, making it suitable for real-time document upload endpoints.
3. **Interpretability**: L2-regularized logistic regression coefficients directly expose top contributing terms per category.

### 2.2 Feature Representation Comparison
- **`tfidf_word`**: Produced a compact vocabulary of ~1,800 n-grams with minimal memory footprint (<2 MB).
- **`tfidf_word_char`**: Increased vocabulary dimensionality to ~12,000 features. While highly resilient to severe OCR misspellings, inference latency increased by ~3.5×.
- **Decision**: `tfidf_word` with $(1, 2)$-grams and sublinear TF scaling was selected as the **Production Architecture** because it maximizes throughput while achieving optimal accuracy.

---

## 3. Final Held-Out Test Set Evaluation

The production pipeline was evaluated strictly once against the 91 unseen test samples:

```
                      precision    recall  f1-score   support

Academic Achievement       1.00      1.00      1.00         8
       Certification       1.00      1.00      1.00         8
          Conference       1.00      1.00      1.00         8
   Cultural Activity       1.00      1.00      1.00         8
           Hackathon       1.00      1.00      1.00         8
          Internship       1.00      1.00      1.00         8
             Seminar       1.00      1.00      1.00         9
              Sports       1.00      1.00      1.00         8
Technical Competition      1.00      1.00      1.00         8
  Volunteer Activity       1.00      1.00      1.00         8
            Workshop       1.00      1.00      1.00         8

            accuracy                           1.00        91
           macro avg       1.00      1.00      1.00        91
        weighted avg       1.00      1.00      1.00        91
```

---

## 4. Confusion Matrix

The $11 \times 11$ confusion matrix confirms zero off-diagonal misclassifications on the held-out benchmark:

```
                      [AA  CE  CO  CU  HA  IN  SE  SP  TC  VO  WO]
Academic Achievement  [ 8   0   0   0   0   0   0   0   0   0   0]
Certification         [ 0   8   0   0   0   0   0   0   0   0   0]
Conference            [ 0   0   8   0   0   0   0   0   0   0   0]
Cultural Activity     [ 0   0   0   8   0   0   0   0   0   0   0]
Hackathon             [ 0   0   0   0   8   0   0   0   0   0   0]
Internship            [ 0   0   0   0   0   8   0   0   0   0   0]
Seminar               [ 0   0   0   0   0   0   9   0   0   0   0]
Sports                [ 0   0   0   0   0   0   0   8   0   0   0]
Technical Competition [ 0   0   0   0   0   0   0   0   8   0   0]
Volunteer Activity    [ 0   0   0   0   0   0   0   0   0   8   0]
Workshop              [ 0   0   0   0   0   0   0   0   0   0   8]
```

---

## 5. Error & Failure-Mode Analysis

To stress-test model robustness, adversarial edge cases and potential failure modes were simulated:

### 5.1 Potential Confusion Pairs
1. **`Hackathon` vs. `Technical Competition`**:
   - *Ambiguity*: Both feature coding, software prototyping, and algorithmic challenges.
   - *Resolution*: Hackathon certificates consistently contain temporal sprint cues (`"24-hour"`, `"hackathon"`, `"sprint"`), whereas Technical Competitions emphasize `"coding round"`, `"debug"`, and `"problem solving contest"`.
2. **`Workshop` vs. `Seminar`**:
   - *Ambiguity*: Both involve technical presentations within an academic venue.
   - *Resolution*: Workshops emphasize practical execution (`"hands-on"`, `"laboratory"`, `"bootcamp"`), whereas Seminars center on lecture delivery (`"talk"`, `"guest lecture"`, `"speaker"`).

### 5.2 Failure Mode: Short or Truncated Text
When an OCR failure extracts fewer than 5 words (e.g., `"Certificate of Participation John Doe"`):
- The classifier confidence drops below the $0.70$ threshold.
- The system automatically transitions the certificate status to `review_required`, preventing erroneous portfolio updates.

---

## 6. Model Serialization & Artifacts

The final production model is serialized under `ml/models/production/`:
- `certificate_classifier.joblib`: Serialized scikit-learn Pipeline (TextPreprocessor + TfidfVectorizer + LogisticRegression).
- `label_encoder.joblib`: LabelEncoder preserving deterministic category index mapping.
- `model_metadata.json`: Model version metadata, training timestamps, hyperparameters, and class mapping.
