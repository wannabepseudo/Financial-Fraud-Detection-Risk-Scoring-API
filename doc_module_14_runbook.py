"""
Module 14: Production Operations Runbook & Quickstart Verification
"""

def get_content():
    return """
<h1>Module 14: Production Operations Runbook &amp; Quickstart Verification</h1>

<h2>14.1 Step-by-Step Local Setup &amp; Reproduction</h2>
<p>
To spin up the complete microservice from scratch on a new developer workstation or CI/CD runner:
</p>

<h3>1. Environment Setup</h3>
<pre><code># 1. Clone repository and navigate to directory
git clone https://github.com/wannabepseudo/Financial-Fraud-Detection-Risk-Scoring-API.git
cd Financial-Fraud-Detection-Risk-Scoring-API

# 2. Create virtual environment and install pinned dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt</code></pre>

<h3>2. Data Synthesis, Model Training &amp; EDA</h3>
<pre><code># 3. Generate 45,000 synthetic banking records with realistic class imbalance
python data/generate_synthetic_data.py

# 4. Train XGBoost + SVM hybrid ensemble and calibrate decision threshold
python models/train.py

# 5. Generate high-resolution EDA plots for cybersecurity dashboard
python eda/run_eda.py</code></pre>

<h3>3. Automated Testing &amp; Verification</h3>
<pre><code># 6. Execute full automated test suite (verifying routes and sub-50ms SLA)
python -m pytest tests -v</code></pre>

<h3>4. Launching the Microservice</h3>
<pre><code># 7. Start FastAPI ASGI server with auto-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload</code></pre>
<p>
Access points:
</p>
<ul>
    <li><strong>Interactive Web Dashboard:</strong> <a href="http://localhost:8000">http://localhost:8000</a></li>
    <li><strong>Interactive Swagger / OpenAPI Docs:</strong> <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></li>
    <li><strong>Health Check Endpoint:</strong> <a href="http://localhost:8000/health">http://localhost:8000/health</a></li>
</ul>

<h2>14.2 Production Verification: cURL Command Suite</h2>

<h3>1. Normal Everyday Purchase (Expected: APPROVE)</h3>
<pre><code>curl -X POST "http://localhost:8000/api/v1/score" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 28.50,
    "channel": "POS_CHIP",
    "merchant_category": "grocery",
    "velocity_1h": 0,
    "is_new_device": 0
  }'</code></pre>
<p>
<strong>Expected Output:</strong> <code>"decision": "APPROVE", "risk_score": 3.8, "risk_tier": "LOW", "inference_latency_ms": 2.95</code>.
</p>

<h3>2. Multi-Vector Attack (Expected: DECLINE)</h3>
<pre><code>curl -X POST "http://localhost:8000/api/v1/score" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 3450.00,
    "channel": "API",
    "merchant_category": "crypto_exchange",
    "velocity_1h": 5,
    "is_foreign_transaction": 1,
    "failed_pin_attempts": 3,
    "is_new_device": 1
  }'</code></pre>
<p>
<strong>Expected Output:</strong> <code>"decision": "DECLINE", "risk_score": 93.6, "risk_tier": "CRITICAL", "risk_factors": ["VELOCITY_SPIKE", "UNRECOGNIZED_FOREIGN_DEVICE", "CREDENTIAL_RISK", "HIGH_RISK_MERCHANT"]</code>.
</p>

<h2>14.3 Production Operations &amp; Monitoring Checklist</h2>
<table>
    <thead>
        <tr>
            <th>Operational Pillar</th>
            <th>Production Best Practice</th>
            <th>Monitoring Metric / Alert Threshold</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Latency SLA Monitoring</strong></td>
            <td>Export <code>X-Response-Time-Ms</code> to Prometheus / Datadog via Datadog Agent or OpenTelemetry middleware.</td>
            <td>Alert if P95 latency exceeds <strong>25.0 ms</strong> (50% of the 50ms SLA ceiling) for &gt;2 consecutive minutes.</td>
        </tr>
        <tr>
            <td><strong>Model Drift &amp; Retraining</strong></td>
            <td>Schedule continuous model retraining pipelines (e.g., weekly Airflow / Kubeflow DAGs) using recent chargeback settlements.</td>
            <td>Trigger emergency retraining if Population Stability Index (PSI) &gt; 0.20 or evaluation AUC-ROC drops below <strong>90.0%</strong>.</td>
        </tr>
        <tr>
            <td><strong>Security &amp; Rate Limiting</strong></td>
            <td>Enable <code>ENABLE_API_KEY_AUTH = True</code> in <code>app/config.py</code> and terminate TLS/HTTPS at the API Gateway (AWS ALB / Cloudflare).</td>
            <td>Enforce rate-limiting (e.g., 200 requests/sec per API key) using Redis Token Bucket middleware.</td>
        </tr>
        <tr>
            <td><strong>Database Maintenance</strong></td>
            <td>For high-volume SQLite deployments, run <code>PRAGMA wal_autocheckpoint</code> and daily <code>VACUUM</code>; for enterprise clusters, transition to PostgreSQL read-replicas.</td>
            <td>Monitor database lock wait time; alert if SQLite file lock contention &gt; 5 ms.</td>
        </tr>
    </tbody>
</table>

<div style="margin-top: 40px; text-align: center; border-top: 1px solid #cbd5e1; padding-top: 20px; font-size: 8.5pt; color: #64748b;">
    <strong>Financial Fraud Detection &amp; Risk Scoring API 2026</strong> &mdash; Built for High-Throughput Fintech Security &amp; Real-Time Risk Intelligence.
</div>

</body>
</html>
"""
