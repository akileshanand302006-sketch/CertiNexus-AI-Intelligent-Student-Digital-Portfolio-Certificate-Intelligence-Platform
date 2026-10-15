"""
CertiNexus AI — Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Auth Schemas
# ============================================================

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = None
    institution: Optional[str] = None

class UserLogin(BaseModel):
    email: Optional[str] = None
    username_or_email: Optional[str] = None
    username: Optional[str] = None
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str


# ============================================================
# User Schemas
# ============================================================

class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[str] = None
    role: str = "student"
    portfolio_public: bool = False
    portfolio_theme: str = "liquid-glass"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[str] = None
    portfolio_public: Optional[bool] = None
    portfolio_theme: Optional[str] = None


# ============================================================
# Certificate Schemas
# ============================================================

class CertificateResponse(BaseModel):
    id: str
    title: Optional[str] = None
    recipient_name: Optional[str] = None
    organization: Optional[str] = None
    institution: Optional[str] = None
    event: Optional[str] = None
    issue_date: Optional[str] = None
    duration: Optional[str] = None
    certificate_id_extracted: Optional[str] = None
    document_type: Optional[str] = "certificate"
    category: Optional[str] = None
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_confidence_level: Optional[str] = None
    ai_important_terms: Optional[List[Dict[str, Any]]] = None
    status: str = "uploaded"
    is_reviewed: bool = False
    raw_ocr_text: Optional[str] = None
    extracted_skills: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    is_public: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Advanced Intelligence
    ocr_regions: Optional[List[Dict[str, Any]]] = None
    extraction_data: Optional[Dict[str, Any]] = None
    explanation_data: Optional[Dict[str, Any]] = None
    duplicate_hash: Optional[str] = None
    quality_score: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class CertificateUpdate(BaseModel):
    title: Optional[str] = None
    recipient_name: Optional[str] = None
    organization: Optional[str] = None
    institution: Optional[str] = None
    event: Optional[str] = None
    issue_date: Optional[str] = None
    duration: Optional[str] = None
    certificate_id_extracted: Optional[str] = None
    category: Optional[str] = None
    ai_summary: Optional[str] = None
    is_public: Optional[bool] = None
    is_reviewed: Optional[bool] = None

class ProcessingStatus(BaseModel):
    certificate_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None


class ExtractionResponse(BaseModel):
    certificate_id: str
    category: Optional[str] = None
    completeness_score: float = 0.0
    entities: List[Dict[str, Any]] = []
    structured_fields: Dict[str, Any] = {}
    skills: List[str] = []


class ExplanationResponse(BaseModel):
    certificate_id: str
    category: str
    confidence: float
    confidence_level: str
    positive_terms: List[Dict[str, Any]] = []
    negative_terms: List[Dict[str, Any]] = []
    alternatives: List[Dict[str, Any]] = []
    explanation_text: str = ""
    model_version: str = ""


class OCRDetailsResponse(BaseModel):
    certificate_id: str
    ocr_engine: str = "easyocr"
    raw_text: str = ""
    clean_text: str = ""
    regions: List[Dict[str, Any]] = []
    quality_score: Optional[Dict[str, Any]] = None
    num_regions: int = 0


class CorrectionRequest(BaseModel):
    field_name: str
    corrected_value: str



# ============================================================
# Skill Schemas
# ============================================================

class SkillResponse(BaseModel):
    id: str
    skill_name: str
    skill_category: Optional[str] = None
    confidence: float = 1.0
    occurrence_count: int = 1
    first_detected: Optional[datetime] = None
    last_detected: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Analytics Schemas
# ============================================================

class AnalyticsResponse(BaseModel):
    total_certificates: int = 0
    total_skills: int = 0
    total_categories: int = 0
    category_distribution: Dict[str, int] = {}
    skills_distribution: Dict[str, int] = {}
    recent_certificates: List[CertificateResponse] = []
    monthly_activity: Dict[str, int] = {}
    portfolio_completeness: float = 0.0


# ============================================================
# Portfolio Schemas
# ============================================================

class PortfolioResponse(BaseModel):
    user: UserProfile
    certificates: List[CertificateResponse] = []
    skills: List[SkillResponse] = []
    category_distribution: Dict[str, int] = {}
    timeline: List[Dict[str, Any]] = []
    portfolio_completeness: float = 0.0


# ============================================================
# Admin / ML Research Schemas
# ============================================================

class DatasetStatsResponse(BaseModel):
    total_samples: int = 0
    total_categories: int = 0
    categories: List[str] = []
    class_distribution: Dict[str, int] = {}
    text_statistics: Dict[str, Any] = {}
    vocabulary: Dict[str, Any] = {}

class ModelPerformanceResponse(BaseModel):
    model_name: str = ""
    version: str = ""
    metrics: Dict[str, float] = {}
    classes: List[str] = []
    confusion_matrix: Optional[List[List[int]]] = None
    classification_report: Optional[Dict[str, Any]] = None

class ExperimentResponse(BaseModel):
    experiments: List[Dict[str, Any]] = []

class ModelComparisonResponse(BaseModel):
    models: Dict[str, Any] = {}
