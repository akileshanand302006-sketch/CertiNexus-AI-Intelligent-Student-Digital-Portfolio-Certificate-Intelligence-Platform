"""
CertiNexus AI — Skills Repository (MongoDB Atlas)

Stores extracted student skills and frequency in MongoDB Atlas.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class SkillRepository:
    """MongoDB Repository for skills collection."""

    COLLECTION_NAME = "skills"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def upsert_skill(self, user_id: str, skill_name: str, cert_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Insert or increment student skill occurrence."""
        now = datetime.now(timezone.utc)
        if self.col is None:
            return {}

        existing = self.col.find_one({"user_id": user_id, "skill_name": skill_name})
        if existing:
            self.col.update_one(
                {"_id": existing["_id"]},
                {
                    "$inc": {"occurrence_count": 1},
                    "$set": {"last_detected": now},
                    "$addToSet": {"certificate_ids": cert_id},
                }
            )
            return self.col.find_one({"_id": existing["_id"]})
        else:
            doc = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "skill_name": skill_name,
                "skill_category": category or "General",
                "confidence": 1.0,
                "occurrence_count": 1,
                "source_certificate_id": cert_id,
                "certificate_ids": [cert_id],
                "first_detected": now,
                "last_detected": now,
            }
            self.col.insert_one(doc)
            return doc

    def get_user_skills(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all skills for a user."""
        if self.col is None:
            return []
        cursor = self.col.find({"user_id": user_id})
        return list(cursor)
