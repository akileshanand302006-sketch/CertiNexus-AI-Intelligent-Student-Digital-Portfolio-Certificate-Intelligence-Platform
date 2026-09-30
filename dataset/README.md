# CertiNexus AI — Dataset Documentation

## Data Card

### Overview
| Field | Value |
|-------|-------|
| **Name** | CertiNexus Certificate Text Classification Dataset |
| **Version** | 1.0 |
| **Task** | Multi-class text classification |
| **Size** | ~600 samples |
| **Categories** | 11 achievement types |
| **Format** | CSV |
| **Language** | English |

### Source & Collection Method
This dataset is **synthetically generated** specifically for this research project. Certificate text samples were created using:

1. **Template-based generation**: Multiple realistic certificate text templates per category, with variable substitution for names, organizations, events, dates, and achievements.
2. **Vocabulary variation**: Different phrasings, formats, and organizational styles to ensure lexical diversity.
3. **OCR noise simulation**: Configurable character-level noise to simulate real OCR artifacts (character swaps, deletions, extra spaces).

No real student certificates or personal data were used in dataset creation.

### License
This dataset is created by the project authors for academic research purposes. It is available under **CC BY-SA 4.0** for educational use.

### Categories
| Category | Description | Target Samples |
|----------|-------------|----------------|
| Academic Achievement | Grades, honors, dean's list, academic awards | ~55 |
| Certification | Professional/technical certifications | ~55 |
| Internship | Industry internship completion | ~55 |
| Workshop | Workshop participation/completion | ~55 |
| Hackathon | Hackathon participation/winning | ~55 |
| Technical Competition | Coding contests, tech competitions | ~55 |
| Seminar | Seminar/guest lecture attendance | ~55 |
| Conference | Conference attendance/presentation | ~55 |
| Sports | Sports achievements and participation | ~55 |
| Cultural Activity | Arts, music, dance, drama events | ~55 |
| Volunteer Activity | Social service, volunteering, NSS/NCC | ~55 |

### Schema
| Column | Type | Description |
|--------|------|-------------|
| document_id | string | Unique identifier |
| raw_text | string | Simulated OCR-extracted text |
| clean_text | string | Preprocessed clean text |
| certificate_title | string | Certificate title |
| organization | string | Issuing organization |
| event | string | Event name |
| date | string | Issue date |
| category | string | Achievement category (target label) |
| source | string | Data source identifier |

### Ethics & Privacy
- **No real student data**: All samples are synthetically generated
- **No PII**: Names used are fictional or common placeholders
- **Research purpose**: Created exclusively for ML classification research
- **Anonymization**: Not applicable (no real data to anonymize)
- **Consent**: Not applicable (synthetic data)

### Known Limitations
1. Synthetic text may not capture the full diversity of real certificate language
2. OCR noise simulation is approximate; real OCR errors have document-specific patterns
3. Category boundaries may overlap (e.g., "Technical Competition" vs "Hackathon")
4. English-only; does not cover multilingual certificates
5. Template-based generation may introduce patterns that don't exist in real certificates

### Preprocessing
See `ml/preprocessing/text_preprocessor.py` for the full preprocessing pipeline.
