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
    recipient_name = Column(String(500))
    organization = Column(String(500))
    institution = Column(String(500))
    event = Column(String(500))
    issue_date = Column(String(100))
    duration = Column(String(100))
    certificate_id_extracted = Column(String(200))
    achievement_level = Column(String(100))
    ai_summary = Column(Text)

    # AI Classification & Document Type
    document_type = Column(String(50), default="certificate")  # certificate, resume, transcript, general_document
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

    # Advanced Intelligence & Document Pipeline
    ocr_regions = Column(JSON)
    extraction_data = Column(JSON)
    explanation_data = Column(JSON)
    duplicate_hash = Column(String(64), index=True)
    quality_score = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="certificates")
    entities = relationship("ExtractedEntity", back_populates="certificate", cascade="all, delete-orphan")
    regions = relationship("OCRRegion", back_populates="certificate", cascade="all, delete-orphan")
    corrections = relationship("UserCorrection", back_populates="certificate", cascade="all, delete-orphan")


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


class OCRRegion(Base):
    __tablename__ = "ocr_regions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(36), ForeignKey("certificates.id"), nullable=False, index=True)
    text = Column(String(500))
    confidence = Column(Float, default=1.0)
    bbox = Column(JSON)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    certificate = relationship("Certificate", back_populates="regions")


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(36), ForeignKey("certificates.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    text = Column(String(500), nullable=False)
    confidence = Column(Float, default=1.0)
    source = Column(String(50), default="rule_ner")
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    certificate = relationship("Certificate", back_populates="entities")


class UserCorrection(Base):
    __tablename__ = "user_corrections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(36), ForeignKey("certificates.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    original_value = Column(Text)
    corrected_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    certificate = relationship("Certificate", back_populates="corrections")

