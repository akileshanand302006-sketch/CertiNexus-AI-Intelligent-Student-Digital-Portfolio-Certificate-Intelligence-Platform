"""
CertiNexus AI — Classification & Model Predictions Repository (MongoDB Atlas)

Stores classification decisions, individual model predictions (NB, Logistic Regression, LinearSVC),
confidence calibration, top alternatives, and influential terms used by the classifier.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class ClassificationRepository:
    """MongoDB Repository for classifications and model predictions collections."""

    COLLECTION_NAME = "classifications"
    PREDICTIONS_COLLECTION = "model_predictions"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    @property
    def pred_col(self) -> Optional[Collection]:
        return get_collection(self.PREDICTIONS_COLLECTION)

    def save_classification(self, classification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save classification output and multi-model predictions in MongoDB."""
        now = datetime.now(timezone.utc)
        cert_id = classification_data.get("certificate_id")

        predictions_list = classification_data.get("predictions", [])
        if not predictions_list and classification_data.get("model_name"):
            predictions_list = [
                {
                    "model": classification_data.get("model_name"),
                    "prediction": classification_data.get("category"),
                    "confidence": float(classification_data.get("confidence", 0.0)),
                }
            ]

        doc = {
            "_id": str(uuid.uuid4()),
            "certificate_id": cert_id,
            "predictions": predictions_list,
            "final_prediction": classification_data.get("final_prediction") or classification_data.get("category"),
            "final_model": classification_data.get("final_model") or classification_data.get("model_name", "LinearSVC"),
            "confidence": float(classification_data.get("confidence", 0.0)),
            "confidence_level": classification_data.get("confidence_level", "medium"),
            "top_3_predictions": classification_data.get("top_3_predictions", []),
            "all_probabilities": classification_data.get("all_probabilities", []),
            "influential_terms": classification_data.get("influential_terms") or classification_data.get("important_terms", []),
            "feature_attributions": classification_data.get("feature_attributions", {}),
            "calibration_method": classification_data.get("calibration_method", "Platt Scaling (CalibratedClassifierCV)"),
            "model_version": classification_data.get("model_version", "2.0.0"),
            "created_at": now,
            "updated_at": now,
        }

        # Store in classifications collection
        if self.col is not None and cert_id:
            self.col.update_one({"certificate_id": cert_id}, {"$set": doc}, upsert=True)

        # Also store model predictions summary in model_predictions collection
        if self.pred_col is not None and cert_id:
            pred_doc = {
                "_id": str(uuid.uuid4()),
                "certificate_id": cert_id,
                "predictions": predictions_list,
                "final_prediction": doc["final_prediction"],
                "final_model": doc["final_model"],
                "created_at": now,
            }
            self.pred_col.update_one({"certificate_id": cert_id}, {"$set": pred_doc}, upsert=True)

        return doc

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve classification details by certificate id."""
        if self.col is None:
            return None
        return self.col.find_one({"certificate_id": certificate_id})

    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete classification records for a certificate."""
        if self.col is None:
            return False
        res = self.col.delete_many({"certificate_id": certificate_id})
        if self.pred_col is not None:
            self.pred_col.delete_many({"certificate_id": certificate_id})
        return res.deleted_count > 0
