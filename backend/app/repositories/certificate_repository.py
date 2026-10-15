"""
CertiNexus AI — Certificate Repository (MongoDB Atlas)

Handles persistence, lookup, query by user, category filtering, and status updates for certificates.
Supports full structured document schema while maintaining backwards compatibility with legacy flat fields.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo import DESCENDING
from pymongo.collection import Collection

from app.core.database import get_collection


class CertificateRepository:
    """MongoDB Repository for Certificate documents."""

    COLLECTION_NAME = "certificates"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def _normalize_doc(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize certificate dictionary into structured MongoDB schema."""
        now = datetime.now(timezone.utc)
        doc_id = cert_data.get("_id") or cert_data.get("id") or str(uuid.uuid4())

        # Extract file sub-document
        file_info = cert_data.get("file") or {
            "filename": cert_data.get("original_filename", ""),
            "mime_type": cert_data.get("file_type", "application/octet-stream"),
            "storage_path": cert_data.get("file_path", ""),
            "file_hash": cert_data.get("duplicate_hash") or cert_data.get("file_hash", ""),
            "file_size": cert_data.get("file_size", 0),
        }

        # Extract recipient sub-document
        recipient_info = cert_data.get("recipient") or {
            "name": cert_data.get("recipient_name", ""),
            "role": cert_data.get("recipient_role", "Participant"),
            "institution": cert_data.get("institution", ""),
        }

        # Extract issuer sub-document
        issuer_info = cert_data.get("issuer") or {
            "name": cert_data.get("organization", ""),
            "type": cert_data.get("issuer_type", "Organization"),
        }

        # Extract event sub-document
        event_info = cert_data.get("event") or {
            "name": cert_data.get("event_name") or (cert_data.get("event") if isinstance(cert_data.get("event"), str) else ""),
            "date": cert_data.get("issue_date", ""),
            "location": cert_data.get("location", ""),
        }

        # Extract achievement sub-document
        achievement_info = cert_data.get("achievement") or {
            "title": cert_data.get("achievement_level", ""),
            "rank": cert_data.get("rank", ""),
            "score": cert_data.get("score", ""),
            "percentage": cert_data.get("percentage", ""),
        }

        # Extract credential sub-document
        credential_info = cert_data.get("credential") or {
            "id": cert_data.get("certificate_id_extracted", ""),
            "number": cert_data.get("certificate_number", ""),
            "verification_url": cert_data.get("verification_url", ""),
        }

        # Extract timeline sub-document
        timeline_info = cert_data.get("timeline") or {
            "issue_date": cert_data.get("issue_date", ""),
            "start_date": cert_data.get("start_date", ""),
            "end_date": cert_data.get("end_date", ""),
            "expiry_date": cert_data.get("expiry_date", ""),
            "duration": cert_data.get("duration", ""),
        }

        # Classification sub-document
        classification_info = cert_data.get("classification") or {
            "category": cert_data.get("category") or cert_data.get("ai_category", ""),
            "confidence": cert_data.get("ai_confidence", 0.0),
            "confidence_level": cert_data.get("ai_confidence_level", "medium"),
            "model": cert_data.get("model_name", "LinearSVC"),
            "model_version": cert_data.get("model_version", "2.0.0"),
            "important_terms": cert_data.get("ai_important_terms", []),
        }

        doc = {
            "_id": doc_id,
            "id": doc_id,
            "user_id": cert_data.get("user_id"),
            "file": file_info,
            "category": cert_data.get("category") or classification_info.get("category", "Unclassified"),
            "title": cert_data.get("title", ""),
            "recipient": recipient_info,
            "issuer": issuer_info,
            "event": event_info,
            "achievement": achievement_info,
            "credential": credential_info,
            "timeline": timeline_info,
            "skills": cert_data.get("extracted_skills") or cert_data.get("skills", []),
            "classification": classification_info,
            "processing_status": cert_data.get("status") or cert_data.get("processing_status", "uploaded"),
            "verification_status": cert_data.get("verification_status", "not_independently_verified"),

            # Preserved OCR & ML Pipeline data
            "raw_ocr_text": cert_data.get("raw_ocr_text", ""),
            "clean_text": cert_data.get("clean_text", ""),
            "ocr_regions": cert_data.get("ocr_regions", []),
            "ocr_engine": cert_data.get("ocr_engine", "craft+crnn"),
            "extraction_data": cert_data.get("extraction_data", {}),
            "explanation_data": cert_data.get("explanation_data", {}),
            "duplicate_hash": cert_data.get("duplicate_hash", ""),
            "quality_score": cert_data.get("quality_score", {}),

            # State & Metadata
            "status": cert_data.get("status", "uploaded"),
            "is_reviewed": cert_data.get("is_reviewed", False),
            "is_correction": cert_data.get("is_correction", False),
            "is_public": cert_data.get("is_public", False),
            "processing_time_ms": cert_data.get("processing_time_ms", 0.0),
            "model_version": cert_data.get("model_version", "2.0.0"),

            # Backwards-compatible flat fields for FastAPI serializers
            "original_filename": file_info.get("filename", ""),
            "file_path": file_info.get("storage_path", ""),
            "file_type": file_info.get("mime_type", ""),
            "file_size": file_info.get("file_size", 0),
            "recipient_name": recipient_info.get("name", ""),
            "organization": issuer_info.get("name", ""),
            "institution": recipient_info.get("institution", ""),
            "issue_date": timeline_info.get("issue_date", ""),
            "duration": timeline_info.get("duration", ""),
            "certificate_id_extracted": credential_info.get("id", ""),
            "achievement_level": achievement_info.get("title", ""),
            "ai_category": classification_info.get("category", ""),
            "ai_confidence": classification_info.get("confidence", 0.0),
            "ai_confidence_level": classification_info.get("confidence_level", "medium"),
            "ai_important_terms": classification_info.get("important_terms", []),
            "extracted_skills": cert_data.get("extracted_skills") or cert_data.get("skills", []),

            "created_at": cert_data.get("created_at") or now,
            "updated_at": cert_data.get("updated_at") or now,
        }
        return doc

    def create(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or upsert a certificate document in MongoDB."""
        doc = self._normalize_doc(cert_data)
        if self.col is not None:
            self.col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
        return doc

    def find_by_id(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Find a certificate document by id."""
        if self.col is None:
            return None
        return self.col.find_one({"$or": [{"_id": cert_id}, {"id": cert_id}]})

    def find_by_user(self, user_id: str, public_only: bool = False) -> List[Dict[str, Any]]:
        """Find all certificates belonging to a specific user."""
        if self.col is None:
            return []
        query: Dict[str, Any] = {"user_id": user_id}
        if public_only:
            query["is_public"] = True
        cursor = self.col.find(query).sort("created_at", DESCENDING)
        return list(cursor)

    def find_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Find an existing certificate by file duplicate hash."""
        if self.col is None or not file_hash:
            return None
        return self.col.find_one({
            "$or": [
                {"file.file_hash": file_hash},
                {"duplicate_hash": file_hash}
            ]
        })

    def update(self, cert_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update certificate document fields in MongoDB."""
        if self.col is None:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        self.col.update_one(
            {"$or": [{"_id": cert_id}, {"id": cert_id}]},
            {"$set": updates}
        )
        return self.find_by_id(cert_id)

    def delete(self, cert_id: str) -> bool:
        """Delete a certificate document from MongoDB."""
        if self.col is None:
            return False
        res = self.col.delete_one({"$or": [{"_id": cert_id}, {"id": cert_id}]})
        return res.deleted_count > 0

    def count_by_user(self, user_id: str) -> int:
        """Count total certificates for a user."""
        if self.col is None:
            return 0
        return self.col.count_documents({"user_id": user_id})
