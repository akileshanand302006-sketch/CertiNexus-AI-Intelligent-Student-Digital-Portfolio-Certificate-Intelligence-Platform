"""
CertiNexus AI — Certificate API

Handles upload, processing, CRUD, and AI classification.
"""

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate, ModelFeedback, StudentSkill
from app.models.user import User
from app.schemas.schemas import CertificateResponse, CertificateUpdate, ProcessingStatus

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = os.environ.get("STORAGE_PATH", "./storage/uploads")


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
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Create certificate record
    cert = Certificate(
        user_id=user.id,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        status="uploaded",
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    # Process synchronously for now (async worker would be better for production)
    _process_certificate(cert, db)

    return cert


def _process_certificate(cert: Certificate, db: Session):
    """Process a certificate through the AI pipeline."""
    import sys
    import time

    start_time = time.time()

    # Add project root to path for ML imports
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        # Step 1: OCR
        cert.status = "ocr_processing"
        db.commit()

        raw_text = _extract_text(cert.file_path, cert.file_type)
        cert.raw_ocr_text = raw_text

        # Step 2: Text preprocessing
        cert.status = "extracting"
        db.commit()

        from ml.preprocessing.text_preprocessor import CertificateTextPreprocessor
        preprocessor = CertificateTextPreprocessor()
        clean_text = preprocessor.transform([raw_text])[0]
        cert.clean_text = clean_text

        # Step 3: Classification
        cert.status = "classifying"
        db.commit()

        from ml.inference.predictor import CertificateClassifier
        classifier = CertificateClassifier(
            model_dir=os.path.join(project_root, "ml", "models", "production")
        )
        classifier.load()
        prediction = classifier.predict(clean_text)

        cert.ai_category = prediction["category"]
        cert.category = prediction["category"]
        cert.ai_confidence = prediction["confidence"]
        cert.ai_confidence_level = prediction["confidence_level"]
        cert.ai_important_terms = prediction.get("important_terms", [])
        cert.model_version = prediction.get("model_version", "unknown")

        # Step 4: Skill extraction (simple keyword-based)
        cert.status = "analyzing"
        db.commit()

        skills = _extract_skills(clean_text)
        cert.extracted_skills = skills

        # Update student skills
        for skill_name in skills:
            _update_student_skill(cert.user_id, skill_name, cert.id, db)

        # Complete
        processing_time = (time.time() - start_time) * 1000
        cert.processing_time_ms = processing_time
        cert.status = "completed" if prediction["confidence_level"] != "low" else "review_required"
        cert.ocr_engine = "text_extraction"
        db.commit()

    except Exception as e:
        cert.status = "failed"
        db.commit()
        print(f"Certificate processing failed: {e}")


def _extract_text(file_path: str, file_type: str) -> str:
    """Extract text from a certificate file."""
    try:
        if file_type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text.strip()
            except ImportError:
                return f"[PDF text extraction unavailable - file: {os.path.basename(file_path)}]"
        else:
            # Image OCR
            try:
                import easyocr
                reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                results = reader.readtext(file_path, detail=0)
                return ' '.join(results)
            except ImportError:
                # Fallback: return filename info
                return f"[OCR unavailable - image file: {os.path.basename(file_path)}]"
    except Exception as e:
        return f"[Text extraction error: {str(e)}]"


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
