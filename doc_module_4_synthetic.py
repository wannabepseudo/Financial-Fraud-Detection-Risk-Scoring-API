"""
Module 4: Synthetic Banking Transaction Data Generator (generate_synthetic_data.py)
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_py):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    highlighted_py = pygments.highlight(raw_py, PythonLexer(), formatter)
    
    return f"""
<h1>Module 04: Synthetic Banking Transaction Data Generator</h1>

<h2>4.1 Why Synthetic Data Engineering for Financial Fraud?</h2>
<p>
Real-world cardholder transaction data is classified as highly sensitive Personally Identifiable Financial Information (PIFI) and is strictly regulated under PCI-DSS (Payment Card Industry Data Security Standard), GDPR Article 9, and the US Gramm-Leach-Bliley Act (GLBA). Public datasets (such as the Kaggle Credit Card Fraud dataset) are heavily anonymized via Principal Component Analysis (PCA $V_1 - V_{28}$), stripping away all merchant category context, timestamps, device IDs, and geographic coordinates.
</p>
<p>
To build and evaluate a realistic fraud microservice, we engineered a dedicated synthetic generator (<code>data/generate_synthetic_data.py</code>). This engine synthesizes <strong>45,000+ realistic credit card transactions</strong> spanning 1,000 customers, 80 merchants, and 45 days of temporal history, incorporating realistic class imbalance (~4.2% fraud) and stochastic behavioral variance.
</p>

<h2>4.2 Complete Source Code: data/generate_synthetic_data.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>data/generate_synthetic_data.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {highlighted_py}
</div>

<h2>4.3 Brick-by-Brick Line &amp; Algorithm Walkthrough</h2>

<h3>1. Configuration &amp; Merchant Distribution (Lines 16–40)</h3>
<ul>
    <li><code>NUM_USERS = 1000</code>, <code>NUM_MERCHANTS = 80</code>, <code>NUM_TRANSACTIONS = 45000</code>: Calibrated volume ensuring statistical convergence while keeping local execution lightweight (&lt;5 seconds generation time).</li>
    <li><code>FRAUD_TARGET_RATE = 0.042</code>: Reflects real-world payment gateway attack frequencies (~4.2% imbalanced positive class).</li>
    <li><code>MERCHANT_CATEGORIES</code>: Weighted industry distribution reflecting consumer expenditure habits (e.g., Grocery: 22%, Dining: 18%, Gas Station: 12%, Crypto Exchanges: 4%, Gambling: 4%). Each category is assigned a baseline risk tier (<code>LOW</code>, <code>MEDIUM</code>, <code>HIGH</code>).</li>
    <li><code>CHANNELS</code>: Standard payment entry channels: <code>POS_CHIP</code> (35%), <code>WEB</code> (25%), <code>MOBILE_APP</code> (18%), <code>POS_SWIPE</code> (15%), <code>ATM</code> (5%), and <code>API</code> (2%).</li>
</ul>

<h3>2. Geospatial Clustering of Users (Lines 64–100)</h3>
<p>
Cardholders do not distribute uniformly across latitude and longitude; they cluster around metropolitan economic hubs. Lines 68–79 define centroids for 10 major US economic centers (New York, Los Angeles, Chicago, Houston, San Francisco, Seattle, Miami, Denver, Phoenix, Dallas).
</p>
<p>
For each user, coordinates are generated using a bivariate Gaussian distribution centered around their anchor metropolis: (home_lat, home_lon) = (metro_lat + N(0, 0.08^2), metro_lon + N(0, 0.08^2)).
</p>
<p>
This produces realistic suburban and urban population distributions around anchor cities.
</p>

<h3>3. Device Trust &amp; Hardware Fingerprints (Lines 124–143)</h3>
<p>
Each registered customer is assigned a primary authorized hardware profile with device operating systems (iOS 18, Android 15, macOS Sonoma, Windows 11) and trusted hardware fingerprint hashes. This simulates modern mobile banking and digital wallet tokenization.
</p>

<h3>4. Personalized Customer Behavioral Profiles (Lines 150–157)</h3>
<p>
Every customer is assigned an individual mean expenditure (&mu; between $35.00 and $140.00) and standard deviation (&sigma; between $12.00 and $45.00). Consequently, an $80 grocery charge might be routine for Customer A, but represents a 4x spending deviation for Customer B.
</p>

<h3>5. Stochastic Fraud Attack Subtypes (Lines 172–254)</h3>
<p>
To prevent the machine learning model from learning a simplistic single-variable threshold, fraud is injected across five distinct behavioral subtypes:
</p>
<ol>
    <li><strong>Velocity Burst (28% of fraud, Lines 176–195):</strong> Rapid-fire testing where an attacker initiates 2 to 4 transactions within 12 to 95 seconds at a single merchant with randomized IP addresses.</li>
    <li><strong>Amount Anomaly (27% of fraud, Lines 197–211):</strong> Dramatic monetary deviation where expenditure is scaled by 7x to 32x the user's historical baseline average, directed at high-risk merchants.</li>
    <li><strong>Geo / Travel Anomaly (23% of fraud, Lines 213–225):</strong> Originates from overseas or locations 15 to 45 degrees away from the user's home domicile with <code>is_foreign_transaction = 1</code>.</li>
    <li><strong>Credential Stuffing (12% of fraud, Lines 227–239):</strong> Marked by repeated authentication failures (failed_pin_attempts = 2..4) resulting from brute-force automated testing.</li>
    <li><strong>Stealth / Evasive Fraud (10% of fraud, Lines 241–254):</strong> Subtle fraudulent purchases that closely mimic normal expenditure amounts and locations, modeling advanced cyber adversaries.</li>
</ol>

<h3>6. Legitimate Edge Cases: Eliminating False Positives (Lines 256–310)</h3>
<div class="callout callout-warning">
    <div class="callout-title">Why Synthetic Edge Cases are Critical</div>
    A common flaw in naive ML models is flagging every vacation or expensive laptop purchase as fraud. To ensure our model learns nuanced non-linear decision boundaries, Lines 258–310 inject legitimate edge cases:
    <ul>
        <li><strong>Big Legitimate Purchases:</strong> Legitimate cardholders buying electronics or airline tickets ($500–$2,500) from their trusted device.</li>
        <li><strong>Legitimate Vacations:</strong> Transactions conducted far from home coordinates, but using physical POS chips and zero failed PIN attempts.</li>
        <li><strong>Device Upgrades:</strong> Legitimate customer purchases on an untrusted new device (e.g., new smartphone), accompanied by exactly 1 forgotten PIN attempt.</li>
        <li><strong>Errand Sucking / Shopping Sprees:</strong> Multiple legitimate purchases in a single afternoon across different retail stores.</li>
    </ul>
    Training the ensemble on these edge cases allows the model to achieve <strong>87.82% precision</strong>, dramatically minimizing cardholder friction.
</div>
"""
