"""
CertiNexus AI — OCR Results Repository (MongoDB Atlas)

Stores CRAFT text detection and CRNN+BiLSTM+CTC recognition results.
Preserves raw OCR, cleaned text, bounding boxes, and image quality metrics.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

from app.core.database import get_collection


class OCRRepository:
    """MongoDB Repository for OCR Results collection."""

    COLLECTION_NAME = "ocr_results"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def save_ocr_result(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update OCR result for a certificate."""
        now = datetime.now(timezone.utc)
        doc_id = ocr_data.get("_id") or str(uuid.uuid4())
        cert_id = ocr_data.get("certificate_id")

        # Standardize regions bounding box schema
        normalized_regions = []
        for r in ocr_data.get("regions", []):
            bbox = r.get("bbox") or r.get("bounding_box") or {}
            if isinstance(bbox, list):
                # Polygon or [[x1, y1], [x2, y2], ...]
                pts = bbox
                if len(pts) >= 4 and isinstance(pts[0], (list, tuple)):
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    bbox_dict = {
                        "x": min(xs),
                        "y": min(ys),
                        "width": max(xs) - min(xs),
                        "height": max(ys) - min(ys),
                    }
                else:
                    bbox_dict = {"raw": pts}
            elif isinstance(bbox, dict):
                bbox_dict = bbox
            else:
                bbox_dict = {}

            normalized_regions.append({
                "text": r.get("text", ""),
                "confidence": float(r.get("confidence", 1.0)),
                "bounding_box": bbox_dict,
                "order_index": r.get("order_index", len(normalized_regions)),
            })

        doc = {
            "_id": doc_id,
            "certificate_id": cert_id,
            "detector": ocr_data.get("detector", "CRAFT"),
            "ocr_model": ocr_data.get("ocr_model", "CRNN-BiLSTM-CTC"),
            "full_text": ocr_data.get("full_text") or ocr_data.get("raw_text", ""),
            "cleaned_text": ocr_data.get("cleaned_text") or ocr_data.get("clean_text", ""),
            "average_confidence": float(ocr_data.get("average_confidence", 0.0)),
            "regions": normalized_regions,
            "quality_metrics": ocr_data.get("quality_metrics", {}),
            "created_at": ocr_data.get("created_at") or now,
            "updated_at": now,
        }

        if self.col is not None and cert_id:
            self.col.update_one({"certificate_id": cert_id}, {"$set": doc}, upsert=True)
        return doc

    def get_by_certificate_id(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve OCR result by certificate id."""
        if self.col is None:
            return None
        return self.col.find_one({"certificate_id": certificate_id})

    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete OCR results for a certificate."""
        if self.col is None:
            return False
        res = self.col.delete_many({"certificate_id": certificate_id})
        return res.deleted_count > 0
