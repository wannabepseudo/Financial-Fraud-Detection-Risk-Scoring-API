"""
Integration Tests for FastAPI Microservice Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["models_loaded"] is True
    assert data["sla_target_ms"] == 50.0


def test_score_single_transaction_endpoint():
    payload = {
        "user_id": "usr_api_test",
        "amount": 25.00,
        "channel": "POS_CHIP",
        "merchant_category": "grocery",
        "velocity_1h": 0,
        "is_foreign_transaction": 0,
        "failed_pin_attempts": 0,
        "is_new_device": 0
    }
    response = client.post("/api/v1/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "decision" in data
    assert "model_breakdown" in data
    assert "inference_latency_ms" in data
    assert data["inference_latency_ms"] < 50.0
    assert response.headers.get("X-SLA-Status") == "PASS"


def test_batch_score_endpoint():
    payload = {
        "transactions": [
            {"amount": 10.0, "channel": "POS_CHIP", "merchant_category": "grocery"},
            {"amount": 4200.0, "channel": "API", "merchant_category": "crypto_exchange", "velocity_1h": 5, "is_new_device": 1}
        ]
    }
    response = client.post("/api/v1/score/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
    assert data["avg_latency_ms"] < 50.0


def test_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["auc_roc"] >= 0.90
    assert data["metrics"]["precision"] >= 0.85


def test_sql_query_execution_endpoint():
    payload = {"query_id": "merchant_risks"}
    response = client.post("/api/v1/sql/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["row_count"] > 0
    assert "merchant_category" in data["columns"]


def test_serve_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "FinSecure AI" in response.text
