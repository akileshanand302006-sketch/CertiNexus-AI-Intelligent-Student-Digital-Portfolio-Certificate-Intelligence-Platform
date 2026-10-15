"""
CertiNexus AI — ML Model Experiments Repository (MongoDB Atlas)

Stores ML experiment tracking logs, GridSearchCV configurations, Stratified K-Fold cross validation metrics,
Macro-F1, per-class evaluation, model sizes, and benchmark reports.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo import DESCENDING
from pymongo.collection import Collection

from app.core.database import get_collection


class ExperimentRepository:
    """MongoDB Repository for model_experiments collection."""

    COLLECTION_NAME = "model_experiments"

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    @property
    def col(self) -> Optional[Collection]:
        if self._collection is not None:
            return self._collection
        return get_collection(self.COLLECTION_NAME)

    def log_experiment(self, exp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update an ML experiment run."""
        now = datetime.now(timezone.utc)
        exp_id = exp_data.get("experiment_id") or str(uuid.uuid4())

        doc = {
            "_id": exp_data.get("_id") or str(uuid.uuid4()),
            "experiment_id": exp_id,
            "dataset": exp_data.get("dataset", "CAPCC-v1"),
            "dataset_version": exp_data.get("dataset_version", "1.0.0"),
            "feature_representation": exp_data.get("feature_representation") or exp_data.get("feature_set", "tfidf_word"),
            "classifier": exp_data.get("classifier") or exp_data.get("model", "LinearSVC"),
            "hyperparameters": exp_data.get("hyperparameters") or exp_data.get("parameters", {}),
            "cross_validation": exp_data.get("cross_validation", "5-Fold Stratified"),
            "accuracy": float(exp_data.get("accuracy") or exp_data.get("validation_accuracy", 0.0)),
            "macro_precision": float(exp_data.get("macro_precision", 0.0)),
            "macro_recall": float(exp_data.get("macro_recall", 0.0)),
            "macro_f1": float(exp_data.get("macro_f1", 0.0)),
            "weighted_f1": float(exp_data.get("weighted_f1", 0.0)),
            "training_time": float(exp_data.get("training_time", 0.0)),
            "inference_time": float(exp_data.get("inference_time", 0.0)),
            "model_size": exp_data.get("model_size", "unknown"),
            "model_version": exp_data.get("model_version", "certinexus-ml-v1"),
            "observations": exp_data.get("observations", ""),
            "created_at": exp_data.get("created_at") or now,
            "updated_at": now,
        }

        if self.col is not None:
            self.col.update_one({"experiment_id": exp_id}, {"$set": doc}, upsert=True)
        return doc

    def get_all_experiments(self) -> List[Dict[str, Any]]:
        """Retrieve all experiment runs ordered by macro_f1 descending."""
        if self.col is None:
            return []
        cursor = self.col.find().sort("macro_f1", DESCENDING)
        return list(cursor)

    def get_by_id(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Find experiment by experiment_id."""
        if self.col is None:
            return None
        return self.col.find_one({"experiment_id": experiment_id})

    def get_best_model(self) -> Optional[Dict[str, Any]]:
        """Retrieve highest performing model based on Macro-F1 metric."""
        if self.col is None:
            return None
        return self.col.find_one(sort=[("macro_f1", DESCENDING)])
