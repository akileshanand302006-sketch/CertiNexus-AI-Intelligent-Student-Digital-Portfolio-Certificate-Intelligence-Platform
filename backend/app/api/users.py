"""
CertiNexus AI — Users API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.user import User
from app.schemas.schemas import UserProfile, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_current_user_dep)):
    """Get current user profile."""
    return user


@router.patch("/me", response_model=UserProfile)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
