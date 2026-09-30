"""
CertiNexus AI — Portfolio API
"""

from collections import Counter
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate, StudentSkill
from app.models.user import User
from app.schemas.schemas import CertificateResponse, PortfolioResponse, SkillResponse, UserProfile

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Get current user's portfolio data."""
    return _build_portfolio(user, db)


@router.patch("")
async def update_portfolio(
    settings: Dict[str, Any],
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Update portfolio settings."""
    allowed = {"portfolio_public", "portfolio_theme"}
    for key, value in settings.items():
        if key in allowed:
            setattr(user, key, value)
    db.commit()
    return {"status": "updated"}


@router.get("/public/{username}", response_model=PortfolioResponse)
async def get_public_portfolio(username: str, db: Session = Depends(get_db)):
    """Get a user's public portfolio by username."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(404, "Portfolio not found")
    if not user.portfolio_public:
        raise HTTPException(403, "This portfolio is private")
    return _build_portfolio(user, db, public_only=True)


def _build_portfolio(user: User, db: Session, public_only: bool = False) -> PortfolioResponse:
    """Build portfolio data for a user."""
    query = db.query(Certificate).filter(Certificate.user_id == user.id)
    if public_only:
        query = query.filter(Certificate.is_public == True)
    certs = query.order_by(Certificate.created_at.desc()).all()

    skills = db.query(StudentSkill).filter(
        StudentSkill.user_id == user.id
    ).all()

    # Category distribution
    cat_dist = Counter(c.category for c in certs if c.category)

    # Timeline
    timeline = []
    for c in certs:
        if c.issue_date or c.created_at:
            timeline.append({
                "date": c.issue_date or (c.created_at.isoformat() if c.created_at else ""),
                "title": c.title or "Untitled Certificate",
                "category": c.category or "Other",
                "organization": c.organization or "",
            })

    # Completeness
    completeness_score = 0
    total = 7
    if user.full_name: completeness_score += 1
    if user.bio: completeness_score += 1
    if user.institution: completeness_score += 1
    if user.department: completeness_score += 1
    if len(certs) >= 1: completeness_score += 1
    if len(certs) >= 5: completeness_score += 1
    if len(skills) >= 3: completeness_score += 1

    return PortfolioResponse(
        user=UserProfile.model_validate(user),
        certificates=[CertificateResponse.model_validate(c) for c in certs],
        skills=[SkillResponse.model_validate(s) for s in skills],
        category_distribution=dict(cat_dist),
        timeline=timeline,
        portfolio_completeness=round(completeness_score / total * 100, 1),
    )
