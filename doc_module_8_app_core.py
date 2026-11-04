"""
Module 8: Application Configuration, Schemas & DB Connectors (config, schemas, db)
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_config, raw_schemas, raw_db):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    h_config = pygments.highlight(raw_config, PythonLexer(), formatter)
    h_schemas = pygments.highlight(raw_schemas, PythonLexer(), formatter)
    h_db = pygments.highlight(raw_db, PythonLexer(), formatter)
    
    return f"""
<h1>Module 08: Application Configuration, Schemas &amp; DB Connectors</h1>

<h2>8.1 Data Modeling: Why Pydantic v2 vs Dataclasses &amp; Marshmallow?</h2>
<p>
Data validation at microservice boundaries is critical for security and system stability. Below is a comparative evaluation of Python data validation libraries:
</p>

<table>
    <thead>
        <tr>
            <th>Validation Framework</th>
            <th>Runtime Speed &amp; Parsing</th>
            <th>Type Coercion &amp; Constraints</th>
            <th>OpenAPI / JSON Schema Integration</th>
            <th>Microservice Verdict</th>
        </tr>
    </thead>
    <tbody>
        <tr class="comparison-winner">
            <td><strong>Pydantic v2 (Chosen)</strong></td>
            <td>Engineered in pure Rust (<code>pydantic-core</code>); benchmarks 5x to 20x faster than Pydantic v1 and Marshmallow.</td>
            <td>Enforces strict data types, range bounds (<code>gt=0</code>, <code>ge=0, le=23</code>), and regex patterns at sub-millisecond speeds.</td>
            <td>Native automatic generation of OpenAPI 3.1 JSON schemas utilized directly by FastAPI.</td>
            <td><strong>Optimal:</strong> High-throughput request parsing with zero manual validation boilerplate.</td>
        </tr>
        <tr>
            <td><strong>Python <code>@dataclass</code></strong></td>
            <td>Native Python performance, but performs <em>zero</em> runtime validation or type coercion out of the box.</td>
            <td>Requires writing custom <code>__post_init__</code> validation logic for every field constraint.</td>
            <td>No native OpenAPI generation; requires external schema mappers.</td>
            <td><strong>Insufficient:</strong> Lacks defensive validation necessary for hostile external API inputs.</td>
        </tr>
        <tr>
            <td><strong>Marshmallow</strong></td>
            <td>Pure Python implementation; relatively slow serialization and parsing overhead under high concurrency.</td>
            <td>Mature validation schema, but verbose syntax requiring duplicate field definitions.</td>
            <td>Requires third-party extensions (<code>apispec</code>) to generate OpenAPI documentation.</td>
            <td><strong>Legacy:</strong> Superseded by modern typed Pydantic architectures.</td>
        </tr>
    </tbody>
</table>

<h2>8.2 Complete Source Code: app/config.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/config.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_config}
</div>

<h3>Walkthrough: app/config.py</h3>
<p>
<code>app/config.py</code> establishes single-source-of-truth constants:
</p>
<ul>
    <li><code>SLA_MAX_LATENCY_MS = 50.0</code>: Establishes the hard execution ceiling for inference middleware.</li>
    <li><code>DEFAULT_DECISION_THRESHOLDS</code>: Centralizes the operational decision cutoffs (<code>REVIEW_THRESHOLD: 35.0</code>, <code>DECLINE_THRESHOLD: 70.0</code>).</li>
    <li><code>API_KEY</code> &amp; <code>ENABLE_API_KEY_AUTH</code>: Configures production authorization headers via environment variables (<code>FRAUD_API_KEY</code>).</li>
</ul>

<h2>8.3 Complete Source Code: app/schemas.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/schemas.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_schemas}
</div>

<h3>Walkthrough: app/schemas.py</h3>
<p>
Defines strongly typed request/response contracts:
</p>
<ul>
    <li><code>TransactionInput</code>: Accepts client transaction parameters with strict Pydantic Field constraints (e.g., <code>amount: float = Field(..., gt=0)</code> prevents zero or negative charges; <code>hour_of_day: Optional[int] = Field(default=None, ge=0, le=23)</code> restricts hours to valid clock times).</li>
    <li><code>RiskScoreResponse</code>: The response contract delivering <code>risk_score</code>, <code>risk_tier</code>, <code>decision</code>, <code>confidence</code>, <code>model_breakdown</code> (raw XGBoost vs. SVM probabilities), <code>risk_factors</code>, and <code>inference_latency_ms</code>.</li>
    <li><code>BatchScoreRequest</code> &amp; <code>BatchScoreResponse</code>: Enables high-throughput array processing.</li>
</ul>

<h2>8.4 Complete Source Code: app/db.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/db.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {h_db}
</div>

<h3>Walkthrough: app/db.py</h3>
<p>
Provides thread-safe relational database utilities:
</p>
<ul>
    <li><code>get_db_connection()</code>: Returns an active connection with <code>conn.row_factory = sqlite3.Row</code>, allowing dictionary-style key access on SQL result columns.</li>
    <li><code>get_user_profile_and_velocity(user_id)</code>: Queries user registration and calculates 30-day baseline spend in sub-millisecond time. Integrates cold-start fallbacks if a user is not found.</li>
    <li><code>get_analytics_summary()</code>: Executes macro-aggregations across 45,000+ records to power the dashboard metrics counters and category breakdowns.</li>
    <li><code>get_recent_transactions(limit=25)</code>: Fetches the most recent live transactions for the real-time event monitor.</li>
    <li><code>execute_analytical_query(query_id)</code>: Dynamically executes the complex SQL queries defined in Module 03, returning structured column headers and data rows.</li>
</ul>
"""
