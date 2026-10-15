"""
CertiNexus AI — Certificate API

Handles upload, processing, CRUD, and AI classification.
"""

import os
import sys
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import (
    Certificate,
    ExtractedEntity,
    ModelFeedback,
    OCRRegion,
    StudentSkill,
    UserCorrection,
)
from app.models.user import User
from app.schemas.schemas import (
    CertificateResponse,
    CertificateUpdate,
    CorrectionRequest,
    ExplanationResponse,
    ExtractionResponse,
    OCRDetailsResponse,
    ProcessingStatus,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.services.entity_extractor import extract_certificate_entities
from app.repositories import (
    CertificateRepository,
    OCRRepository,
    EntityRepository,
    ClassificationRepository,
    CorrectionRepository,
    ProcessingJobRepository,
    SkillRepository,
)

router = APIRouter()

cert_repo = CertificateRepository()
ocr_repo = OCRRepository()
entity_repo = EntityRepository()
classification_repo = ClassificationRepository()
correction_repo = CorrectionRepository()
job_repo = ProcessingJobRepository()
skill_repo = SkillRepository()

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = os.environ.get("STORAGE_PATH", os.path.join(PROJECT_ROOT, "backend", "storage", "uploads"))

_ocr_reader_cache = None


def _get_ocr_reader():
    global _ocr_reader_cache
    if _ocr_reader_cache is None:
        try:
            import easyocr
            _ocr_reader_cache = easyocr.Reader(['en'], gpu=False, verbose=False)
        except Exception as e:
            print(f"Could not initialize EasyOCR: {e}")
            return None
    return _ocr_reader_cache


@router.post("/upload", response_model=CertificateResponse)
async def upload_certificate(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Upload a certificate for AI processing."""
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    # Read file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename or "file")[1]
    file_id = str(uuid.uuid4())
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}"))

    with open(file_path, "wb") as f:
        f.write(content)

    # Create default title from original filename
    base_title = os.path.splitext(file.filename or "Certificate")[0]
    clean_title = base_title.replace('_', ' ').replace('-', ' ').title()

    # Create certificate record
    cert = Certificate(
        user_id=user.id,
        title=clean_title,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        status="uploaded",
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    # Initialize MongoDB Atlas record & processing job
    try:
        job_repo.create_job(cert.id)
        cert_repo.create({
            "_id": cert.id,
            "id": cert.id,
            "user_id": user.id,
            "title": clean_title,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_type": file.content_type,
            "file_size": len(content),
            "status": "uploaded",
        })
    except Exception as e:
        print(f"Notice: MongoDB Atlas initial cert persistence: {e}")

    # Process synchronously
    _process_certificate(cert, db)

    return cert


def _process_certificate(cert: Certificate, db: Session):
    """Process a certificate through the full ML/OCR intelligence pipeline and sync to MongoDB Atlas."""
    import time
    import traceback

    start_time = time.time()

    try:
        # Step 1: Preprocessing & OCR
        cert.status = "ocr_processing"
        db.commit()
        try:
            job_repo.update_stage(cert.id, "ocr")
        except Exception:
            pass

        raw_text, ocr_engine, regions_data, quality_data = _run_ocr_pipeline(cert.file_path, cert.file_type)
        cert.raw_ocr_text = raw_text
        cert.ocr_engine = ocr_engine
        cert.ocr_regions = regions_data
        cert.quality_score = quality_data
        db.commit()

        # Store OCRRegion rows in SQLite
        if regions_data:
            db.query(OCRRegion).filter(OCRRegion.certificate_id == cert.id).delete()
            for idx, r in enumerate(regions_data):
                reg = OCRRegion(
                    certificate_id=cert.id,
                    text=r.get("text", ""),
                    confidence=r.get("confidence", 1.0),
                    bbox=r.get("bbox", []),
                    order_index=idx,
                )
                db.add(reg)

        # Step 2: Information and Entity Extraction (Rule-based NER + Duplicate Detection)
        cert.status = "extracting"
        db.commit()
        try:
            job_repo.update_stage(cert.id, "ner")
        except Exception:
            pass

        # Text cleaning with postprocessor
        from ml.ocr.postprocessor import OCRPostProcessor
        postprocessor = OCRPostProcessor()
        postproc_result = postprocessor.process(raw_text)
        clean_text = postproc_result.cleaned_text or raw_text
        cert.clean_text = clean_text

        # Persist OCR results to MongoDB Atlas
        try:
            avg_conf = sum([float(r.get("confidence", 1.0)) for r in (regions_data or [])]) / max(len(regions_data or []), 1)
            ocr_repo.save_ocr_result({
                "certificate_id": cert.id,
                "detector": "CRAFT",
                "ocr_model": "CRNN-BiLSTM-CTC" if ocr_engine == "craft+crnn" else ocr_engine,
                "full_text": raw_text,
                "cleaned_text": clean_text,
                "average_confidence": avg_conf,
                "regions": regions_data or [],
                "quality_metrics": quality_data or {},
            })
        except Exception as e:
            print(f"Notice: MongoDB OCR persistence: {e}")

        # Duplicate detection hash
        try:
            from ml.extraction.duplicate_detector import DuplicateDetector
            dup = DuplicateDetector()
            cert.duplicate_hash = dup.compute_text_hash(clean_text)
        except Exception as e:
            print(f"Duplicate hash notice: {e}")

        # Rule-based NER extraction
        from ml.extraction.rule_ner import RuleBasedNER
        ner = RuleBasedNER()
        ner_result = ner.extract(clean_text)

        # Store ExtractedEntity rows in SQLite
        db.query(ExtractedEntity).filter(ExtractedEntity.certificate_id == cert.id).delete()
        for ent in ner_result.entities:
            ee = ExtractedEntity(
                certificate_id=cert.id,
                entity_type=ent.entity_type,
                text=ent.text,
                confidence=ent.confidence,
                source=ent.source,
                start_char=ent.start,
                end_char=ent.end,
                metadata_json=ent.metadata,
            )
            db.add(ee)

        # Persist Entities to MongoDB Atlas
        try:
            entity_repo.save_entities(cert.id, [e.to_dict() for e in ner_result.entities])
        except Exception as e:
            print(f"Notice: MongoDB entity persistence: {e}")

        # Legacy fallback entity extractor for summary & extra heuristics
        legacy_entities = extract_certificate_entities(raw_text, cert.original_filename or "")
        if legacy_entities.get("ai_summary"):
            cert.ai_summary = legacy_entities["ai_summary"]

        # Step 3: Document-Type Gatekeeper & Routing
        cert.status = "classifying"
        db.commit()
        try:
            job_repo.update_stage(cert.id, "classification")
        except Exception:
            pass

        from ml.classifiers.document_router import DocumentTypeRouter
        from ml.extraction.indian_doc_extractor import IndianDocumentExtractor

        router = DocumentTypeRouter()
        route_info = router.route(clean_text, cert.original_filename or "")
        cert.document_type = route_info["document_type"]

        if cert.document_type in [
            "aadhaar", "pan", "voter_id", "voter", "driving_licence", "vehicle_rc",
            "marksheet", "timetable", "fee_receipt", "passbook", "patta"
        ]:
            # Indian Identity / Academic / Financial Record
            extractor = IndianDocumentExtractor()
            extracted_result = extractor.extract(clean_text, cert.document_type, cert.original_filename or "", regions_data)
            fields = extracted_result.get("fields", {})

            cert.ai_category = route_info["label"]
            cert.category = route_info["label"]
            cert.ai_confidence = route_info["confidence"]
            cert.ai_confidence_level = "High" if route_info["confidence"] >= 0.8 else "Medium"
            cert.model_version = "IndianDocIntelligence-v1.0"
            cert.extraction_data = extracted_result
            cert.status = "completed" if not route_info["requires_review"] else "review_required"
            cert.is_reviewed = not route_info["requires_review"]

            # Map primary schema fields
            if fields.get("recipient_name"):
                cert.recipient_name = fields["recipient_name"]
            elif fields.get("voter_name"):
                cert.recipient_name = fields["voter_name"]
            elif fields.get("student_name"):
                cert.recipient_name = fields["student_name"]
            elif fields.get("owner_name"):
                cert.recipient_name = fields["owner_name"]
            elif fields.get("account_holder"):
                cert.recipient_name = fields["account_holder"]

            if fields.get("issuing_authority"):
                cert.organization = fields["issuing_authority"]
            elif fields.get("institution"):
                cert.organization = fields["institution"]
                cert.institution = fields["institution"]
            elif fields.get("bank_name"):
                cert.organization = fields["bank_name"]

            if fields.get("issue_date"):
                cert.issue_date = fields["issue_date"]
            elif fields.get("dob"):
                cert.issue_date = f"DOB: {fields['dob']}"
            elif fields.get("payment_date"):
                cert.issue_date = fields["payment_date"]

            cert.event = route_info["label"]
            cert.title = f"{route_info['label']} — {cert.recipient_name or 'Cardholder'}"
            cert.ai_summary = f"Indian {route_info['label']} successfully extracted with strict PII masking."

            prediction = {
                "category": route_info["label"],
                "confidence": route_info["confidence"],
                "confidence_level": cert.ai_confidence_level,
                "model": "IndianDocumentRouter",
                "model_version": "v1.0",
                "important_terms": [{"term": k, "weight": float(v), "importance_pct": min(100.0, float(v) * 15.0)} for k, v in route_info.get("scores", {}).items() if v > 0],
                "all_probabilities": [{"category": route_info["label"], "probability": route_info["confidence"]}],
            }
            cert.ai_important_terms = prediction["important_terms"]

        elif cert.document_type == "resume":
            # Resume / Curriculum Vitae
            extractor = IndianDocumentExtractor()
            extracted_result = extractor.extract(clean_text, "resume", cert.original_filename or "", regions_data)
            fields = extracted_result.get("fields", {})

            cert.ai_category = "Resume / CV"
            cert.category = "Resume / CV"
            cert.ai_confidence = route_info["confidence"]
            cert.ai_confidence_level = "High"
            cert.model_version = "DocumentTypeRouter-v1.0"
            cert.extraction_data = extracted_result
            cert.status = "completed"
            cert.is_reviewed = True

            if fields.get("candidate_name"):
                cert.recipient_name = fields["candidate_name"]
            cert.organization = "Candidate Resume / Curriculum Vitae"
            cert.event = "Student Portfolio & Skill Profile"
            cert.title = f"Resume — {cert.recipient_name or 'Candidate'}"
            cert.ai_summary = "Candidate Resume document profiling technical competencies, background, and skills."

            prediction = {
                "category": "Resume / CV",
                "confidence": route_info["confidence"],
                "confidence_level": "High",
                "model": "DocumentTypeRouter",
                "model_version": "v1.0",
                "important_terms": [{"term": "resume profile", "weight": 1.0, "importance_pct": 98.0}],
                "all_probabilities": [{"category": "Resume / CV", "probability": route_info["confidence"]}],
            }
            cert.ai_important_terms = prediction["important_terms"]

        else:
            # Genuine Certificate / Credential — Run 11-category classifier
            from ml.inference.predictor import CertificateClassifier
            model_dir = os.path.join(PROJECT_ROOT, "ml", "models", "production")
            classifier = CertificateClassifier(model_dir=model_dir)
            classifier.load()
            prediction = classifier.predict(clean_text)

            cert.document_type = "certificate"
            cert.ai_category = prediction["category"]
            cert.category = prediction["category"]
            cert.ai_confidence = prediction["confidence"]
            cert.ai_confidence_level = prediction["confidence_level"]
            cert.ai_important_terms = prediction.get("important_terms", [])
            cert.model_version = prediction.get("model_version", "unknown")

            if cert.ai_confidence < 0.40:
                cert.status = "review_required"
                cert.is_reviewed = False

        # Persist Classification & Predictions to MongoDB Atlas
        try:
            classification_repo.save_classification({
                "certificate_id": cert.id,
                "category": cert.category,
                "confidence": cert.ai_confidence,
                "confidence_level": cert.ai_confidence_level,
                "model_name": prediction.get("model", "LinearSVC"),
                "model_version": cert.model_version,
                "important_terms": cert.ai_important_terms,
                "all_probabilities": prediction.get("all_probabilities", []),
                "top_3_predictions": [p for p in prediction.get("all_probabilities", [])[:3]],
            })
        except Exception as e:
            print(f"Notice: MongoDB classification persistence: {e}")

        # Step 4: Category-specific field extraction (Only for accredited certificate categories)
        if cert.document_type == "certificate":
            try:
                job_repo.update_stage(cert.id, "metadata_extraction")
            except Exception:
                pass

            try:
                from ml.extraction.certificate_fields import CategoryFieldExtractor
                field_extractor = CategoryFieldExtractor()
                cat_fields = field_extractor.extract(clean_text, category=cert.category, ner_result=ner_result)
                cert.extraction_data = {
                    "structured_fields": cat_fields.to_dict(),
                    "completeness_score": cat_fields.completeness_score,
                    "entities": [e.to_dict() for e in ner_result.entities],
                }
                if cat_fields.holder_name:
                    cert.recipient_name = cat_fields.holder_name
                elif legacy_entities.get("recipient_name"):
                    cert.recipient_name = legacy_entities["recipient_name"]

                if cat_fields.issuing_organization:
                    cert.organization = cat_fields.issuing_organization
                elif legacy_entities.get("organization"):
                    cert.organization = legacy_entities["organization"]

                if cat_fields.issue_date:
                    cert.issue_date = cat_fields.issue_date
                elif legacy_entities.get("issue_date"):
                    cert.issue_date = legacy_entities["issue_date"]

                if cat_fields.certificate_id:
                    cert.certificate_id_extracted = cat_fields.certificate_id
                elif legacy_entities.get("certificate_id_extracted"):
                    cert.certificate_id_extracted = legacy_entities["certificate_id_extracted"]

                if cat_fields.duration:
                    cert.duration = cat_fields.duration
                elif legacy_entities.get("duration"):
                    cert.duration = legacy_entities["duration"]

                if cat_fields.event_name:
                    cert.event = cat_fields.event_name
                elif legacy_entities.get("event"):
                    cert.event = legacy_entities["event"]

            except Exception as e:
                print(f"Category extraction notice: {e}")
                cert.extraction_data = {
                    "structured_fields": {},
                    "completeness_score": 50.0,
                    "entities": [e.to_dict() for e in ner_result.entities],
                }

        # Build Explanation data
        pos_terms = [t for t in cert.ai_important_terms if t.get("weight", 0) > 0][:8]
        neg_terms = [t for t in cert.ai_important_terms if t.get("weight", 0) < 0][:5]
        all_probs = prediction.get("all_probabilities", [])
        alternatives = [p for p in all_probs if p.get("category") != cert.category][:3]
        cert.explanation_data = {
            "category": cert.category,
            "confidence": cert.ai_confidence,
            "confidence_level": cert.ai_confidence_level,
            "positive_terms": pos_terms,
            "negative_terms": neg_terms,
            "alternatives": alternatives,
            "explanation_text": f"Document classified as {cert.category} ({cert.ai_confidence:.1%} confidence). Key distinguishing terms: {', '.join([t['term'] for t in pos_terms[:3]]) if pos_terms else 'document context'}.",
            "model_version": cert.model_version,
        }

        # Refine certificate title with extracted metadata
        is_id_doc = cert.document_type in [
            "aadhaar", "voter_id", "voter", "pan", "driving_licence",
            "vehicle_rc", "passbook", "patta", "fee_receipt", "timetable", "resume"
        ]
        if not is_id_doc:
            if cert.event and cert.organization:
                cert.title = f"{cert.event} — {cert.organization}"
            elif cert.event:
                cert.title = f"{cert.event} Certificate"
            elif cert.organization:
                cert.title = f"{cert.category} at {cert.organization}"

        # Step 5: Skill extraction
        cert.status = "analyzing"
        db.commit()

        is_identity_or_admin = cert.document_type in [
            "aadhaar", "voter_id", "voter", "pan", "driving_licence",
            "vehicle_rc", "passbook", "patta", "fee_receipt", "timetable"
        ]

        if is_identity_or_admin:
            combined_skills = []
            cert.extracted_skills = []
        else:
            from ml.extraction.skills import SkillDatabase
            skill_db = SkillDatabase()
            db_skills = [s.text for s in skill_db.extract_skills(clean_text)]
            extracted_skills = legacy_entities.get("extracted_skills", [])
            combined_skills = list(dict.fromkeys(db_skills + extracted_skills))
            cert.extracted_skills = combined_skills

            # Update student skills in SQLite & MongoDB Atlas
            for skill_name in combined_skills:
                _update_student_skill(cert.user_id, skill_name, cert.id, db)
                try:
                    skill_repo.upsert_skill(cert.user_id, skill_name, cert.id)
                except Exception as e:
                    print(f"Notice: MongoDB skill persistence: {e}")

        # Complete
        processing_time = (time.time() - start_time) * 1000
        cert.processing_time_ms = processing_time
        cert.status = "completed" if prediction["confidence_level"] != "low" else "review_required"
        db.commit()

        # Update MongoDB Atlas certificate document & complete job
        try:
            job_repo.complete_job(cert.id)
            cert_repo.update(cert.id, {
                "title": cert.title,
                "category": cert.category,
                "recipient_name": cert.recipient_name,
                "organization": cert.organization,
                "institution": cert.institution,
                "event": cert.event,
                "issue_date": cert.issue_date,
                "duration": cert.duration,
                "certificate_id_extracted": cert.certificate_id_extracted,
                "achievement_level": cert.achievement_level,
                "ai_category": cert.ai_category,
                "ai_confidence": cert.ai_confidence,
                "ai_confidence_level": cert.ai_confidence_level,
                "ai_important_terms": cert.ai_important_terms,
                "status": cert.status,
                "processing_status": cert.status,
                "raw_ocr_text": cert.raw_ocr_text,
                "clean_text": cert.clean_text,
                "ocr_regions": cert.ocr_regions,
                "extracted_skills": cert.extracted_skills,
                "extraction_data": cert.extraction_data,
                "explanation_data": cert.explanation_data,
                "duplicate_hash": cert.duplicate_hash,
                "quality_score": cert.quality_score,
                "processing_time_ms": cert.processing_time_ms,
                "model_version": cert.model_version,
            })
        except Exception as e:
            print(f"Notice: MongoDB Atlas cert finalization: {e}")

    except Exception as e:
        traceback.print_exc()
        cert.status = "failed"
        db.commit()
        try:
            job_repo.fail_job(cert.id, str(e))
        except Exception:
            pass
        print(f"Certificate processing failed: {e}")
        print(f"Certificate processing failed: {e}")


def _run_ocr_pipeline(file_path: str, file_type: str):
    """
    Run OCR pipeline on certificate/document file.
    Supports scanned raster PDFs, bilingual Indian documents, and standard images.
    Returns (text, engine, regions, quality_metrics).
    """
    # Resolve relative path if needed
    if not os.path.exists(file_path):
        fname = os.path.basename(file_path)
        for base in [
            UPLOAD_DIR,
            os.path.join(PROJECT_ROOT, "storage", "uploads"),
            os.path.join(PROJECT_ROOT, "backend", "storage", "uploads"),
            PROJECT_ROOT,
            os.path.join(PROJECT_ROOT, "backend"),
        ]:
            cand = os.path.join(base, fname)
            if os.path.exists(cand):
                file_path = cand
                break

    try:
        if file_type == "application/pdf" or file_path.lower().endswith(".pdf"):
            try:
                import fitz
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()

                # If the PDF is a scanned/raster document (e.g., e-Aadhaar or scan with no text stream)
                if len(text.strip()) < 20:
                    page_texts = []
                    all_regions = []
                    reader = _get_ocr_reader()
                    import numpy as np
                    import cv2

                    for page_idx, page in enumerate(doc):
                        pix = page.get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("png")
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if reader is not None and img is not None:
                            results = reader.readtext(img, detail=1)
                            p_text = " ".join([r[1] for r in results]).strip()
                            if p_text:
                                page_texts.append(p_text)
                            for r in results:
                                all_regions.append({
                                    "text": str(r[1]),
                                    "confidence": float(r[2]),
                                    "bbox": [[int(coord) for coord in pt] for pt in r[0]],
                                    "page": page_idx + 1,
                                })

                    doc.close()
                    combined_text = "\n\n".join(page_texts).strip()
                    quality_score = 88.0 if len(combined_text) > 50 else 60.0
                    return combined_text, "easyocr-raster-pdf", all_regions, {"overall_quality": quality_score, "type": "scanned_pdf"}

                doc.close()
                return text.strip(), "pymupdf", [], {"overall_quality": 95.0, "type": "pdf"}
            except Exception as e:
                print(f"PDF extraction error: {e}")
                return f"[PDF extraction notice: {os.path.basename(file_path)}]", "fallback", [], None
        else:
            # Image OCR via EasyOCR
            reader = _get_ocr_reader()
            if reader is not None and os.path.exists(file_path):
                results = reader.readtext(file_path, detail=1)
                lines_text = []
                regions = []
                for r in results:
                    text_str = str(r[1]).strip()
                    conf = float(r[2])
                    if text_str:
                        lines_text.append(text_str)
                        regions.append({
                            "text": text_str,
                            "confidence": conf,
                            "bbox": [[int(coord) for coord in pt] for pt in r[0]],
                        })
                full_text = "\n".join(lines_text).strip()
                avg_conf = sum([r["confidence"] for r in regions]) / max(len(regions), 1)
                quality = {"overall_quality": round(avg_conf * 100, 1), "regions_count": len(regions)}
                return full_text, "easyocr", regions, quality

            return f"[Image document: {os.path.basename(file_path)}]", "fallback", [], None
    except Exception as e:
        print(f"Text extraction error: {e}")
        return f"[Text extraction error: {str(e)}]", "error", [], None


def _extract_skills(text: str) -> list:
    """Extract skills from certificate text using keyword matching."""
    SKILL_KEYWORDS = {
        "python": "Python", "java": "Java", "javascript": "JavaScript",
        "react": "React", "angular": "Angular", "node.js": "Node.js",
        "machine learning": "Machine Learning", "deep learning": "Deep Learning",
        "artificial intelligence": "Artificial Intelligence", "ai": "AI",
        "data science": "Data Science", "sql": "SQL", "nosql": "NoSQL",
        "cloud computing": "Cloud Computing", "aws": "AWS", "azure": "Azure",
        "docker": "Docker", "kubernetes": "Kubernetes", "devops": "DevOps",
        "cybersecurity": "Cybersecurity", "blockchain": "Blockchain",
        "flutter": "Flutter", "swift": "Swift", "kotlin": "Kotlin",
        "html": "HTML", "css": "CSS", "git": "Git",
        "agile": "Agile", "scrum": "Scrum", "project management": "Project Management",
        "leadership": "Leadership", "teamwork": "Teamwork",
        "communication": "Communication", "problem solving": "Problem Solving",
        "web development": "Web Development", "mobile development": "Mobile Development",
        "database": "Database", "networking": "Networking",
        "tensorflow": "TensorFlow", "pytorch": "PyTorch",
        "natural language processing": "NLP", "computer vision": "Computer Vision",
        "data analytics": "Data Analytics", "big data": "Big Data",
        "iot": "IoT", "internet of things": "IoT",
    }

    text_lower = text.lower()
    found_skills = []
    for keyword, skill_name in SKILL_KEYWORDS.items():
        if keyword in text_lower:
            if skill_name not in found_skills:
                found_skills.append(skill_name)

    return found_skills


def _update_student_skill(user_id: str, skill_name: str, cert_id: str, db: Session):
    """Update or create a student skill record."""
    existing = db.query(StudentSkill).filter(
        StudentSkill.user_id == user_id,
        StudentSkill.skill_name == skill_name,
    ).first()

    if existing:
        existing.occurrence_count += 1
        existing.last_detected = datetime.utcnow()
    else:
        skill = StudentSkill(
            user_id=user_id,
            skill_name=skill_name,
            source_certificate_id=cert_id,
        )
        db.add(skill)


@router.get("", response_model=list[CertificateResponse])
async def list_certificates(
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """List all certificates for the current user."""
    certs = db.query(Certificate).filter(
        Certificate.user_id == user.id
    ).order_by(Certificate.created_at.desc()).all()
    return certs


@router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get a specific certificate."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")
    return cert


@router.patch("/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: str,
    data: CertificateUpdate,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Update certificate details (human-in-the-loop correction)."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    update_data = data.model_dump(exclude_unset=True)

    # Track category corrections for human-in-the-loop
    if "category" in update_data and update_data["category"] != cert.ai_category:
        feedback = ModelFeedback(
            certificate_id=cert.id,
            original_prediction=cert.ai_category,
            original_confidence=cert.ai_confidence,
            corrected_label=update_data["category"],
            model_version=cert.model_version,
        )
        db.add(feedback)
        cert.is_correction = True

    for field, value in update_data.items():
        setattr(cert, field, value)

    db.commit()
    db.refresh(cert)

    # Sync to MongoDB Atlas
    try:
        cert_repo.update(cert.id, update_data)
    except Exception as e:
        print(f"Notice: MongoDB cert update: {e}")

    return cert


@router.delete("/{certificate_id}")
async def delete_certificate(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Delete a certificate."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    # Delete file
    if cert.file_path and os.path.exists(cert.file_path):
        os.remove(cert.file_path)

    db.delete(cert)
    db.commit()

    # Cascade delete in MongoDB Atlas
    try:
        cert_repo.delete(cert.id)
        ocr_repo.delete_by_certificate_id(cert.id)
        entity_repo.delete_by_certificate_id(cert.id)
        classification_repo.delete_by_certificate_id(cert.id)
    except Exception as e:
        print(f"Notice: MongoDB cert cascade delete: {e}")

    return {"status": "deleted"}


@router.get("/{certificate_id}/processing-status", response_model=ProcessingStatus)
async def get_processing_status(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get the processing status of a certificate."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    # Check MongoDB Atlas processing job record
    try:
        job = job_repo.get_by_certificate_id(certificate_id)
        if job:
            return ProcessingStatus(
                certificate_id=cert.id,
                status=job.get("status", cert.status),
                progress=int(job.get("progress", 0)),
                message=f"Stage: {job.get('current_stage', cert.status)} ({job.get('status', 'running')})",
            )
    except Exception:
        pass

    progress_map = {
        "uploaded": 10, "ocr_processing": 30, "extracting": 50,
        "classifying": 70, "analyzing": 85, "completed": 100,
        "failed": 0, "review_required": 100,
    }
    message_map = {
        "uploaded": "Document uploaded",
        "ocr_processing": "Extracting text via OCR...",
        "extracting": "Extracting information...",
        "classifying": "AI classification in progress...",
        "analyzing": "Analyzing skills and content...",
        "completed": "Processing complete",
        "failed": "Processing failed",
        "review_required": "Low confidence — manual review required",
    }

    return ProcessingStatus(
        certificate_id=cert.id,
        status=cert.status,
        progress=progress_map.get(cert.status, 0),
        message=message_map.get(cert.status, "Unknown status"),
    )


@router.get("/{certificate_id}/file")
async def get_certificate_file(
    certificate_id: str,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Serve the raw certificate file (image or PDF) for browser preview with inline disposition."""
    import mimetypes
    from app.api.auth import verify_token
    
    raw_token = token
    if not raw_token and authorization and authorization.startswith("Bearer "):
        raw_token = authorization[7:]

    if not raw_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = verify_token(raw_token)
    user_id = payload.get("sub")

    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user_id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    file_path = cert.file_path
    if not file_path or not os.path.exists(file_path):
        fname = os.path.basename(cert.file_path or "")
        search_dirs = [
            os.path.join(PROJECT_ROOT, "storage", "uploads"),
            os.path.join(PROJECT_ROOT, "backend", "storage", "uploads"),
            os.path.join(PROJECT_ROOT, "storage"),
            os.path.join(PROJECT_ROOT, "backend", "storage"),
        ]
        for s_dir in search_dirs:
            candidate = os.path.join(s_dir, fname)
            if os.path.exists(candidate):
                file_path = candidate
                # Self-heal path in database
                cert.file_path = file_path
                try:
                    db.commit()
                except Exception:
                    pass
                break

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(404, "Certificate file not found on disk")

    # Determine accurate media type
    media_type = cert.file_type
    if not media_type or media_type == "application/octet-stream":
        inferred, _ = mimetypes.guess_type(file_path)
        media_type = inferred or "application/pdf"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        content_disposition_type="inline",
        filename=cert.original_filename or f"certificate-{cert.id}",
    )


@router.post("/{certificate_id}/confirm", response_model=CertificateResponse)
async def confirm_certificate(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Human-in-the-loop: Confirm and approve AI classification."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    cert.status = "completed"
    cert.is_reviewed = True
    db.commit()
    db.refresh(cert)
    return cert


@router.post("/{certificate_id}/reprocess", response_model=CertificateResponse)
async def reprocess_certificate(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Reprocess an existing certificate through the complete ML/OCR intelligence pipeline."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    _process_certificate(cert, db)
    db.refresh(cert)
    return cert


@router.get("/{certificate_id}/extraction", response_model=ExtractionResponse)
async def get_certificate_extraction(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get rich entity extraction and category-specific fields for a certificate."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    ext_data = cert.extraction_data or {}
    entities = ext_data.get("entities", [])
    if not entities and cert.entities:
        entities = [
            {
                "type": e.entity_type,
                "text": e.text,
                "confidence": e.confidence,
                "source": e.source,
                "start": e.start_char,
                "end": e.end_char,
            }
            for e in cert.entities
        ]

    return ExtractionResponse(
        certificate_id=cert.id,
        category=cert.category,
        completeness_score=ext_data.get("completeness_score", 0.0),
        entities=entities,
        structured_fields=ext_data.get("structured_fields", {}),
        skills=cert.extracted_skills or [],
    )


@router.get("/{certificate_id}/explanation", response_model=ExplanationResponse)
async def get_certificate_explanation(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get ML explanation and feature attribution for the classification decision."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    exp_data = cert.explanation_data or {}
    return ExplanationResponse(
        certificate_id=cert.id,
        category=cert.category or cert.ai_category or "Unclassified",
        confidence=cert.ai_confidence or 0.0,
        confidence_level=cert.ai_confidence_level or "medium",
        positive_terms=exp_data.get("positive_terms", []),
        negative_terms=exp_data.get("negative_terms", []),
        alternatives=exp_data.get("alternatives", []),
        explanation_text=exp_data.get("explanation_text", f"Classified as {cert.category}"),
        model_version=cert.model_version or "1.0",
    )


@router.get("/{certificate_id}/ocr", response_model=OCRDetailsResponse)
async def get_certificate_ocr(
    certificate_id: str,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get detailed OCR output including bounding regions, raw text, and quality score."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    regions = cert.ocr_regions or []
    if not regions and cert.regions:
        regions = [
            {
                "text": r.text,
                "confidence": r.confidence,
                "bbox": r.bbox,
                "order_index": r.order_index,
            }
            for r in cert.regions
        ]

    return OCRDetailsResponse(
        certificate_id=cert.id,
        ocr_engine=cert.ocr_engine or "easyocr",
        raw_text=cert.raw_ocr_text or "",
        clean_text=cert.clean_text or "",
        regions=regions,
        quality_score=cert.quality_score,
        num_regions=len(regions),
    )


@router.post("/{certificate_id}/correct", response_model=CertificateResponse)
async def correct_certificate_field(
    certificate_id: str,
    req: CorrectionRequest,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Record a human-in-the-loop field correction and update the certificate."""
    cert = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.user_id == user.id,
    ).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    orig_val = getattr(cert, req.field_name, None)

    correction = UserCorrection(
        certificate_id=cert.id,
        user_id=user.id,
        field_name=req.field_name,
        original_value=str(orig_val) if orig_val is not None else "",
        corrected_value=req.corrected_value,
    )
    db.add(correction)

    if hasattr(cert, req.field_name):
        setattr(cert, req.field_name, req.corrected_value)

    if req.field_name == "category":
        cert.is_correction = True

    cert.is_reviewed = True
    db.commit()
    db.refresh(cert)

    # Sync to MongoDB Atlas user_corrections and certificates collections
    try:
        correction_repo.save_correction({
            "certificate_id": cert.id,
            "user_id": user.id,
            "field_name": req.field_name,
            "original_value": str(orig_val) if orig_val is not None else "",
            "corrected_value": req.corrected_value,
            "corrected_by": user.id,
        })
        cert_repo.update(cert.id, {
            req.field_name: req.corrected_value,
            "is_reviewed": True,
            "is_correction": cert.is_correction,
        })
    except Exception as e:
        print(f"Notice: MongoDB correction sync: {e}")

    return cert

