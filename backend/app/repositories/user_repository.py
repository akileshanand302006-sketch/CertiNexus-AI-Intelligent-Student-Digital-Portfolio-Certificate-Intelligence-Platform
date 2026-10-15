"""
CertiNexus AI — User Repository (MongoDB Atlas)

Handles persistence, lookup, password hashing, and profile updates for users.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class UserRepository:
    """MongoDB Repository for user management."""

    COLLECTION_NAME = "users"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user document in MongoDB."""
        now = datetime.now(timezone.utc)
        doc = {
            "_id": user_data.get("_id") or user_data.get("id") or str(uuid.uuid4()),
            "id": user_data.get("id") or user_data.get("_id") or str(uuid.uuid4()),
            "email": user_data["email"].strip().lower(),
            "username": user_data.get("username", user_data["email"]).strip(),
            "password_hash": user_data.get("password_hash") or user_data.get("hashed_password"),
            "full_name": user_data.get("full_name", ""),
            "role": user_data.get("role", "student"),
            "is_active": user_data.get("is_active", True),
            "profile": {
                "institution": user_data.get("institution", ""),
                "department": user_data.get("department", ""),
                "degree": user_data.get("degree", ""),
                "academic_year": user_data.get("academic_year", "2026-2027"),
                "graduation_year": user_data.get("graduation_year", "2027"),
                "bio": user_data.get("bio", ""),
                "profile_photo": user_data.get("avatar_url", ""),
                "skills": user_data.get("skills", []),
                "social_links": user_data.get("social_links", {}),
                "portfolio_public": user_data.get("portfolio_public", False),
                "portfolio_theme": user_data.get("portfolio_theme", "liquid-glass"),
            },
            "created_at": user_data.get("created_at") or now,
            "updated_at": user_data.get("updated_at") or now,
        }
        # Keep id and _id synchronized
        doc["id"] = doc["_id"]

        if self.col is not None:
            try:
                self.col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            except Exception:
                pass
        return doc

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user document by email."""
        if self.col is None:
            return None
        try:
            return self.col.find_one({"email": email.strip().lower()})
        except Exception:
            return None

    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a user document by id."""
        if self.col is None:
            return None
        try:
            return self.col.find_one({"$or": [{"_id": user_id}, {"id": user_id}]})
        except Exception:
            return None

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user document by username."""
        if self.col is None:
            return None
        try:
            return self.col.find_one({"username": username.strip()})
        except Exception:
            return None

    def update(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile or general fields."""
        if self.col is None:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        
        # Flatten profile updates if needed
        profile_fields = {
            "institution", "department", "degree", "academic_year", "graduation_year",
            "bio", "profile_photo", "skills", "social_links", "portfolio_public", "portfolio_theme"
        }
        
        set_dict: Dict[str, Any] = {}
        for k, v in updates.items():
            if k in profile_fields:
                set_dict[f"profile.{k}"] = v
            else:
                set_dict[k] = v

        self.col.update_one(
            {"$or": [{"_id": user_id}, {"id": user_id}]},
            {"$set": set_dict}
        )
        return self.find_by_id(user_id)

    def delete(self, user_id: str) -> bool:
        """Delete a user document."""
        if self.col is None:
            return False
        res = self.col.delete_one({"$or": [{"_id": user_id}, {"id": user_id}]})
        return res.deleted_count > 0

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List users for admin management."""
        if self.col is None:
            return []
        cursor = self.col.find().limit(limit)
        return list(cursor)
