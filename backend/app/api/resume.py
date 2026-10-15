"""
CertiNexus AI — Resume API

Compiles verified student portfolio data, certificates, and extracted skills
into structured resume formats for preview, customization, and export.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate, StudentSkill
from app.models.user import User
from app.schemas.schemas import CertificateResponse, SkillResponse, UserProfile

router = APIRouter()


class ResumeCustomization(BaseModel):
    template: str = "modern"
    title: Optional[str] = "Software Systems Student & Developer"
    summary: Optional[str] = None
    selected_certificate_ids: Optional[List[str]] = None
    selected_skills: Optional[List[str]] = None
    show_contact: bool = True
    show_education: bool = True
    show_certificates: bool = True
    show_skills: bool = True


class ResumeDataResponse(BaseModel):
    user: UserProfile
    headline: str
    summary: str
    contact_email: str
    institution: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[str] = None
    skills: List[SkillResponse]
    certificates: List[CertificateResponse]
    total_verified_certificates: int


@router.get("/data", response_model=ResumeDataResponse)
async def get_resume_data(
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Retrieve compiled profile, skill, and certificate data for resume generation."""
    certs = (
        db.query(Certificate)
        .filter(Certificate.user_id == user.id)
        .order_by(Certificate.issue_date.desc().nullslast(), Certificate.created_at.desc())
        .all()
    )

    skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.user_id == user.id)
        .order_by(StudentSkill.occurrence_count.desc(), StudentSkill.confidence.desc())
        .all()
    )

    headline = user.department or "Software Systems Student"
    summary = (
        user.bio
        or f"Motivated {user.department or 'Software Systems'} student at {user.institution or 'University'} with a verified portfolio of {len(certs)} academic and professional achievements."
    )

    verified_count = sum(1 for c in certs if c.is_reviewed or (c.ai_confidence_level == "high"))

    return ResumeDataResponse(
        user=UserProfile.model_validate(user),
        headline=headline,
        summary=summary,
        contact_email=user.email,
        institution=user.institution,
        department=user.department,
        graduation_year=user.graduation_year,
        skills=[SkillResponse.model_validate(s) for s in skills],
        certificates=[CertificateResponse.model_validate(c) for c in certs],
        total_verified_certificates=verified_count,
    )


@router.post("/generate")
async def generate_resume(
    customization: ResumeCustomization,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Generate structured resume payload formatted for the selected template."""
    query = db.query(Certificate).filter(Certificate.user_id == user.id)
    if customization.selected_certificate_ids:
        query = query.filter(Certificate.id.in_(customization.selected_certificate_ids))
    certs = query.order_by(Certificate.issue_date.desc().nullslast(), Certificate.created_at.desc()).all()

    skill_query = db.query(StudentSkill).filter(StudentSkill.user_id == user.id)
    if customization.selected_skills:
        skill_query = skill_query.filter(StudentSkill.skill_name.in_(customization.selected_skills))
    skills = skill_query.order_by(StudentSkill.occurrence_count.desc()).all()

    resume_sections = {
        "template": customization.template,
        "header": {
            "name": user.full_name or user.username,
            "title": customization.title,
            "email": user.email if customization.show_contact else None,
            "institution": user.institution if customization.show_education else None,
            "department": user.department if customization.show_education else None,
            "graduation_year": user.graduation_year if customization.show_education else None,
        },
        "summary": customization.summary or user.bio or "Dedicated software systems scholar.",
        "skills": [s.skill_name for s in skills] if customization.show_skills else [],
        "certificates": [
            {
                "id": c.id,
                "title": c.title or "Verified Certificate",
                "organization": c.organization,
                "category": c.category or c.ai_category,
                "issue_date": c.issue_date,
                "credential_id": c.certificate_id_extracted,
                "confidence": c.ai_confidence,
            }
            for c in certs
        ] if customization.show_certificates else [],
    }

    return {
        "status": "success",
        "resume": resume_sections,
    }


class SaveResumeToPortfolioRequest(BaseModel):
    title: Optional[str] = "FlowCV Professional Resume"
    headline: Optional[str] = None
    summary: Optional[str] = None
    template: str = "flow_modern"
    accent: Optional[str] = "indigo"
    skills: List[str] = []
    projects: Optional[List[Dict[str, Any]]] = None
    experience_bullets: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    contact_location: Optional[str] = None


@router.post("/save-to-portfolio")
async def save_resume_to_portfolio(
    payload: SaveResumeToPortfolioRequest,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Save the customized FlowCV resume as an accredited document in the user's digital portfolio."""
    import uuid
    from datetime import datetime

    cert_title = f"FlowCV Resume — {payload.headline or 'Professional CV'}"

    # Check if an existing FlowCV resume exists for this user to update, or create a new one
    existing_resume = (
        db.query(Certificate)
        .filter(Certificate.user_id == user.id, Certificate.document_type == "resume", Certificate.title.like("FlowCV Resume%"))
        .first()
    )

    if existing_resume:
        existing_resume.title = cert_title
        existing_resume.category = "Resume / CV"
        existing_resume.ai_category = "Resume / CV"
        existing_resume.ai_summary = payload.summary or "FlowCV ATS-Optimized Professional Resume"
        existing_resume.extracted_skills = payload.skills
        existing_resume.extraction_data = {
            "headline": payload.headline,
            "summary": payload.summary,
            "template": payload.template,
            "accent": payload.accent,
            "projects": payload.projects,
            "experience_bullets": payload.experience_bullets,
            "phone": payload.contact_phone,
            "location": payload.contact_location,
            "saved_at": datetime.utcnow().isoformat(),
        }
        existing_resume.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_resume)
        return {
            "status": "success",
            "message": "Updated FlowCV Resume in Digital Portfolio",
            "certificate_id": existing_resume.id,
            "title": existing_resume.title,
        }
    else:
        new_resume = Certificate(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=cert_title,
            recipient_name=user.full_name or user.username,
            organization="CertiNexus FlowCV Resume Studio",
            document_type="resume",
            category="Resume / CV",
            ai_category="Resume / CV",
            status="completed",
            ai_confidence=0.99,
            ai_confidence_level="high",
            ai_summary=payload.summary or "FlowCV ATS-Optimized Professional Resume",
            extracted_skills=payload.skills,
            is_reviewed=True,
            is_public=user.portfolio_public,
            created_at=datetime.utcnow(),
            extraction_data={
                "headline": payload.headline,
                "summary": payload.summary,
                "template": payload.template,
                "accent": payload.accent,
                "projects": payload.projects,
                "experience_bullets": payload.experience_bullets,
                "phone": payload.contact_phone,
                "location": payload.contact_location,
                "saved_at": datetime.utcnow().isoformat(),
            },
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        return {
            "status": "success",
            "message": "Added FlowCV Resume to Digital Portfolio",
            "certificate_id": new_resume.id,
            "title": new_resume.title,
        }

