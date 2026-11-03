"""
Unit Tests for Machine Learning Pipeline & Inference Engine
"""

import unittest
import os
import time

from app.pipeline import engine
from app.schemas import TransactionInput


class TestFraudModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        engine.load_artifacts()

    def test_engine_loaded(self):
        self.assertTrue(engine.loaded, "Fraud detection engine failed to load serialized artifacts.")
        self.assertIsNotNone(engine.xgb_model)
        self.assertIsNotNone(engine.svm_model)
        self.assertIsNotNone(engine.preprocessor)

    def test_legitimate_transaction_scoring(self):
        """Normal everyday grocery purchase should receive a LOW risk score and APPROVE decision."""
        legit_tx = TransactionInput(
            user_id="usr_test_legit",
            amount=42.50,
            channel="POS_CHIP",
            merchant_category="grocery",
            hour_of_day=14,
            velocity_1h=0,
            velocity_24h=1,
            distance_from_home_km=3.2,
            is_foreign_transaction=0,
            failed_pin_attempts=0,
            is_new_device=0
        )
        res = engine.score(legit_tx)
        self.assertEqual(res.decision, "APPROVE")
        self.assertEqual(res.risk_tier, "LOW")
        self.assertLess(res.risk_score, 35.0)
        self.assertLess(res.inference_latency_ms, 50.0, "Latency SLA violated (>50ms).")

    def test_blatant_fraud_scoring(self):
        """Multi-vector fraud attack (velocity spike, foreign untrusted device, outlier crypto spend) should DECLINE."""
        fraud_tx = TransactionInput(
            user_id="usr_test_fraud",
            amount=3850.00,
            channel="API",
            merchant_category="crypto_exchange",
            hour_of_day=2,
            velocity_1h=5,
            velocity_24h=8,
            distance_from_home_km=4200.0,
            is_foreign_transaction=1,
            failed_pin_attempts=3,
            is_new_device=1,
            amount_to_avg_ratio=18.0
        )
        res = engine.score(fraud_tx)
        self.assertEqual(res.decision, "DECLINE")
        self.assertIn(res.risk_tier, ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(res.risk_score, 70.0)
        self.assertTrue(len(res.risk_factors) >= 2, "Expected multiple explainability risk factors.")

    def test_sub_50ms_latency_sla_benchmark(self):
        """Benchmark 50 single inferences and verify all finish under 50ms SLA."""
        sample_tx = TransactionInput(
            user_id="usr_bench",
            amount=150.00,
            channel="WEB",
            merchant_category="electronics",
            velocity_1h=1
        )
        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            res = engine.score(sample_tx)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)
            self.assertLess(elapsed_ms, 50.0, f"Latency benchmark exceeded 50ms: {elapsed_ms:.2f}ms")

        avg_lat = sum(latencies) / len(latencies)
        print(f"\n[Test Benchmark] Avg latency across 50 requests: {avg_lat:.2f} ms")


if __name__ == "__main__":
    unittest.main()
