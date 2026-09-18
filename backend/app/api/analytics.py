"""
CertiNexus AI — Analytics API
"""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate, StudentSkill
from app.models.user import User
from app.schemas.schemas import AnalyticsResponse, CertificateResponse

router = APIRouter()


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get analytics dashboard data."""
    certs = db.query(Certificate).filter(Certificate.user_id == user.id).all()
    skills = db.query(StudentSkill).filter(StudentSkill.user_id == user.id).all()

    # Category distribution
    cat_dist = Counter(c.category for c in certs if c.category)

    # Skills distribution
    skill_dist = Counter(s.skill_name for s in skills)

    # Monthly activity
    monthly = Counter()
    for c in certs:
        if c.created_at:
            key = c.created_at.strftime("%Y-%m")
            monthly[key] += 1

    # Recent certificates
    recent = sorted(certs, key=lambda x: x.created_at or "", reverse=True)[:5]

    # Portfolio completeness
    completeness = _calculate_completeness(user, certs, skills)

    return AnalyticsResponse(
        total_certificates=len(certs),
        total_skills=len(skills),
        total_categories=len(cat_dist),
        category_distribution=dict(cat_dist),
        skills_distribution=dict(skill_dist.most_common(20)),
        recent_certificates=[CertificateResponse.model_validate(c) for c in recent],
        monthly_activity=dict(sorted(monthly.items())),
        portfolio_completeness=completeness,
    )


def _calculate_completeness(user: User, certs: list, skills: list) -> float:
    """Calculate portfolio completeness score."""
    score = 0
    total = 7

    if user.full_name:
        score += 1
    if user.bio:
        score += 1
    if user.institution:
        score += 1
    if user.department:
        score += 1
    if len(certs) >= 1:
        score += 1
    if len(certs) >= 5:
        score += 1
    if len(skills) >= 3:
        score += 1

    return round(score / total * 100, 1)
