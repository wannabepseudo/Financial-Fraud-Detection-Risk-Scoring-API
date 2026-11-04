"""
Module 7: Production Inference Pipeline & Explainability Engine (pipeline.py)
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_py):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    highlighted_py = pygments.highlight(raw_py, PythonLexer(), formatter)
    
    return f"""
<h1>Module 07: Production Inference Pipeline &amp; Explainability Engine</h1>

<h2>7.1 Regulatory Requirements for Machine Learning in Banking</h2>
<p>
In consumer finance, deploying an uninterpretable "black-box" model is legally prohibited in many jurisdictions. Under the <strong>US Fair Credit Reporting Act (FCRA § 615(a))</strong>, the <strong>Equal Credit Opportunity Act (ECOA / Regulation B)</strong>, and the <strong>European Union General Data Protection Regulation (GDPR Article 22)</strong>, any financial institution that rejects or delays a consumer transaction based on automated processing must provide an <strong>Adverse Action Explanation</strong> detailing the primary key factors that led to the decline.
</p>
<p>
The file <code>app/pipeline.py</code> implements the production inference engine. Beyond computing raw classification probabilities, it integrates a deterministic <strong>Explainability Reason Code Generator</strong> that maps mathematical anomaly drivers into human-readable, auditable compliance factors.
</p>

<h2>7.2 Complete Source Code: app/pipeline.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>app/pipeline.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {highlighted_py}
</div>

<h2>7.3 Brick-by-Brick Line &amp; Component Analysis</h2>

<h3>1. Category Risk Mapping (Lines 29–42)</h3>
<p>
<code>CATEGORY_RISK_MAP</code> provides $O(1)$ memory lookup of baseline risk coefficients across 10 industry sectors (e.g., Grocery: 0.0, Gas Station: 0.1, Crypto Exchange: 0.95). When a raw transaction payload arrives without an explicit risk override, this table provides an immediate, calibrated baseline.
</p>

<h3>2. The Engine Singleton Pattern (Lines 44–70 &amp; 238–239)</h3>
<p>
<code>engine = FraudDetectionEngine()</code> initializes a global singleton. Loading machine learning models from disk via <code>joblib.load()</code> takes between 100 ms and 250 ms. Instantiating models once at server startup and holding them in memory ensures zero deserialization overhead during live HTTP requests, preserving the sub-50ms SLA.
</p>

<h3>3. Online Feature Assembly &amp; Cold-Start Handling (Lines 71–140)</h3>
<p>
When an incoming JSON payload arrives at <code>score(tx)</code>:
</p>
<ul>
    <li><strong>Temporal Clock Resolution (Lines 74–79):</strong> Resolves <code>hour_of_day</code> and <code>day_of_week</code>, falling back to current system time if omitted, and computes unit-circle trigonometric projections (sin, cos).</li>
    <li><strong>Database Profile Lookup (Lines 81–98):</strong> If a valid customer ID is provided, the engine queries SQLite (<code>get_user_profile_and_velocity</code>) to fetch historical 30-day baseline spend (&mu;) and rolling velocities.</li>
    <li><strong>Cold-Start Resilience:</strong> If the customer is newly registered or unregistered (<code>usr_demo_customer</code>), the engine applies safe, calibrated population medians (&mu; = $75.00, v_1h = 0, v_24h = 1), preventing crash exceptions.</li>
    <li><strong>Geospatial Haversine Resolution (Lines 100–113):</strong> Dynamically calculates distance from the customer's registered billing coordinates. If coordinates are omitted, foreign transaction flags apply realistic fallback distances (4,500 km vs 8.5 km).</li>
    <li><strong>Exact Feature Alignment (Lines 122–140):</strong> Packs features into a single-row Pandas DataFrame whose column schema matches the preprocessor's expected matrix.</li>
</ul>

<h3>4. Hybrid Inference &amp; Risk Calibration (Lines 142–150)</h3>
<pre><code># Preprocessing & Model Inference
X_proc = self.preprocessor.transform(df_feat)
prob_xgb = float(self.xgb_model.predict_proba(X_proc)[0, 1])
prob_svm = float(self.svm_model.predict_proba(X_proc)[0, 1])

# Hybrid Ensemble Scoring (75% XGBoost + 25% SVM)
ensemble_prob = 0.75 * prob_xgb + 0.25 * prob_svm

# Calibrate to 0 - 100 Risk Score
risk_score = round(ensemble_prob * 100.0, 1)</code></pre>
<p>
The ensemble transforms high-dimensional transactional attributes into an intuitive, normalized <strong>Risk Score between 0.0 and 100.0</strong>.
</p>

<h3>5. Decision Tier Assignment (Lines 152–165)</h3>
<p>
Transactions are routed into three operational actions based on production thresholds:
</p>
<table>
    <thead>
        <tr>
            <th>Risk Score Range</th>
            <th>Risk Tier</th>
            <th>Recommended Decision</th>
            <th>Operational Workflow</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>0.0 – 34.9</strong></td>
            <td><span class="badge badge-pass">LOW</span></td>
            <td><strong>APPROVE</strong></td>
            <td>Frictionless real-time authorization; zero user disruption.</td>
        </tr>
        <tr>
            <td><strong>35.0 – 69.9</strong></td>
            <td><span class="badge badge-warn">MEDIUM</span></td>
            <td><strong>REVIEW</strong></td>
            <td>Step-up authentication required (SMS OTP or Push 3D-Secure challenge).</td>
        </tr>
        <tr>
            <td><strong>70.0 – 100.0</strong></td>
            <td><span class="badge badge-crit">HIGH / CRITICAL</span></td>
            <td><strong>DECLINE</strong></td>
            <td>Immediate transaction termination; account placed on security alert.</td>
        </tr>
    </tbody>
</table>

<h3>6. Rule-Based Explainability Generation (Lines 166–218)</h3>
<p>
To satisfy FCRA and GDPR compliance, Lines 167–218 inspect the primary behavioral drivers:
</p>
<ul>
    <li><code>VELOCITY_SPIKE</code>: Triggered when v_1h &ge; 3, notifying analysts of automated testing bursts.</li>
    <li><code>OUTLIER_AMOUNT</code>: Triggered when amount / &mu; &ge; 4.0, explaining severe deviation from customer habits.</li>
    <li><code>CREDENTIAL_RISK</code>: Generated when failed PIN attempts &ge; 2.</li>
    <li><code>UNRECOGNIZED_FOREIGN_DEVICE</code>: Indicates simultaneous untrusted hardware and overseas origin.</li>
    <li><code>HIGH_RISK_MERCHANT</code>: Highlights high-risk industry exposure (e.g., crypto exchange).</li>
    <li><code>STANDARD_BEHAVIOR</code>: Emitted on low-risk transactions confirming verified baseline alignment.</li>
</ul>
"""
