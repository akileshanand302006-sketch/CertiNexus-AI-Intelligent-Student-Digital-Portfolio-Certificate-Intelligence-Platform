"""
CertiNexus AI — User Database Models
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    institution = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    graduation_year = Column(String(10), nullable=True)
    role = Column(String(20), default="student")  # student, admin
    is_active = Column(Boolean, default=True)
    portfolio_public = Column(Boolean, default=False)
    portfolio_theme = Column(String(50), default="liquid-glass")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("StudentSkill", back_populates="user", cascade="all, delete-orphan")
