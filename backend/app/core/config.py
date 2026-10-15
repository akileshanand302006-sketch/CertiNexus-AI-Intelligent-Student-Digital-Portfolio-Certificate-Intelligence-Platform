"""
CertiNexus AI — Application Configuration

Loads settings from environment variables and .env file.
Provides centralized access to MongoDB, JWT, Storage, and ML parameters.
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load root .env
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
env_paths = [
    _project_root / ".env",
    _backend_dir / ".env",
    Path(".env"),
]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=False)
        break


class Settings:
    """Application settings class."""

    # Project metadata
    PROJECT_NAME: str = "CertiNexus AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    # MongoDB Atlas Configuration
    MONGODB_URI: str = os.environ.get(
        "MONGODB_URI",
        "mongodb+srv://akileshanand302006_db_user:<db_password>@certinexuscluster.e5ke8fh.mongodb.net/certinexus?retryWrites=true&w=majority&appName=CertiNexusCluster"
    )
    MONGODB_DATABASE: str = os.environ.get("MONGODB_DATABASE", "certinexus")
    MONGODB_MAX_POOL_SIZE: int = int(os.environ.get("MONGODB_MAX_POOL_SIZE", "50"))
    MONGODB_MIN_POOL_SIZE: int = int(os.environ.get("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = int(
        os.environ.get("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")
    )

    # Legacy Database URL (Fallback / Local SQLite)
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./certinexus.db")

    # JWT Authentication
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "certinexus-secure-jwt-secret-key-2026")
    JWT_REFRESH_SECRET: str = os.environ.get("JWT_REFRESH_SECRET", "certinexus-refresh-secret-key-2026")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # File Storage
    STORAGE_TYPE: str = os.environ.get("STORAGE_TYPE", "local")
    STORAGE_PATH: str = os.environ.get("STORAGE_PATH", "./storage/uploads")

    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.environ.get(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]

    # Server
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")

    # ML Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = float(os.environ.get("HIGH_CONFIDENCE_THRESHOLD", "0.80"))
    LOW_CONFIDENCE_THRESHOLD: float = float(os.environ.get("LOW_CONFIDENCE_THRESHOLD", "0.50"))

    @property
    def is_mongodb_configured(self) -> bool:
        """Check if MONGODB_URI is provided and does not contain placeholder password."""
        uri = self.MONGODB_URI
        if not uri:
            return False
        if "<db_password>" in uri or "<password>" in uri or "YOUR_REAL_PASSWORD" in uri:
            return False
        return True


settings = Settings()
