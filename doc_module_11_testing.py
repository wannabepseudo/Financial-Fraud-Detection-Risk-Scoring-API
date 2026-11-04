"""
Module 11: Automated Testing, SLA Benchmarks & Quality Assurance (tests)
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_test_model, raw_test_api):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    h_model = pygments.highlight(raw_test_model, PythonLexer(), formatter)
    h_api = pygments.highlight(raw_test_api, PythonLexer(), formatter)
    
    return f"""
<h1>Module 11: Automated Testing, SLA Benchmarks &amp; Quality Assurance</h1>

<h2>11.1 The Testing Pyramid for Real-Time Financial Microservices</h2>
<p>
Financial APIs demand rigorous automated verification. A software defect or latency spike in a banking service can cause cascading payment authorization timeouts. The project's automated test suite combines:
</p>
<ol>
    <li><strong>Pipeline Unit Tests (<code>tests/test_model.py</code>):</strong> Validates model artifact loading, deterministic decision thresholds, risk tier boundaries, explainability factor generation, and single-inference SLA benchmarks.</li>
    <li><strong>Integration &amp; API Tests (<code>tests/test_api.py</code>):</strong> Uses Starlette's <code>TestClient</code> to verify HTTP status codes, Pydantic input validation rejections, batch scoring aggregation, and custom response latency headers.</li>
</ol>

<h2>11.2 Complete Source Code: tests/test_model.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>tests/test_model.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_model}
</div>

<h3>Walkthrough: tests/test_model.py</h3>
<ul>
    <li><code>test_engine_loaded()</code>: Asserts that <code>engine.loaded</code> is True and that the XGBoost classifier, Support Vector Machine, and ColumnTransformer are non-null.</li>
    <li><code>test_legitimate_transaction_scoring()</code>: Feeds a standard $42.50 grocery transaction conducted via POS chip near home. Asserts <code>decision == "APPROVE"</code>, <code>risk_score &lt; 35.0</code>, and <code>latency &lt; 50.0 ms</code>.</li>
    <li><code>test_blatant_fraud_scoring()</code>: Feeds a high-risk multi-vector attack ($3,850 API transfer to a crypto exchange at 2:00 AM from a new foreign device with 3 failed PIN attempts). Asserts <code>decision == "DECLINE"</code>, <code>risk_score &ge; 70.0</code>, and ensures at least 2 explainability reason codes are populated.</li>
    <li><code>test_sub_50ms_latency_sla_benchmark()</code>: Executes 50 consecutive single inferences, asserting that <strong>100% of requests complete under the strict 50.0 ms SLA threshold</strong> (average measured latency: 3.16 ms).</li>
</ul>

<h2>11.3 Complete Source Code: tests/test_api.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>tests/test_api.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_api}
</div>

<h3>Walkthrough: tests/test_api.py</h3>
<ul>
    <li><code>test_health_check_endpoint()</code>: Verifies <code>GET /health</code> returns HTTP 200, status "HEALTHY", and SLA target 50.0 ms.</li>
    <li><code>test_score_single_transaction_endpoint()</code>: Sends a JSON POST payload to <code>/api/v1/score</code>, asserting response structure and confirming that the response header <code>X-SLA-Status</code> equals <code>"PASS"</code>.</li>
    <li><code>test_batch_score_endpoint()</code>: Submits a batch of 2 transactions and asserts that <code>total_processed == 2</code> and <code>avg_latency_ms &lt; 50.0</code>.</li>
    <li><code>test_metrics_endpoint()</code>: Validates that <code>GET /api/v1/metrics</code> returns model evaluation statistics with <code>auc_roc &ge; 0.90</code> and <code>precision &ge; 0.85</code>.</li>
    <li><code>test_sql_query_execution_endpoint()</code>: Asserts that <code>POST /api/v1/sql/execute</code> successfully runs the merchant category risk aggregation query.</li>
    <li><code>test_serve_dashboard()</code>: Asserts that the root path <code>GET /</code> returns the interactive HTML dashboard.</li>
</ul>

<div class="callout callout-success">
    <div class="callout-title">Automated Test Execution Summary</div>
    Running <code>python -m pytest tests -v</code> produces:
    <pre><code>tests/test_api.py::test_health_check_endpoint PASSED                     [ 10%]
tests/test_api.py::test_score_single_transaction_endpoint PASSED         [ 20%]
tests/test_api.py::test_batch_score_endpoint PASSED                      [ 30%]
tests/test_api.py::test_metrics_endpoint PASSED                          [ 40%]
tests/test_api.py::test_sql_query_execution_endpoint PASSED              [ 50%]
tests/test_api.py::test_serve_dashboard PASSED                           [ 60%]
tests/test_model.py::TestFraudModel::test_blatant_fraud_scoring PASSED   [ 70%]
tests/test_model.py::TestFraudModel::test_engine_loaded PASSED           [ 80%]
tests/test_model.py::TestFraudModel::test_legitimate_transaction_scoring PASSED [ 90%]
tests/test_model.py::TestFraudModel::test_sub_50ms_latency_sla_benchmark PASSED [100%]
======================== 10 passed in 3.73s ========================</code></pre>
</div>
"""
