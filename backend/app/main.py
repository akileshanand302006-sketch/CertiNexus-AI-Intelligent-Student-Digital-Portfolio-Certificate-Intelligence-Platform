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

# Add project root to path for ML imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import admin, analytics, auth, certificates, portfolio, resume, search, users
from app.database.connection import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    create_tables()
    print("Database tables created")

    # Create upload directory
    upload_dir = os.environ.get("STORAGE_PATH", "./storage/uploads")
    os.makedirs(upload_dir, exist_ok=True)

    yield

    # Shutdown
    print("Application shutting down")


app = FastAPI(
    title="CertiNexus AI",
    description="Intelligent Student Digital Portfolio & Certificate Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin / ML Research"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "CertiNexus AI"}
