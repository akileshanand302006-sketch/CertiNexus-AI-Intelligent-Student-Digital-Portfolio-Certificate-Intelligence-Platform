# CertiNexus AI — User Stories & ML Task Mapping

**Course**: 20MSSL12 Machine Learning Lab  
**Application**: CertiNexus AI Student Portfolio & Certificate Intelligence  

---

## User Story 1: Automated Certificate Ingestion & Multi-Class Classification

### 1.1 Story Statement
> **As a** computer science student preparing for campus recruitment,  
> **I want to** upload a PDF or image of my hackathon or workshop certificate,  
> **So that** the platform automatically classifies the certificate into the correct achievement domain without requiring me to manually fill out tedious metadata forms.

### 1.2 Associated ML Task
- **Core Task**: Supervised multi-class natural language text classification ($|\mathcal{C}| = 11$).
- **Subtask**: OCR text extraction and text normalization via `CertificateTextPreprocessor`.

### 1.3 Acceptance Criteria
1. **Scenario 1 (Successful Upload & High-Confidence Classification)**:
   - **Given** a student is logged into the CertiNexus web portal,
   - **When** the student uploads a certificate document containing text indicating a hackathon achievement,
   - **Then** the platform extracts the text via OCR within 2 seconds,
   - **And** the classifier assigns the category `"Hackathon"` with confidence $\ge 0.85$,
   - **And** the UI displays the predicted category, confidence badge, and the top-contributing terms (e.g., `"hackathon"`, `"sprint"`, `"prototype"`).
2. **Scenario 2 (Corrupted or Unreadable Document)**:
   - **Given** an uploaded image that contains illegible or blurry text,
   - **When** OCR text extraction produces fewer than 3 tokens,
   - **Then** the system tags the document status as `"review_required"`,
   - **And** prompts the student to manually provide the title and category while preserving the file.

---

## User Story 2: Automatic Technical Skill Discovery & Portfolio Aggregation

### 2.1 Story Statement
> **As a** student building an academic portfolio,  
> **I want** the system to automatically identify technical and soft skills mentioned in my certificates (e.g., "Python", "Deep Learning", "React", "Docker"),  
> **So that** my student skills graph is automatically populated with evidence-backed proficiencies.

### 2.2 Associated ML Task
- **Core Task**: Named Entity Recognition (NER) and lexicon-based domain skill extraction.
- **Subtask**: Frequency aggregation and proficiency confidence updating.

### 2.3 Acceptance Criteria
1. **Scenario 1 (Skill Detection & Count Increment)**:
   - **Given** a certificate whose text mentions `"successfully completed Machine Learning and Python bootcamp"`,
   - **When** the document processing completes,
   - **Then** the student's skills database adds or updates `"Python"` and `"Machine Learning"`,
   - **And** increments their occurrence count and associates the source certificate ID.
2. **Scenario 2 (Skills View)**:
   - **Given** detected skills in the database,
   - **When** the student visits `/skills`,
   - **Then** skills are displayed with occurrence counts, verification source tags, and filtering options.

---

## User Story 3: Human-in-the-Loop Feedback & Uncertainty Triaging

### 3.1 Story Statement
> **As a** student whose certificate contains ambiguous domain text,  
> **I want** to easily review and correct any ML category prediction,  
> **So that** my portfolio remains 100% accurate and my corrections train future model iterations.

### 3.2 Associated ML Task
- **Core Task**: Active learning supervisory data capture and confidence threshold routing.

### 3.3 Acceptance Criteria
1. **Scenario 1 (Student Corrects Prediction)**:
   - **Given** a certificate predicted as `"Technical Competition"` that was actually an `"Academic Achievement"`,
   - **When** the student changes the category dropdown on `/certificates/:id` and saves,
   - **Then** the certificate's category updates immediately,
   - **And** a record is created in the `model_feedback` table recording the original prediction, confidence, corrected label, and timestamp.
2. **Scenario 2 (Low Confidence Notification)**:
   - **Given** a model prediction with confidence $< 0.70$,
   - **When** processing completes,
   - **Then** the certificate is marked with an amber `"Review Required"` badge in the dashboard.

---

## User Story 4: Public Verified Digital Portfolio Sharing

### 3.1 Story Statement
> **As a** job-seeking graduate,  
> **I want to** share a public, themeable web link (`/portfolio/{username}`) with prospective employers,  
> **So that** recruiters can independently inspect my verified credentials, skills, and achievement timeline.

### 4.2 Associated ML Task
- **Core Task**: Structured aggregation of high-confidence predictions and verified achievement metrics.

### 4.3 Acceptance Criteria
1. **Scenario 1 (Public View Accessibility)**:
   - **Given** a user who enabled `"Public Portfolio"` in their settings,
   - **When** an unauthenticated recruiter visits `/portfolio/john_doe`,
   - **Then** the page renders the candidate's bio, university, verified skill badges, and public certificates without prompting for login.
2. **Scenario 2 (Private Portfolio Protection)**:
   - **Given** a user with `"portfolio_public": false`,
   - **When** an external visitor navigates to their portfolio link,
   - **Then** a 403 Forbidden / "This portfolio is private" notification is rendered.

---

## User Story 5: Verified ATS-Optimized Resume Generation & Export

### 5.1 Story Statement
> **As an** engineering applicant applying to tech companies,  
> **I want to** generate an ATS-compatible resume sourced strictly from my verified certificates,  
> **So that** I can print or export a clean, publication-grade resume PDF where every claimed skill and certification is backed by verified data.

### 5.2 Associated ML Task
- **Core Task**: Data structuring, verification filtering ($p \ge 0.85$ or human-reviewed), and ATS formatting.

### 5.3 Acceptance Criteria
1. **Scenario 1 (Resume Customization & Live Preview)**:
   - **Given** a student on the `/resume` page,
   - **When** selecting between templates (Modern Tech, Academic CV, Minimalist, Executive),
   - **Then** the live A4 preview immediately re-renders with the selected typography and layout.
2. **Scenario 2 (Print / PDF Export)**:
   - **Given** the resume preview,
   - **When** the student clicks `"Print / Save as PDF"`,
   - **Then** the browser print dialogue triggers, and the injected print CSS strips all web chrome/sidebars, producing a clean, single-page resume sheet.
