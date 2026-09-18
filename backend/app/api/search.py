"""
CertiNexus AI — Search API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.certificate import Certificate
from app.models.user import User
from app.schemas.schemas import CertificateResponse

router = APIRouter()


@router.get("", response_model=list[CertificateResponse])
async def search_certificates(
    q: str = Query("", min_length=0),
    category: str = Query(None),
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Search certificates by text query and/or category filter."""
    query = db.query(Certificate).filter(Certificate.user_id == user.id)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            Certificate.title.ilike(search_term) |
            Certificate.organization.ilike(search_term) |
            Certificate.event.ilike(search_term) |
            Certificate.clean_text.ilike(search_term) |
            Certificate.raw_ocr_text.ilike(search_term)
        )

    if category:
        query = query.filter(Certificate.category == category)

    results = query.order_by(Certificate.created_at.desc()).limit(50).all()
    return results
