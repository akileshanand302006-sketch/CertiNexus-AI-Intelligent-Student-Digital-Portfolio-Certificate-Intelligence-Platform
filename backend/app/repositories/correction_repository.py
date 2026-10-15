"""
CertiNexus AI — User Corrections Repository (MongoDB Atlas)

Stores human-in-the-loop annotations and corrections for certificates.
Preserves original AI output vs user edits to build future fine-tuning datasets.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo import DESCENDING
from pymongo.collection import Collection

from app.core.database import get_collection


class CorrectionRepository:
    """MongoDB Repository for user_corrections collection."""

    COLLECTION_NAME = "user_corrections"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def save_correction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a human-in-the-loop field correction."""
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "certificate_id": data.get("certificate_id"),
            "user_id": data.get("user_id"),
            "field": data.get("field") or data.get("field_name"),
            "field_name": data.get("field_name") or data.get("field"),
            "original_value": str(data.get("original_value", "")),
            "corrected_value": str(data.get("corrected_value", "")),
            "corrected_by": data.get("corrected_by") or data.get("user_id"),
            "created_at": data.get("created_at") or now,
        }

        if self.col is not None:
            self.col.insert_one(doc)
        return doc

    def get_by_certificate_id(self, certificate_id: str) -> List[Dict[str, Any]]:
        """Retrieve all corrections for a specific certificate."""
        if self.col is None:
            return []
        cursor = self.col.find({"certificate_id": certificate_id}).sort("created_at", DESCENDING)
        return list(cursor)

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent user corrections for HITL dataset analysis."""
        if self.col is None:
            return []
        cursor = self.col.find().sort("created_at", DESCENDING).limit(limit)
        return list(cursor)
