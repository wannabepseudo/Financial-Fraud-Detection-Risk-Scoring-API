"""
Real-Time Fraud Inference Pipeline & Anomaly Engine
Loads pre-trained XGBoost and SVM pipelines, executes feature derivation,
scores transactions with sub-50ms latency, and produces explainability factors.
"""

import os
import time
import json
import uuid
import math
import joblib
import numpy as np
import scipy.stats  # SciPy compatibility
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

from app.config import (
    XGB_MODEL_PATH,
    SVM_MODEL_PATH,
    PREPROCESSOR_PATH,
    METRICS_PATH,
    DEFAULT_DECISION_THRESHOLDS
)
from app.schemas import TransactionInput, RiskScoreResponse, RiskFactor
from app.db import get_user_profile_and_velocity

# Category risk lookup table
CATEGORY_RISK_MAP = {
    "grocery": 0.0,
    "dining": 0.0,
    "gas_station": 0.1,
    "pharmacy": 0.0,
    "clothing": 0.1,
    "electronics": 0.5,
    "travel": 0.6,
    "p2p_transfer": 0.85,
    "gambling": 0.90,
    "crypto_exchange": 0.95,
}


class FraudDetectionEngine:
    def __init__(self):
        self.xgb_model = None
        self.svm_model = None
        self.preprocessor = None
        self.metrics = None
        self.loaded = False

    def load_artifacts(self):
        print("[*] Loading machine learning models and preprocessing pipelines...")
        if os.path.exists(XGB_MODEL_PATH):
            self.xgb_model = joblib.load(XGB_MODEL_PATH)
        if os.path.exists(SVM_MODEL_PATH):
            self.svm_model = joblib.load(SVM_MODEL_PATH)
        if os.path.exists(PREPROCESSOR_PATH):
            self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, "r") as f:
                self.metrics = json.load(f)

        self.loaded = (
            self.xgb_model is not None and
            self.svm_model is not None and
            self.preprocessor is not None
        )
        print(f"[+] Model engine initialized. Ready: {self.loaded}")

    def score(self, tx: TransactionInput) -> RiskScoreResponse:
        t_start = time.perf_counter()

        now = datetime.now()
        hour = tx.hour_of_day if tx.hour_of_day is not None else now.hour
        day_of_week = tx.day_of_week if tx.day_of_week is not None else now.weekday()
        sin_hour = np.sin(2 * np.pi * hour / 24.0)
        cos_hour = np.cos(2 * np.pi * hour / 24.0)

        # Baseline & velocity resolution
        user_prof = None
        if tx.user_id and tx.user_id != "usr_demo_customer":
            user_prof = get_user_profile_and_velocity(tx.user_id)

        mean_amt = user_prof["mean_amount"] if user_prof else 75.0
        amt_ratio = (
            tx.amount_to_avg_ratio
            if tx.amount_to_avg_ratio is not None
            else round(tx.amount / max(1.0, mean_amt), 2)
        )

        v1h = tx.velocity_1h if tx.velocity_1h is not None else (user_prof["velocity_1h"] if user_prof else 0)
        v24h = tx.velocity_24h if tx.velocity_24h is not None else (user_prof["velocity_24h"] if user_prof else 1)
        cum_spend = (
            tx.cumulative_spend_24h
            if tx.cumulative_spend_24h is not None
            else tx.amount + (user_prof["cumulative_spend_24h"] if user_prof else 0.0)
        )

        # Distance calculation (Haversine or override)
        geo_lat = getattr(tx, 'geo_lat', None)
        geo_lon = getattr(tx, 'geo_lon', None)
        if tx.distance_from_home_km is not None:
            dist_km = tx.distance_from_home_km
        elif geo_lat is not None and geo_lon is not None and user_prof:
            lat1, lon1 = math.radians(user_prof["home_lat"]), math.radians(user_prof["home_lon"])
            lat2, lon2 = math.radians(geo_lat), math.radians(geo_lon)
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
            dist_km = round(6371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)
        else:
            dist_km = 4500.0 if tx.is_foreign_transaction else 8.5

        # Merchant risk score
        m_risk = (
            tx.merchant_risk_score
            if tx.merchant_risk_score is not None
            else CATEGORY_RISK_MAP.get(tx.merchant_category.lower(), 0.2)
        )

        # Build feature DataFrame matching train pipeline exactly
        feature_dict = {
            'amount': [float(tx.amount)],
            'velocity_1h': [int(v1h)],
            'velocity_24h': [int(v24h)],
            'cumulative_spend_24h': [float(cum_spend)],
            'amount_to_avg_ratio_30d': [float(amt_ratio)],
            'distance_from_home_km': [float(dist_km)],
            'is_foreign_transaction': [int(tx.is_foreign_transaction)],
            'failed_pin_attempts': [int(tx.failed_pin_attempts)],
            'is_new_device': [int(tx.is_new_device)],
            'merchant_risk_score': [float(m_risk)],
            'sin_hour': [float(sin_hour)],
            'cos_hour': [float(cos_hour)],
            'day_of_week': [int(day_of_week)],
            'channel': [str(tx.channel)],
            'merchant_category': [str(tx.merchant_category.lower())]
        }
        df_feat = pd.DataFrame(feature_dict)

        # Preprocessing & Model Inference
        X_proc = self.preprocessor.transform(df_feat)
        prob_xgb = float(self.xgb_model.predict_proba(X_proc)[0, 1])
        prob_svm = float(self.svm_model.predict_proba(X_proc)[0, 1])

        # Hybrid Ensemble Scoring
        ensemble_prob = 0.75 * prob_xgb + 0.25 * prob_svm

        # Calibrate to 0 - 100 Risk Score
        risk_score = round(ensemble_prob * 100.0, 1)

        # Decision & Risk Tier Assignment
        if risk_score >= DEFAULT_DECISION_THRESHOLDS["DECLINE_THRESHOLD"]:
            tier = "CRITICAL" if risk_score >= 85.0 else "HIGH"
            decision = "DECLINE"
        elif risk_score >= DEFAULT_DECISION_THRESHOLDS["REVIEW_THRESHOLD"]:
            tier = "MEDIUM"
            decision = "REVIEW"
        else:
            tier = "LOW"
            decision = "APPROVE"

        # Model Confidence
        confidence = round(max(ensemble_prob, 1.0 - ensemble_prob), 3)

        # Rule-Based Anomaly Explainability Generation
        risk_factors = []
        if v1h >= 3:
            risk_factors.append(RiskFactor(
                factor="VELOCITY_SPIKE",
                severity="HIGH" if v1h < 5 else "CRITICAL",
                description=f"Transaction velocity burst: {v1h} transactions initiated within 60 minutes."
            ))
        if amt_ratio >= 4.0:
            risk_factors.append(RiskFactor(
                factor="OUTLIER_AMOUNT",
                severity="HIGH",
                description=f"Spending deviation: Amount is {amt_ratio:.1f}x higher than customer's 30-day baseline."
            ))
        if tx.failed_pin_attempts >= 2:
            risk_factors.append(RiskFactor(
                factor="CREDENTIAL_RISK",
                severity="HIGH" if tx.failed_pin_attempts == 2 else "CRITICAL",
                description=f"Authentication anomaly: {tx.failed_pin_attempts} consecutive failed PIN/CVV attempts."
            ))
        if tx.is_foreign_transaction and tx.is_new_device:
            risk_factors.append(RiskFactor(
                factor="UNRECOGNIZED_FOREIGN_DEVICE",
                severity="CRITICAL",
                description="Account security: Untrusted device operating outside user home country."
            ))
        elif tx.is_foreign_transaction:
            risk_factors.append(RiskFactor(
                factor="CROSS_BORDER_TRANSACTION",
                severity="MEDIUM",
                description=f"Cross-border transaction detected {dist_km:.0f} km from home location."
            ))
        elif tx.is_new_device:
            risk_factors.append(RiskFactor(
                factor="UNTRUSTED_DEVICE",
                severity="MEDIUM",
                description="Unregistered hardware fingerprint or new browser session."
            ))

        if m_risk >= 0.8:
            risk_factors.append(RiskFactor(
                factor="HIGH_RISK_MERCHANT",
                severity="HIGH",
                description=f"High-risk merchant industry: '{tx.merchant_category}' with elevated chargeback rates."
            ))

        if not risk_factors and tier == "LOW":
            risk_factors.append(RiskFactor(
                factor="STANDARD_BEHAVIOR",
                severity="LOW",
                description="Transaction parameters align with verified customer behavioral profile."
            ))

        latency_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        return RiskScoreResponse(
            transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
            risk_score=risk_score,
            risk_tier=tier,
            decision=decision,
            confidence=confidence,
            model_breakdown={
                "xgboost_probability": round(prob_xgb, 4),
                "svm_probability": round(prob_svm, 4),
                "ensemble_probability": round(ensemble_prob, 4)
            },
            risk_factors=risk_factors,
            inference_latency_ms=latency_ms,
            evaluated_at=datetime.now().isoformat()
        )


# Global Engine Singleton
engine = FraudDetectionEngine()
