"""
CertiNexus AI — Processing Jobs Repository (MongoDB Atlas)

Tracks asynchronous pipeline execution stages:
upload -> preprocessing -> text_detection -> ocr -> ner -> feature_extraction ->
classification -> metadata_extraction -> duplicate_detection -> completed
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class ProcessingJobRepository:
    """MongoDB Repository for processing_jobs collection."""

    COLLECTION_NAME = "processing_jobs"

    STAGE_PROGRESS = {
        "upload": 10,
        "preprocessing": 20,
        "text_detection": 35,
        "ocr": 50,
        "ner": 65,
        "feature_extraction": 75,
        "classification": 85,
        "metadata_extraction": 92,
        "duplicate_detection": 97,
        "completed": 100,
        "failed": 0,
    }

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def create_job(self, certificate_id: str) -> Dict[str, Any]:
        """Create a new processing job for a certificate."""
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "certificate_id": certificate_id,
            "status": "processing",
            "current_stage": "upload",
            "progress": 10,
            "started_at": now,
            "completed_at": None,
            "error": None,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"certificate_id": certificate_id}, {"$set": doc}, upsert=True)
        return doc

    def update_stage(self, certificate_id: str, stage: str, progress: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Update job stage and calculate progress."""
        now = datetime.now(timezone.utc)
        prog = progress if progress is not None else self.STAGE_PROGRESS.get(stage, 50)
        updates = {
            "current_stage": stage,
            "status": "processing",
            "progress": prog,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"certificate_id": certificate_id}, {"$set": updates})
        return self.get_by_certificate_id(certificate_id)

    def complete_job(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Mark job as completed successfully."""
        now = datetime.now(timezone.utc)
        updates = {
            "current_stage": "completed",
            "status": "completed",
            "progress": 100,
            "completed_at": now,
            "error": None,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"certificate_id": certificate_id}, {"$set": updates})
        return self.get_by_certificate_id(certificate_id)

    def fail_job(self, certificate_id: str, error_message: str) -> Optional[Dict[str, Any]]:
        """Mark job as failed with error details."""
        now = datetime.now(timezone.utc)
        updates = {
            "status": "failed",
            "progress": 0,
            "completed_at": now,
            "error": error_message,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"certificate_id": certificate_id}, {"$set": updates})
        return self.get_by_certificate_id(certificate_id)

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status for a certificate."""
        if self.col is None:
            return None
        return self.col.find_one({"certificate_id": certificate_id})
