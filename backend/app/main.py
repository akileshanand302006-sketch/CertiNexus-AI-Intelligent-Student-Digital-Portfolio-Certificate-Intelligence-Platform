"""
CertiNexus AI — FastAPI Backend Application

Main entry point for the API server.
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root and backend to path for ML and app imports
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_project_root = os.path.dirname(_backend_dir)
for _p in [_project_root, _backend_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.api import admin, analytics, auth, certificates, chat, ml, portfolio, resume, search, users
from app.database.connection import create_tables
from app.core.database import db_manager, check_mongodb_health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # 1. Initialize MongoDB Atlas connection
    mongo_ok = db_manager.connect()
    if mongo_ok:
        print(f"Connected to MongoDB Atlas: {settings.MONGODB_DATABASE}")
    else:
        print(f"MongoDB Atlas notice: {db_manager.connection_error or 'degraded mode'}")

    # 2. Initialize fallback SQLite tables if used
    try:
        create_tables()
        print("Fallback SQLite schema verified")
    except Exception as e:
        print(f"Fallback SQLite schema notice: {e}")

    # 3. Create upload directory
    upload_dir = settings.STORAGE_PATH
    os.makedirs(upload_dir, exist_ok=True)

    yield

    # Shutdown: gracefully close MongoDB connection
    db_manager.disconnect()
    print("Application shutting down: MongoDB connection closed")


app = FastAPI(
    title="CertiNexus AI",
    description="Intelligent Student Digital Portfolio & Certificate Intelligence API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
origins = settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(users.router, prefix="/api", tags=["Profile"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chatbot"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin / ML Research"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML Intelligence"])


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """
    MongoDB Atlas & Backend health check endpoint.
    Reports connectivity status without leaking credentials.
    """
    health = check_mongodb_health()
    return {
        "status": health["status"],
        "database": health["database"],
        "database_name": health.get("database_name", "certinexus"),
        "service": "CertiNexus AI",
        "version": settings.VERSION,
    }

