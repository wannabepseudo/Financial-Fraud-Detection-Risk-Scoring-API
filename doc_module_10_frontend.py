"""
Module 10: Interactive Cybersecurity & Fintech Dashboard (static frontend)
"""

def get_content():
    return """
<h1>Module 10: Interactive Cybersecurity &amp; Fintech Dashboard</h1>

<h2>10.1 UI/UX Architecture: Glassmorphism Cybersecurity HUD</h2>
<p>
The application serves a complete, responsive, single-page application (SPA) directly from FastAPI's static directory (<code>static/index.html</code>, <code>static/css/styles.css</code>, and <code>static/js/app.js</code>). Designed with a modern dark-mode aesthetic (deep slate background <code>#0b0f19</code>, card surfaces <code>#1e293b</code>, and neon telemetry accents), it provides security operations analysts with real-time visibility into the fraud detection engine.
</p>

<h2>10.2 Core Frontend Modules &amp; Engineering Highlights</h2>

<h3>1. The Animated Radial Risk Speedometer</h3>
<p>
The centerpiece of the scoring simulator is a custom SVG radial gauge displaying real-time risk scores (0 to 100):
</p>
<pre><code>&lt;svg viewBox="0 0 200 200" class="gauge-svg"&gt;
  &lt;circle class="gauge-bg" cx="100" cy="100" r="85" /&gt;
  &lt;circle id="gauge-fill" class="gauge-progress" cx="100" cy="100" r="85" /&gt;
&lt;/svg&gt;</code></pre>
<p>
<strong>Mathematical Animation Mechanism:</strong> The gauge's circumference is calculated as $C = 2\\pi r = 2 \\times 3.14159 \\times 85 \\approx 534.07\\text{ px}$. The dash array is initialized to <code>stroke-dasharray: 534</code>. When a transaction is scored:
</p>
$$\\text{offset} = 534 - \\left(\\frac{\\text{risk\\_score}}{100} \\times 534\\right)$$
<p>
Applying CSS transitions on <code>stroke-dashoffset</code> animates the dial with a fluid 800ms ease-out curve. Dynamic threshold logic shifts the dial color smoothly from <strong>Emerald Green (#10b981)</strong> for low-risk approvals, to <strong>Amber (#f59e0b)</strong> for manual review, to <strong>Crimson Red (#ef4444)</strong> for declines.
</p>

<h3>2. Real-Time Transaction Simulation Studio</h3>
<p>
Enables security engineers and fraud analysts to adjust variables in real time:
</p>
<ul>
    <li><strong>Input Controls:</strong> Numerical inputs for transaction amount, dropdowns for payment channel and merchant category, and security toggle checkboxes (<code>New Device</code>, <code>Foreign Origin</code>, <code>Failed PIN Attempts</code>).</li>
    <li><strong>Scenario Presets:</strong> One-click trigger buttons that load realistic attack archetypes:
        <ul>
            <li><code>Legitimate Purchase</code>: $45.00 grocery charge on a trusted chip terminal &rarr; <strong>Risk Score: 4.2 (APPROVE)</strong>.</li>
            <li><code>Velocity Attack</code>: $1,200.00 web purchase with 5 transactions in 1 hour &rarr; <strong>Risk Score: 91.5 (DECLINE)</strong>.</li>
            <li><code>Crypto Heist</code>: $3,800.00 API transfer to crypto exchange on untrusted device &rarr; <strong>Risk Score: 94.8 (DECLINE)</strong>.</li>
            <li><code>Credential Stuffing</code>: $650.00 purchase with 3 consecutive failed PIN attempts &rarr; <strong>Risk Score: 88.2 (DECLINE)</strong>.</li>
        </ul>
    </li>
    <li><strong>Explainability Badges:</strong> The UI parses the API's <code>risk_factors</code> array and dynamically renders colored badges explaining the primary detection triggers.</li>
</ul>

<h3>3. Live Transaction Telemetry Stream</h3>
<p>
Connects to <code>GET /api/v1/analytics/recent</code> to display a live scrolling ledger of payment events. The table surfaces customer IDs, merchant categories, amounts, channel types, and color-coded status badges, mirroring enterprise fraud monitoring consoles.
</p>

<h3>4. Interactive SQL Query Inspector</h3>
<p>
Allows compliance auditors to inspect and execute the production feature engineering queries directly against the live database:
</p>
<ul>
    <li>Auditors can select between <em>Rolling Velocity Windows</em>, <em>Merchant Risk Aggregations</em>, and <em>Impossible Travel Speed Detection</em>.</li>
    <li>Executes <code>POST /api/v1/sql/execute</code> and dynamically generates an HTML table containing the exact analytical output.</li>
</ul>

<h3>5. Model Performance &amp; Evaluation Hub</h3>
<p>
Integrates <strong>Chart.js</strong> to render interactive Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves:
</p>
<ul>
    <li>Fetches downsampled curve coordinate arrays directly from <code>GET /api/v1/metrics</code>.</li>
    <li>Provides interactive hover tooltips displaying the exact False Positive Rate vs. True Positive Rate at every operational threshold.</li>
</ul>
"""
