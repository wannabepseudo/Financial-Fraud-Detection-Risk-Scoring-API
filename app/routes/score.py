"""
Transaction Risk Scoring API Routes
Real-time single transaction scoring and batch scoring endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
import random

from app.schemas import (
    TransactionInput,
    RiskScoreResponse,
    BatchScoreRequest,
    BatchScoreResponse
)
from app.pipeline import engine

router = APIRouter(prefix="/score", tags=["Scoring Engine"])


@router.post("", response_model=RiskScoreResponse, summary="Real-time Transaction Risk Scoring")
async def score_transaction(payload: TransactionInput):
    """
    Evaluates a financial transaction in real-time (<50ms latency SLA)
    using the hybrid XGBoost-SVM anomaly detection pipeline.
    Returns calibrated risk score (0-100), decision, and explainability factors.
    """
    if not engine.loaded:
        raise HTTPException(status_code=503, detail="Model pipeline is not yet initialized.")
    
    return engine.score(payload)


@router.post("/batch", response_model=BatchScoreResponse, summary="Batch Transaction Scoring")
async def batch_score_transactions(payload: BatchScoreRequest):
    """
    Processes and scores multiple transactions concurrently.
    """
    if not engine.loaded:
        raise HTTPException(status_code=503, detail="Model pipeline is not yet initialized.")

    t0 = time.perf_counter()
    results: List[RiskScoreResponse] = []
    high_count = 0
    review_count = 0
    approved_count = 0

    for tx in payload.transactions:
        res = engine.score(tx)
        results.append(res)
        if res.decision == "DECLINE":
            high_count += 1
        elif res.decision == "REVIEW":
            review_count += 1
        else:
            approved_count += 1

    total_time_ms = (time.perf_counter() - t0) * 1000.0
    avg_latency = round(total_time_ms / max(1, len(payload.transactions)), 2)

    return BatchScoreResponse(
        total_processed=len(payload.transactions),
        high_risk_count=high_count,
        review_count=review_count,
        approved_count=approved_count,
        avg_latency_ms=avg_latency,
        results=results
    )


@router.get("/simulate", response_model=RiskScoreResponse, summary="Generate & Score Synthetic Transaction")
async def simulate_transaction(scenario: str = "random"):
    """
    Generates a realistic transaction based on scenario: 'legit', 'velocity_attack', 'crypto_heist', 'credential_stuffing', or 'random'.
    """
    if not engine.loaded:
        raise HTTPException(status_code=503, detail="Model pipeline is not yet initialized.")

    if scenario == "random":
        scenario = random.choice(["legit", "velocity_attack", "crypto_heist", "credential_stuffing"])

    if scenario == "velocity_attack":
        tx = TransactionInput(
            user_id="usr_sim_vel",
            amount=round(random.uniform(450.0, 1850.0), 2),
            channel="WEB",
            merchant_category="electronics",
            velocity_1h=random.randint(4, 7),
            velocity_24h=random.randint(8, 14),
            cumulative_spend_24h=3800.0,
            amount_to_avg_ratio=8.5,
            is_new_device=1,
            failed_pin_attempts=0
        )
    elif scenario == "crypto_heist":
        tx = TransactionInput(
            user_id="usr_sim_crypto",
            amount=round(random.uniform(1500.0, 4800.0), 2),
            channel="API",
            merchant_category="crypto_exchange",
            velocity_1h=2,
            velocity_24h=4,
            amount_to_avg_ratio=18.0,
            is_foreign_transaction=1,
            is_new_device=1,
            failed_pin_attempts=1
        )
    elif scenario == "credential_stuffing":
        tx = TransactionInput(
            user_id="usr_sim_cred",
            amount=round(random.uniform(300.0, 1200.0), 2),
            channel="WEB",
            merchant_category="p2p_transfer",
            failed_pin_attempts=3,
            is_new_device=1,
            amount_to_avg_ratio=5.2
        )
    else:  # legit
        cats = ["grocery", "dining", "gas_station", "clothing"]
        chans = ["POS_CHIP", "POS_SWIPE", "MOBILE_APP"]
        tx = TransactionInput(
            user_id="usr_sim_legit",
            amount=round(random.uniform(12.50, 95.0), 2),
            channel=random.choice(chans),
            merchant_category=random.choice(cats),
            velocity_1h=0,
            velocity_24h=1,
            amount_to_avg_ratio=round(random.uniform(0.4, 1.3), 2),
            is_foreign_transaction=0,
            is_new_device=0,
            failed_pin_attempts=0,
            distance_from_home_km=random.uniform(1.2, 12.0)
        )

    return engine.score(tx)
