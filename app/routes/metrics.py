"""
Model Evaluation Metrics & Performance Benchmarks Route
"""

from fastapi import APIRouter, HTTPException
import json
import os
from app.config import METRICS_PATH
from app.schemas import ModelMetricsResponse

router = APIRouter(prefix="/metrics", tags=["Model Analytics"])


@router.get("", response_model=ModelMetricsResponse, summary="Get Model Metrics & Latency Benchmarks")
async def get_metrics():
    """
    Returns evaluation metrics (AUC-ROC: ~94%, Precision: ~88%, PR-AUC),
    confusion matrix, feature importances, and P95 latency benchmarks.
    """
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="Metrics file not found. Ensure models have been trained.")
    
    with open(METRICS_PATH, "r") as f:
        data = json.load(f)
    
    return data
