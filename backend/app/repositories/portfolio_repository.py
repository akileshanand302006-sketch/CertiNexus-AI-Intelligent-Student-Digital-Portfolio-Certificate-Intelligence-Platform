"""
CertiNexus AI — Portfolio Profiles Repository (MongoDB Atlas)

Manages public and private student portfolio profiles.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class PortfolioRepository:
    """MongoDB Repository for portfolio_profiles collection."""

    COLLECTION_NAME = "portfolio_profiles"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def upsert_portfolio(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert portfolio profile configuration."""
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "portfolio_public": data.get("portfolio_public", False),
            "portfolio_theme": data.get("portfolio_theme", "liquid-glass"),
            "featured_certificates": data.get("featured_certificates", []),
            "custom_sections": data.get("custom_sections", []),
            "updated_at": now,
        }
        if self.col is not None:
            self.col.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
        return doc

    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get portfolio profile by user id."""
        if self.col is None:
            return None
        return self.col.find_one({"user_id": user_id})
