"""
Module 3: Complex SQL Analytical Feature Engineering (queries.sql)
"""
import pygments
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_sql):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    highlighted_sql = pygments.highlight(raw_sql, SqlLexer(), formatter)
    
    return f"""
<h1>Module 03: Complex SQL Analytical Feature Engineering</h1>

<h2>3.1 Feature Engineering Paradigms: Why SQL Window Functions?</h2>
<p>
Feature engineering for fraud detection requires computing time-series velocities and deviations from historical baselines. There are three primary paradigms for computing these features:
</p>

<table>
    <thead>
        <tr>
            <th>Feature Engineering Approach</th>
            <th>Data Consistency</th>
            <th>Computational Efficiency</th>
            <th>Operational Complexity</th>
            <th>Trade-Off Verdict</th>
        </tr>
    </thead>
    <tbody>
        <tr class="comparison-winner">
            <td><strong>In-Database SQL Window Functions (Chosen)</strong></td>
            <td>Absolute consistency; reads directly from the transactional system of record without replication lag.</td>
            <td>Execution pushed down to database engine; leverages composite B-tree indexes; zero memory serialization.</td>
            <td>Low; requires no external services or intermediate cache management.</td>
            <td><strong>Optimal:</strong> Guaranteed consistency between historical training extraction and online live feature inspection.</td>
        </tr>
        <tr>
            <td><strong>Application-Level Pandas in Python</strong></td>
            <td>Prone to train-serving skew if online Python code diverges from offline extraction logic.</td>
            <td>Requires pulling thousands of raw rows into Python process memory before aggregation, causing high GC overhead.</td>
            <td>Medium; requires loading raw historical frames per request.</td>
            <td><strong>Sub-optimal for serving:</strong> High latency and memory overhead on high-throughput microservices.</td>
        </tr>
        <tr>
            <td><strong>Streaming Feature Store (Feast / Flink / Kafka)</strong></td>
            <td>Requires complex synchronization between batch lakehouse (Snowflake/BigQuery) and key-value store (Redis).</td>
            <td>Sub-millisecond reads from pre-aggregated Redis keys, but requires continuous background stream workers.</td>
            <td>Very High; introduces multiple distributed systems, Zookeeper, Kafka clusters, and pipeline maintenance.</td>
            <td><strong>Overkill:</strong> Unnecessary infrastructural cost and operational complexity for single-node to moderate clusters.</td>
        </tr>
    </tbody>
</table>

<h2>3.2 Complete Source Code: data/queries.sql</h2>
<div class="code-container">
    <div class="code-header">
        <span>data/queries.sql</span>
        <span class="lang-badge">SQL</span>
    </div>
    {highlighted_sql}
</div>

<h2>3.3 Brick-by-Brick Line &amp; Query Analysis</h2>

<h3>Query 1: Automated Rolling Window Feature Extraction (Lines 6–90)</h3>
<p>
This analytical query generates the feature matrix for both machine learning training and online customer verification. It utilizes Common Table Expressions (CTEs) to isolate historical aggregations from real-time sliding windows.
</p>

<h4>1. CTE `UserHistoricalBaselines` (Lines 8–17)</h4>
<ul>
    <li>Computes the customer's 30-day baseline average transaction amount (<code>AVG(amount) AS avg_historical_amount_30d</code>) and total 30-day volume.</li>
    <li><code>WHERE epoch_timestamp >= (strftime('%s', 'now') - 2592000)</code>: Restricts the historical calculation to exactly 30 days (2,592,000 seconds). This ensures seasonal drift does not distort the baseline.</li>
</ul>

<h4>2. CTE `RecentVelocity` (Lines 18–55)</h4>
<p>
This section demonstrates the power of ANSI SQL window functions:
</p>
<ul>
    <li><strong>Rolling 1-Hour Velocity (Lines 33–37):</strong>
        <pre><code>COUNT(*) OVER (
    PARTITION BY t.user_id 
    ORDER BY t.epoch_timestamp 
    RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
) - 1 AS velocity_1h</code></pre>
        <strong>Mathematical Mechanism:</strong> For every transaction, the database engine partitions the stream by <code>user_id</code> and counts all rows whose <code>epoch_timestamp</code> falls in the closed interval $[t - 3600, t]$. Subtracting 1 removes the current transaction itself. This isolates rapid-fire card testing bursts.
    </li>
    <li><strong>Rolling 24-Hour Velocity &amp; Cumulative Spend (Lines 39–49):</strong>
        Calculates cumulative 24-hour frequency (interval $[t - 86400, t]$) and total dollar expenditure (<code>SUM(t.amount)</code>). A customer spending 10x their normal daily budget within a 24-hour cycle is an immediate indicator of account compromise.
    </li>
    <li><strong>Lagged Geospatial Tracking (Lines 51–53):</strong>
        Uses <code>LAG(t.geo_lat, 1) OVER (PARTITION BY t.user_id ORDER BY t.epoch_timestamp)</code> to retrieve the physical location and timestamp of the customer's preceding transaction.
    </li>
</ul>

<h4>3. Final Feature Projection &amp; Spherical Trigonometry (Lines 56–90)</h4>
<ul>
    <li><strong>Spending Deviation Ratio (Line 66):</strong>
        <code>ROUND(v.amount / NULLIF(b.avg_historical_amount_30d, 0), 2) AS amount_to_avg_ratio_30d</code><br>
        Normalizes transaction amount against individual customer habit. Using <code>NULLIF(..., 0)</code> prevents mathematical division-by-zero errors on newly registered accounts.
    </li>
    <li><strong>Pure SQL Haversine Distance Formula (Lines 73–81):</strong>
        <p>Computes the great-circle distance (in kilometers) between two coordinates on the Earth's surface (radius R = 6,371 km):</p>
        <p style="font-family: monospace; font-size: 10pt; background: #f8fafc; padding: 8px; border-radius: 4px;">d = 2R * arcsin(sqrt(sin^2(&Delta;&phi;/2) + cos(&phi;_1) * cos(&phi;_2) * sin^2(&Delta;&lambda;/2)))</p>
        Where &phi; is latitude in radians and &lambda; is longitude in radians. This formula is implemented directly within ANSI SQL mathematical functions (<code>SIN</code>, <code>COS</code>, <code>RADIANS</code>, <code>ASIN</code>, <code>POWER</code>, <code>SQRT</code>), calculating exact distance from the customer's registered home coordinates.
    </li>
</ul>

<h3>Query 2: High-Risk Category &amp; Hourly Anomaly Aggregation (Lines 92–104)</h3>
<p>
Aggregates macro-level merchant industry performance:
</p>
<ul>
    <li>Calculates the empirical fraud rate percentage per category: <code>ROUND(100.0 * SUM(t.is_fraud) / COUNT(t.transaction_id), 2)</code>.</li>
    <li>Enables the system to discover high-risk sectors (e.g., <code>crypto_exchange</code> with 28%+ chargeback frequency vs. <code>grocery</code> with &lt;0.5%).</li>
</ul>

<h3>Query 3: Impossible Travel Speed Anomaly Detector (Lines 107–150)</h3>
<div class="callout callout-warning">
    <div class="callout-title">The Physics of Impossible Travel Detection</div>
    Fraud rings frequently use stolen session tokens across geographically dispersed proxy endpoints. Query 3 models physical travel dynamics:
    <ol>
        <li>Retrieves consecutive transaction timestamps (t1, t2) and coordinates ((lat1, lon1), (lat2, lon2)) using the <code>LAG()</code> window function.</li>
        <li>Computes elapsed time in hours: &Delta;t = (t2 - t1) / 3600.0.</li>
        <li>Computes great-circle displacement &Delta;d in kilometers via the Haversine formula.</li>
        <li>Calculates implied velocity: v = &Delta;d / &Delta;t.</li>
        <li>Applies the anomaly filter: <code>HAVING implied_speed_kmh > 800.0 AND time_delta_hours &lt; 4.0</code>. Commercial passenger jetliners cruise at ~800–900 km/h. Any consecutive transaction pair exceeding 800 km/h represents either account credential sharing, compromised proxy networks, or automated fraud bots.</li>
    </ol>
</div>
"""
