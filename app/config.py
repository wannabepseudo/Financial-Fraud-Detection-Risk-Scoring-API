"""
Application Configuration Settings
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_TITLE = "Financial Fraud Detection & Risk Scoring API"
APP_VERSION = "2026.1.0"
API_PREFIX = "/api/v1"

# Database & Model Artifacts
DB_PATH = os.path.join(BASE_DIR, "data", "transactions.db")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "models", "model_artifacts")
XGB_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgb_model.joblib")
SVM_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "svm_model.joblib")
PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, "preprocessor.joblib")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Latency & Risk Scoring SLAs
SLA_MAX_LATENCY_MS = 50.0  # Sub-50ms inference requirement
DEFAULT_DECISION_THRESHOLDS = {
    "REVIEW_THRESHOLD": 35.0,  # 35.0 - 70.0 -> Manual Review
    "DECLINE_THRESHOLD": 70.0  # > 70.0 -> Decline / High Risk Fraud
}

# Security
API_KEY = os.getenv("FRAUD_API_KEY", "fraud_sec_live_2026_94auc88prec")
ENABLE_API_KEY_AUTH = False  # Set True for strict production auth mode
