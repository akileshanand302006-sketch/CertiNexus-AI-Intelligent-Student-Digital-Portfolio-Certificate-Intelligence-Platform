"""
CertiNexus AI — Extracted Entities Repository (MongoDB Atlas)

Stores Rule-Based Named Entity Recognition (NER) outputs for certificates.
Supports 25+ entity types including PERSON, ORGANIZATION, EVENT, SKILL, DATES, CREDENTIAL_ID.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class EntityRepository:
    """MongoDB Repository for extracted NER entities."""

    COLLECTION_NAME = "extracted_entities"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def save_entities(self, certificate_id: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Save extracted entities document for a certificate."""
        now = datetime.now(timezone.utc)
        normalized_entities = []
        for ent in entities:
            normalized_entities.append({
                "type": ent.get("type") or ent.get("entity_type", "UNKNOWN"),
                "value": ent.get("value") or ent.get("text", ""),
                "confidence": float(ent.get("confidence", 1.0)),
                "source": ent.get("source", "rule_ner"),
                "start": ent.get("start") or ent.get("start_char", 0),
                "end": ent.get("end") or ent.get("end_char", 0),
                "metadata": ent.get("metadata") or ent.get("metadata_json", {}),
            })

        doc = {
            "_id": str(uuid.uuid4()),
            "certificate_id": certificate_id,
            "entities": normalized_entities,
            "total_entities": len(normalized_entities),
            "created_at": now,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"certificate_id": certificate_id}, {"$set": doc}, upsert=True)
        return doc

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve extracted entities by certificate id."""
        if self.col is None:
            return None
        return self.col.find_one({"certificate_id": certificate_id})

    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete extracted entities for a certificate."""
        if self.col is None:
            return False
        res = self.col.delete_many({"certificate_id": certificate_id})
        return res.deleted_count > 0
