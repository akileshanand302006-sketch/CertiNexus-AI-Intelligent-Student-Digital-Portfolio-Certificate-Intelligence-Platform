"""
CertiNexus AI — Database Connection

SQLAlchemy engine, session factory, and table creation for SQLite.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./certinexus.db")

# SQLite needs check_same_thread=False for FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables and add any missing columns."""
    from app.models import certificate, user  # noqa: F401 — import for side effects
    Base.metadata.create_all(bind=engine)

    # SQLite schema migration for newly added columns
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("PRAGMA table_info(certificates)"))
            existing_cols = {row[1] for row in result.fetchall()}
            
            new_cols = [
                ("ocr_regions", "TEXT"),
                ("extraction_data", "TEXT"),
                ("explanation_data", "TEXT"),
                ("duplicate_hash", "VARCHAR(64)"),
                ("quality_score", "TEXT"),
            ]
            for col_name, col_type in new_cols:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE certificates ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
    except Exception as e:
        print(f"Schema migration notice: {e}")

