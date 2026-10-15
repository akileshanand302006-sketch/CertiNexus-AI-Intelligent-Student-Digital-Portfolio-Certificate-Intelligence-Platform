"""
CertiNexus AI — ML System & Model Intelligence API Router
Exposes endpoints for active models, benchmark logs, and experiments under /api/ml.
"""

import csv
import json
import os
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user_dep
from app.models.user import User
from app.repositories.experiment_repository import ExperimentRepository

router = APIRouter()
exp_repo = ExperimentRepository()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ML_DIR = os.path.join(PROJECT_ROOT, "ml")
EVAL_DIR = os.path.join(ML_DIR, "evaluation")
EXPERIMENTS_FILE = os.path.join(PROJECT_ROOT, "experiments.csv")


@router.get("/models")
async def get_ml_models(user: User = Depends(get_current_user_dep)):
    """
    Get active production model and candidate model configurations.
    GET /api/ml/models
    """
    prod_meta_path = os.path.join(ML_DIR, "models", "production", "model_metadata.json")
    prod_meta = {}
    if os.path.exists(prod_meta_path):
        with open(prod_meta_path, "r", encoding="utf-8") as f:
            prod_meta = json.load(f)

    # Check candidates
    candidates = []
    candidates_dir = os.path.join(ML_DIR, "models", "candidates")
    if os.path.exists(candidates_dir):
        for fname in os.listdir(candidates_dir):
            if fname.endswith(".joblib") or fname.endswith(".json"):
                candidates.append(fname)

    # Check benchmark results
    bench_path = os.path.join(EVAL_DIR, "benchmark_results.json")
    benchmark_summary = {}
    if os.path.exists(bench_path):
        with open(bench_path, "r", encoding="utf-8") as f:
            bdata = json.load(f)
            benchmark_summary = {
                "champion": bdata.get("best_configuration"),
                "num_experiments": bdata.get("num_experiments"),
                "classes": bdata.get("classes"),
            }

    return {
        "production_model": prod_meta,
        "champion_configuration": benchmark_summary.get("champion", "MultinomialNB__tfidf_word"),
        "candidates": candidates,
        "supported_categories": prod_meta.get("classes", []),
        "pipeline_version": "2.0.0",
        "calibration": "Platt Scaling (CalibratedClassifierCV)",
    }


@router.get("/experiments")
async def get_ml_experiments(user: User = Depends(get_current_user_dep)):
    """
    Get experimental benchmark logs across all 9 experimental matrices from MongoDB Atlas.
    GET /api/ml/experiments
    """
    # 1. Check MongoDB Atlas model_experiments collection
    try:
        mongo_exps = exp_repo.get_all_experiments()
        if mongo_exps:
            # Clean MongoDB ObjectId for JSON serialization
            for ex in mongo_exps:
                if "_id" in ex:
                    ex["_id"] = str(ex["_id"])
            return {
                "source": "mongodb_atlas",
                "experiments": mongo_exps,
                "total": len(mongo_exps),
            }
    except Exception as e:
        print(f"Notice: MongoDB Atlas experiment fetch notice: {e}")

    # 2. From benchmark_results.json and seed MongoDB Atlas
    bench_path = os.path.join(EVAL_DIR, "benchmark_results.json")
    if os.path.exists(bench_path):
        with open(bench_path, "r", encoding="utf-8") as f:
            bdata = json.load(f)
            results = bdata.get("results", [])

            # Background sync to MongoDB Atlas
            try:
                for r in results:
                    exp_repo.log_experiment({
                        "experiment_id": f"{r.get('model')}__{r.get('feature_set')}",
                        "classifier": r.get("model"),
                        "feature_representation": r.get("feature_set"),
                        "accuracy": r.get("test_accuracy", 0.0),
                        "macro_precision": r.get("test_macro_precision", 0.0),
                        "macro_recall": r.get("test_macro_recall", 0.0),
                        "macro_f1": r.get("test_macro_f1", 0.0),
                        "weighted_f1": r.get("test_weighted_f1", 0.0),
                        "training_time": r.get("train_time_sec", 0.0),
                        "inference_time": r.get("inference_time_ms", 0.0),
                        "hyperparameters": r.get("best_params", {}),
                    })
            except Exception:
                pass

            return {
                "source": "benchmark_suite",
                "experiments": results,
                "best_configuration": bdata.get("best_configuration"),
            }

    # 3. Fallback to experiments.csv
    if os.path.exists(EXPERIMENTS_FILE):
        rows = []
        with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(dict(r))
        return {"source": "experiments_csv", "experiments": rows}

    return {"source": "none", "experiments": []}


@router.get("/benchmark-report")
async def get_benchmark_report(user: User = Depends(get_current_user_dep)):
    """
    Get the full markdown system evaluation report.
    GET /api/ml/benchmark-report
    """
    report_file = os.path.join(EVAL_DIR, "SYSTEM_EVALUATION_REPORT.md")
    if not os.path.exists(report_file):
        raise HTTPException(404, "Benchmark report not found. Run benchmark suite first.")

    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()

    return {"report_markdown": content}
