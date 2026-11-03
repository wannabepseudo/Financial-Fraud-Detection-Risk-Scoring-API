"""
Pydantic Schemas for Request & Response Data Validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TransactionInput(BaseModel):
    user_id: Optional[str] = Field(default="usr_demo_customer", description="Customer ID")
    amount: float = Field(..., gt=0, description="Transaction amount in USD", json_schema_extra={"example": 249.99})
    channel: str = Field(default="WEB", description="Payment channel: POS_CHIP, POS_SWIPE, WEB, MOBILE_APP, ATM, API")
    merchant_category: str = Field(default="electronics", description="Merchant category (e.g. grocery, electronics, crypto_exchange, travel)")
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of transaction (0-23). Defaults to current hour.")
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6, description="Day of week (0=Mon, 6=Sun). Defaults to current day.")
    geo_lat: Optional[float] = Field(default=None, description="Transaction latitude coordinate")
    geo_lon: Optional[float] = Field(default=None, description="Transaction longitude coordinate")
    
    # Behavioral and velocity overrides (optional; automatically derived from SQL DB if omitted)
    velocity_1h: Optional[int] = Field(default=None, ge=0, description="Rolling 1-hour transaction count for user")
    velocity_24h: Optional[int] = Field(default=None, ge=0, description="Rolling 24-hour transaction count for user")
    cumulative_spend_24h: Optional[float] = Field(default=None, ge=0.0, description="Cumulative spend in last 24h")
    amount_to_avg_ratio: Optional[float] = Field(default=None, ge=0.0, description="Ratio of amount to user's 30d baseline average")
    distance_from_home_km: Optional[float] = Field(default=None, ge=0.0, description="Distance from registered home coordinate in km")
    
    # Security anomaly flags
    is_foreign_transaction: int = Field(default=0, ge=0, le=1, description="1 if transaction originated outside user home country")
    failed_pin_attempts: int = Field(default=0, ge=0, description="Count of failed PIN/CVV attempts in last 24h")
    is_new_device: int = Field(default=0, ge=0, le=1, description="1 if device fingerprint is untrusted or unseen")
    merchant_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Merchant historical risk weight (0.0=Low, 1.0=High)")


class RiskFactor(BaseModel):
    factor: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    description: str


class RiskScoreResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., description="Calibrated risk score between 0.0 and 100.0")
    risk_tier: str = Field(..., description="Risk Tier: LOW, MEDIUM, HIGH, CRITICAL")
    decision: str = Field(..., description="Action recommendation: APPROVE, REVIEW, DECLINE")
    confidence: float = Field(..., description="Model certainty confidence level (0.0 to 1.0)")
    model_breakdown: Dict[str, float] = Field(..., description="Raw probability contributions from XGBoost & SVM")
    risk_factors: List[RiskFactor] = Field(default=[], description="Primary behavioral risk drivers detected")
    inference_latency_ms: float = Field(..., description="Execution time in milliseconds (< 50ms)")
    evaluated_at: str


class BatchScoreRequest(BaseModel):
    transactions: List[TransactionInput]


class BatchScoreResponse(BaseModel):
    total_processed: int
    high_risk_count: int
    review_count: int
    approved_count: int
    avg_latency_ms: float
    results: List[RiskScoreResponse]


class ModelMetricsResponse(BaseModel):
    model_name: str
    timestamp: str
    dataset_total_samples: int
    dataset_fraud_samples: int
    dataset_fraud_rate_pct: float
    metrics: Dict[str, Any]
    latency_benchmark_ms: Dict[str, Any]
    top_features: List[Dict[str, Any]]
    curves: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    database_connected: bool
    sla_target_ms: float
    timestamp: str


class SQLQueryRequest(BaseModel):
    query_id: str = Field(..., description="Query ID: 'rolling_velocities', 'merchant_risks', 'impossible_travel'")
