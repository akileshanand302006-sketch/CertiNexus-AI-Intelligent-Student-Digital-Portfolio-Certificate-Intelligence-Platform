"""
CertiNexus AI — Certificate Database Models
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # File info
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(20))
    file_size = Column(Integer)

    # Extracted info
    title = Column(String(500))
    organization = Column(String(500))
    event = Column(String(500))
    issue_date = Column(String(100))
    certificate_id_extracted = Column(String(200))
    achievement_level = Column(String(100))

    # AI Classification
    category = Column(String(100))
    ai_category = Column(String(100))  # Original AI prediction
    ai_confidence = Column(Float)
    ai_confidence_level = Column(String(20))  # high, medium, low
    ai_important_terms = Column(JSON)

    # Status
    status = Column(String(50), default="uploaded")
    # uploaded, ocr_processing, extracting, classifying, completed, failed, review_required
    is_reviewed = Column(Boolean, default=False)
    is_correction = Column(Boolean, default=False)  # User corrected the AI prediction

    # OCR
    raw_ocr_text = Column(Text)
    clean_text = Column(Text)

    # Skills
    extracted_skills = Column(JSON)  # List of skill strings

    # Metadata
    model_version = Column(String(50))
    processing_time_ms = Column(Float)
    ocr_engine = Column(String(50))

    # Visibility
    is_public = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="certificates")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    skill_name = Column(String(200), nullable=False)
    skill_category = Column(String(100))  # Programming, AI/ML, Web, etc.
    confidence = Column(Float, default=1.0)
    source_certificate_id = Column(String(36))
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_detected = Column(DateTime, default=datetime.utcnow)
    occurrence_count = Column(Integer, default=1)

    user = relationship("User", back_populates="skills")


class ModelFeedback(Base):
    __tablename__ = "model_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(36), ForeignKey("certificates.id"))
    original_prediction = Column(String(100))
    original_confidence = Column(Float)
    corrected_label = Column(String(100))
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(50))
    date = Column(String(50))
    dataset_version = Column(String(50))
    feature_set = Column(String(100))
    model = Column(String(100))
    parameters = Column(JSON)
    validation_accuracy = Column(Float)
    macro_f1 = Column(Float)
    training_time = Column(Float)
    observations = Column(Text)
