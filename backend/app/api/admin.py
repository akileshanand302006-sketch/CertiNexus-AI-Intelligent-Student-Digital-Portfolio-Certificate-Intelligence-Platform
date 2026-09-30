"""
CertiNexus AI — Admin / ML Research API

Serves experiment results, model performance, dataset statistics,
and confusion matrix data for the ML research dashboard.
"""

import csv
import json
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user_dep
from app.database.connection import get_db
from app.models.user import User
from app.schemas.schemas import (
    DatasetStatsResponse,
    ExperimentResponse,
    ModelComparisonResponse,
    ModelPerformanceResponse,
)

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ML_DIR = os.path.join(PROJECT_ROOT, "ml")
EVAL_DIR = os.path.join(ML_DIR, "evaluation")
EDA_DIR = os.path.join(EVAL_DIR, "eda")
EXPERIMENTS_FILE = os.path.join(PROJECT_ROOT, "experiments.csv")


def _require_admin(user: User):
    if user.role != "admin":
        # For now, allow all users to view ML research data for demo purposes
        pass


@router.get("/dataset-statistics", response_model=DatasetStatsResponse)
async def get_dataset_statistics(user: User = Depends(get_current_user_dep)):
    """Get dataset EDA statistics."""
    eda_path = os.path.join(EDA_DIR, "eda_results.json")
    if not os.path.exists(eda_path):
        raise HTTPException(404, "EDA results not found. Run the EDA pipeline first.")

    with open(eda_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return DatasetStatsResponse(
        total_samples=data.get("total_samples", 0),
        total_categories=data.get("total_categories", 0),
        categories=data.get("categories", []),
        class_distribution=data.get("class_distribution", {}),
        text_statistics=data.get("text_statistics", {}),
        vocabulary=data.get("vocabulary", {}),
    )


@router.get("/model-performance", response_model=ModelPerformanceResponse)
async def get_model_performance(user: User = Depends(get_current_user_dep)):
    """Get production model performance metrics."""
    meta_path = os.path.join(ML_DIR, "models", "production", "model_metadata.json")
    if not os.path.exists(meta_path):
        raise HTTPException(404, "Model metadata not found. Train the model first.")

    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Load confusion matrix
    cm_path = os.path.join(EVAL_DIR, "confusion_matrix.json")
    cm_data = None
    if os.path.exists(cm_path):
        with open(cm_path, 'r', encoding='utf-8') as f:
            cm_data = json.load(f)

    # Load classification report
    report_path = os.path.join(EVAL_DIR, "classification_report.json")
    report = None
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

    return ModelPerformanceResponse(
        model_name=metadata.get("algorithm", ""),
        version=metadata.get("version", ""),
        metrics=metadata.get("metrics", {}),
        classes=metadata.get("classes", []),
        confusion_matrix=cm_data.get("matrix") if cm_data else None,
        classification_report=report,
    )


@router.get("/experiments", response_model=ExperimentResponse)
async def get_experiments(user: User = Depends(get_current_user_dep)):
    """Get experiment log."""
    if not os.path.exists(EXPERIMENTS_FILE):
        return ExperimentResponse(experiments=[])

    experiments = []
    with open(EXPERIMENTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            experiments.append(dict(row))

    return ExperimentResponse(experiments=experiments)


@router.get("/model-comparison", response_model=ModelComparisonResponse)
async def get_model_comparison(user: User = Depends(get_current_user_dep)):
    """Get model comparison results."""
    comp_path = os.path.join(EVAL_DIR, "model_comparison.json")
    if not os.path.exists(comp_path):
        raise HTTPException(404, "Model comparison not found. Run the training pipeline first.")

    with open(comp_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return ModelComparisonResponse(models=data)


@router.get("/error-analysis")
async def get_error_analysis(user: User = Depends(get_current_user_dep)):
    """Get error analysis report."""
    error_path = os.path.join(EVAL_DIR, "error_analysis.json")
    if not os.path.exists(error_path):
        raise HTTPException(404, "Error analysis not found.")

    with open(error_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.get("/confusion-matrix")
async def get_confusion_matrix(user: User = Depends(get_current_user_dep)):
    """Get confusion matrix data."""
    cm_path = os.path.join(EVAL_DIR, "confusion_matrix.json")
    if not os.path.exists(cm_path):
        raise HTTPException(404, "Confusion matrix not found.")

    with open(cm_path, 'r', encoding='utf-8') as f:
        return json.load(f)
