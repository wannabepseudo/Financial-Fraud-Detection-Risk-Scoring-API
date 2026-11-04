"""
Module 9: High-Performance FastAPI Microservice & API Routing
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_main, raw_score, raw_analytics, raw_metrics, raw_sql):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    h_main = pygments.highlight(raw_main, PythonLexer(), formatter)
    h_score = pygments.highlight(raw_score, PythonLexer(), formatter)
    h_analytics = pygments.highlight(raw_analytics, PythonLexer(), formatter)
    h_metrics = pygments.highlight(raw_metrics, PythonLexer(), formatter)
    h_sql = pygments.highlight(raw_sql, PythonLexer(), formatter)
    
    return f"""
<h1>Module 09: High-Performance FastAPI Microservice &amp; API Routing</h1>

<h2>9.1 Web Framework Evaluation: Why FastAPI vs Flask &amp; Django?</h2>
<p>
Serving machine learning models in production requires high concurrency, low serialization latency, and asynchronous non-blocking I/O:
</p>

<table>
    <thead>
        <tr>
            <th>Framework</th>
            <th>Concurrency Model</th>
            <th>Type Validation &amp; Docs</th>
            <th>Baseline Routing Latency</th>
            <th>Suitability for ML Microservices</th>
        </tr>
    </thead>
    <tbody>
        <tr class="comparison-winner">
            <td><strong>FastAPI + Uvicorn (Chosen)</strong></td>
            <td>Asynchronous Server Gateway Interface (ASGI) built on <code>uvloop</code> and <code>Starlette</code>; handles thousands of concurrent requests per worker.</td>
            <td>Native Pydantic v2 validation; automatic interactive OpenAPI / Swagger UI generation (<code>/docs</code>).</td>
            <td>Ultra-low (~0.8 ms framework overhead).</td>
            <td><strong>Optimal:</strong> Purpose-built for modern, type-safe, high-throughput microservices.</td>
        </tr>
        <tr>
            <td><strong>Flask (WSGI)</strong></td>
            <td>Synchronous Web Server Gateway Interface (WSGI); blocked worker threads during concurrent requests without Gevent.</td>
            <td>Requires manual validation boilerplate or third-party Marshmallow plugins; manual Swagger configuration.</td>
            <td>Moderate (~2.5 ms framework overhead).</td>
            <td><strong>Sub-optimal:</strong> Slower concurrency scaling and lacks native asynchronous support.</td>
        </tr>
        <tr>
            <td><strong>Django / Django REST Framework</strong></td>
            <td>Monolithic WSGI/ASGI stack with heavy ORM, middleware layers, and template engines.</td>
            <td>Verbose DRF Serializers; high CPU serialization tax on high-frequency payloads.</td>
            <td>High (~6–12 ms framework overhead).</td>
            <td><strong>Excessive Overhead:</strong> Far too heavy and slow for a single-purpose sub-50ms inference microservice.</td>
        </tr>
    </tbody>
</table>

<h2>9.2 Complete Source Code: app/main.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/main.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_main}
</div>

<h3>Walkthrough: app/main.py</h3>
<ul>
    <li><strong>Lifespan Context Manager &amp; Model Warm-Up (Lines 29–44):</strong>
        <pre><code>@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models, scalers, and warm up inference engine
    engine.load_artifacts()
    warmup_tx = TransactionInput(amount=50.0, channel="WEB", merchant_category="grocery")
    _ = engine.score(warmup_tx)</code></pre>
        <em>Engineering Significance:</em> Python's JIT and Scikit-Learn pipelines exhibit a cold-start latency spike on the very first request due to dynamic library loading. By executing a dummy warm-up transaction during server startup, subsequent live customer requests execute in single-digit milliseconds.
    </li>
    <li><strong>SLA Latency Enforcement Middleware (Lines 66–74):</strong>
        Intercepts every inbound HTTP request, calculates total processing duration using high-precision performance timers (<code>time.perf_counter()</code>), and attaches compliance headers:
        <ul>
            <li><code>X-Response-Time-Ms</code>: Exact wall-clock latency (e.g., <code>3.12</code>).</li>
            <li><code>X-SLA-Status</code>: Emits <code>PASS</code> if duration &lt; 50 ms, or <code>WARN</code> if latency exceeds the SLA ceiling.</li>
        </ul>
    </li>
    <li><strong>Health Check Endpoint (Lines 95–105):</strong> Exposes <code>/health</code> returning model readiness and database connectivity for Docker container probes.</li>
</ul>

<h2>9.3 Complete Source Code: app/routes/score.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/routes/score.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_score}
</div>

<h3>Walkthrough: app/routes/score.py</h3>
<ul>
    <li><code>POST /api/v1/score</code>: The primary production scoring endpoint. Validates client payloads and delegates to <code>engine.score()</code> under sub-50ms SLA.</li>
    <li><code>POST /api/v1/score/batch</code>: Iterates and scores transaction arrays, computing aggregate high-risk, review, and approval tallies with batch average latencies.</li>
    <li><code>GET /api/v1/score/simulate</code>: Built-in scenario generator for client demonstrations (e.g., simulating <code>velocity_attack</code>, <code>crypto_heist</code>, <code>credential_stuffing</code>, or <code>legit</code>).</li>
</ul>

<h2>9.4 Complete Source Code: app/routes/analytics.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/routes/analytics.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_analytics}
</div>

<h2>9.5 Complete Source Code: app/routes/metrics.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/routes/metrics.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_metrics}
</div>

<h2>9.6 Complete Source Code: app/routes/sql_inspector.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/routes/sql_inspector.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_sql}
</div>
"""
