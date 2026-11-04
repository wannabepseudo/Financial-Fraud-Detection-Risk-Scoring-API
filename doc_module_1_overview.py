"""
Module 1: Executive Overview & Payment Gateway Economics
"""

def get_content():
    return """
<h1>Module 01: The Domain of Financial Fraud & Modern Anti-Fraud Architecture</h1>

<h2>1.1 The Payment Authorization Window & Latency Budget</h2>
<p>
Modern digital commerce operates over global interbank communication rails (e.g., Visa, Mastercard, American Express, SWIFT, and FedNow). When a cardholder swipes a card at a Point-of-Sale (POS) terminal or clicks "Pay Now" on a checkout portal, the transaction request is forwarded to an acquiring bank, routed through the card network switch, and delivered to the issuing bank for authorization.
</p>
<p>
The total round-trip authorization window mandated by payment card networks is strictly capped between <strong>500 ms and 2000 ms</strong>. However, network transit, database writes, cryptographic verification (EMV chip cryptograms / 3D-Secure handshakes), and ledger checks consume over 90% of this budget. Consequently, an upstream real-time risk scoring microservice is allocated a <strong>strict Service Level Agreement (SLA) of sub-50 milliseconds</strong> (and ideally single-digit milliseconds).
</p>
<p>
If a fraud scoring API exceeds 50 ms, it risks request timeouts, checkout abandonment, and downstream fallback to degraded static rules. Our microservice achieves an average single-transaction inference latency of <strong>3.16 ms (P95: 3.31 ms)</strong>, running comfortably 15x faster than the maximum allowable SLA.
</p>

<div class="callout callout-warning">
    <div class="callout-title">The Fundamental Fraud Trilemma</div>
    Every financial fraud system balances three competing tensions:
    <ol>
        <li><strong>Fraud Loss Prevention:</strong> Catching criminal transactions before settlement to prevent chargebacks, card replacement costs, and network fines.</li>
        <li><strong>Cardholder Friction (False Positive Friction):</strong> Avoiding false declines on legitimate customers. Studies indicate that 33% of consumers abandon a merchant after an erroneous fraud decline.</li>
        <li><strong>Inference Latency &amp; Throughput:</strong> Scoring transactions synchronously in sub-50ms without degrading authorization throughput during holiday traffic peaks.</li>
    </ol>
</div>

<h2>1.2 The Mathematics of Extreme Class Imbalance</h2>
<p>
In real-world retail banking, fraudulent transactions represent between <strong>0.1% and 4.0%</strong> of total volume. This severe class imbalance creates significant challenges for machine learning:
</p>
<ul>
    <li><strong>The Accuracy Paradox:</strong> A naive model that classifies 100% of transactions as "Legitimate" achieves 96% to 99.9% statistical accuracy while detecting exactly zero dollars of fraud. Standard classification accuracy is not an appropriate metric in fraud detection.</li>
    <li><strong>Precision vs. Recall in Banking:</strong>
        <ul>
            <li><strong>Precision:</strong> TP / (TP + FP). The percentage of flagged transactions that are actually fraudulent. High precision ensures fraud analysts are not overwhelmed with false alarms.</li>
            <li><strong>Recall (Sensitivity):</strong> TP / (TP + FN). The percentage of actual fraud caught. High recall guarantees financial loss containment.</li>
        </ul>
    </li>
    <li><strong>ROC-AUC vs. PR-AUC:</strong> While the Receiver Operating Characteristic Area Under Curve (ROC-AUC) evaluates True Positive Rate vs. False Positive Rate, the False Positive Rate (FP / (TN + FP)) can appear deceptively low when True Negatives (TN) number in the millions. Therefore, we evaluate both <strong>ROC-AUC (achieving 93.75%)</strong> and <strong>Precision-Recall AUC (PR-AUC, achieving 87.94%)</strong> to ensure robust performance on the minority class.</li>
</ul>

<h2>1.3 Primary Fraud Attack Vectors &amp; Behavioral Signatures</h2>
<p>
Modern fraud actors rarely attempt random card theft; instead, they deploy automated infrastructure, card testing bots, compromised credential lists, and geographic proxies. Our system models four distinct attack vectors:
</p>
<table>
    <thead>
        <tr>
            <th>Attack Vector</th>
            <th>Tactics, Techniques &amp; Procedures (TTPs)</th>
            <th>Behavioral Signature / Feature Footprint</th>
            <th>Detection Strategy</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Card-Not-Present (CNP) Velocity Burst</strong></td>
            <td>Automated bots rapidly test stolen card numbers across online merchants within minutes before cardholders notice.</td>
            <td>Abrupt spike in 1-hour transaction frequency (v_1h &ge; 3), small incremental amounts, shared IP subnet.</td>
            <td>Rolling window frequency aggregation with SQL / vectorized windowing; immediate rate-limit triggers.</td>
        </tr>
        <tr>
            <td><strong>Account Takeover (ATO) &amp; Credential Stuffing</strong></td>
            <td>Attackers use breached username/password/PIN dumps to gain unauthorized access to existing customer accounts.</td>
            <td>Multiple failed PIN/CVV attempts (failed_pins &ge; 2), new unverified hardware device fingerprint, off-peak hours.</td>
            <td>Failed credential counter, device trust registry, cyclic temporal anomaly weighting.</td>
        </tr>
        <tr>
            <td><strong>Impossible Travel &amp; Geolocation Hopping</strong></td>
            <td>Transactions executed from physical locations or IP geolocations that imply impossible physical speed.</td>
            <td>Consecutive transactions hundreds of kilometers apart separated by minutes (implied speed &gt; 800 km/h).</td>
            <td>Lagged geospatial distance calculation using the Haversine trigonometric formula in SQL and Python.</td>
        </tr>
        <tr>
            <td><strong>High-Risk Merchant Laundering</strong></td>
            <td>Fraudulent funds funneled through irreversible, high-liquidity channels (cryptocurrency exchanges, gambling, P2P).</td>
            <td>Large anomalous amounts sent to high-chargeback Merchant Category Codes (MCC) with high spending deviation (amt / baseline &gt; 4.0).</td>
            <td>Merchant category risk scoring, customer 30-day baseline spend ratios.</td>
        </tr>
    </tbody>
</table>
"""
