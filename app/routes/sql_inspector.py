"""
SQL Query Inspector & Feature Extraction Routes
Allows inspecting and executing the production SQL queries used for feature extraction.
"""

from fastapi import APIRouter
from app.db import execute_analytical_query
from app.schemas import SQLQueryRequest

router = APIRouter(prefix="/sql", tags=["SQL Feature Engineering"])


@router.get("/queries", summary="Get Pre-configured Production SQL Queries")
async def get_sql_queries():
    return {
        "queries": [
            {
                "id": "rolling_velocities",
                "name": "Rolling 1h & 24h Velocity Window Aggregation",
                "description": "Calculates rolling transaction frequency and 24-hour spend using SQLite window functions."
            },
            {
                "id": "merchant_risks",
                "name": "Merchant Category Risk & Volume Aggregations",
                "description": "Aggregates fraud probability and ticket volume across merchant industry sectors."
            },
            {
                "id": "impossible_travel",
                "name": "Impossible Travel Supersonic Speed Anomaly Detector",
                "description": "Uses LAG window functions and Haversine distance to detect velocities exceeding 800 km/h."
            }
        ]
    }


@router.post("/execute", summary="Execute Analytical SQL Query")
async def run_sql(payload: SQLQueryRequest):
    return execute_analytical_query(payload.query_id)
