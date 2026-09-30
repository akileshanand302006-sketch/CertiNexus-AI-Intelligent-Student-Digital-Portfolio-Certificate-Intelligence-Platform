"""
CertiNexus AI — Certificate API

Handles upload, processing, CRUD, and AI classification.
"""

import os
import sys
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate, ModelFeedback, StudentSkill
from app.models.user import User
from app.schemas.schemas import CertificateResponse, CertificateUpdate, ProcessingStatus

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.services.entity_extractor import extract_certificate_entities

router = APIRouter()

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

    # Process synchronously
    _process_certificate(cert, db)

    return cert


def _process_certificate(cert: Certificate, db: Session):
    """Process a certificate through the AI pipeline."""
    import time
    import traceback

    start_time = time.time()

    try:
        # Step 1: OCR
        cert.status = "ocr_processing"
        db.commit()

        raw_text, ocr_engine = _extract_text(cert.file_path, cert.file_type)
        cert.raw_ocr_text = raw_text
        cert.ocr_engine = ocr_engine

        # Step 2: Information and Entity Extraction
        cert.status = "extracting"
        db.commit()

        entities = extract_certificate_entities(raw_text, cert.original_filename or "")
        if entities.get("recipient_name"):
            cert.recipient_name = entities["recipient_name"]
        if entities.get("organization"):
            cert.organization = entities["organization"]
        if entities.get("institution"):
            cert.institution = entities["institution"]
        if entities.get("event"):
            cert.event = entities["event"]
        if entities.get("issue_date"):
            cert.issue_date = entities["issue_date"]
        if entities.get("duration"):
            cert.duration = entities["duration"]
        if entities.get("certificate_id_extracted"):
            cert.certificate_id_extracted = entities["certificate_id_extracted"]
        if entities.get("ai_summary"):
            cert.ai_summary = entities["ai_summary"]

        from ml.preprocessing.text_preprocessor import CertificateTextPreprocessor
        preprocessor = CertificateTextPreprocessor()
        clean_text = preprocessor.transform([raw_text])[0]
        cert.clean_text = clean_text

        # Step 3: Classification
        cert.status = "classifying"
        db.commit()

        from ml.inference.predictor import CertificateClassifier
        model_dir = os.path.join(PROJECT_ROOT, "ml", "models", "production")
        classifier = CertificateClassifier(model_dir=model_dir)
        classifier.load()
        prediction = classifier.predict(clean_text)

        cert.ai_category = prediction["category"]
        cert.category = prediction["category"]
        cert.ai_confidence = prediction["confidence"]
        cert.ai_confidence_level = prediction["confidence_level"]
        cert.ai_important_terms = prediction.get("important_terms", [])
        cert.model_version = prediction.get("model_version", "unknown")

        # Refine certificate title with extracted metadata
        if entities.get("event") and entities.get("organization"):
            cert.title = f"{entities['event']} — {entities['organization']}"
        elif entities.get("event"):
            cert.title = f"{entities['event']} Certificate"
        elif entities.get("organization"):
            cert.title = f"{cert.category} at {entities['organization']}"

        # Step 4: Skill extraction
        cert.status = "analyzing"
        db.commit()

        basic_skills = _extract_skills(clean_text)
        extracted_skills = entities.get("extracted_skills", [])
        combined_skills = list(dict.fromkeys(extracted_skills + basic_skills))
        cert.extracted_skills = combined_skills

        # Update student skills
        for skill_name in combined_skills:
            _update_student_skill(cert.user_id, skill_name, cert.id, db)

        # Complete
        processing_time = (time.time() - start_time) * 1000
        cert.processing_time_ms = processing_time
        cert.status = "completed" if prediction["confidence_level"] != "low" else "review_required"
        db.commit()

    except Exception as e:
        traceback.print_exc()
        cert.status = "failed"
        db.commit()
        print(f"Certificate processing failed: {e}")


def _extract_text(file_path: str, file_type: str) -> tuple[str, str]:
    """Extract text from a certificate file. Returns (text, engine_name)."""
    # Resolve relative path if needed
    if not os.path.exists(file_path):
        for base in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
            cand = os.path.join(base, file_path.lstrip("./\\"))
            if os.path.exists(cand):
                file_path = cand
                break

    try:
        if file_type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text.strip(), "pymupdf"
            except ImportError:
                return f"[PDF text extraction unavailable - file: {os.path.basename(file_path)}]", "none"
        else:
            # Image OCR
            reader = _get_ocr_reader()
            if reader is not None:
                results = reader.readtext(file_path, detail=0)
                text = ' '.join(results).strip()
                if text:
                    return text, "easyocr"
            return f"[Image certificate: {os.path.basename(file_path)}]", "fallback"
    except Exception as e:
        print(f"Text extraction error: {e}")
        return f"[Text extraction error: {str(e)}]", "error"


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
    """Serve the raw certificate file (image or PDF) for browser preview."""
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
        # Fallback to check relative paths
        for base in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "backend")]:
            cand = os.path.join(base, (cert.file_path or "").lstrip("./\\"))
            if os.path.exists(cand):
                file_path = cand
                break

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(404, "Certificate file not found on disk")

    return FileResponse(
        path=file_path,
        media_type=cert.file_type or "application/octet-stream",
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
