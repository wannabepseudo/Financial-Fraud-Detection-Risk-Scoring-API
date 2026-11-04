"""
Module 5: Exploratory Data Analysis & Behavioral Analytics (run_eda.py)
"""
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_py, img_class_imbalance, img_amount_dist, img_corr_matrix, img_hourly_anomaly, img_roc_pr, img_feat_importance):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    highlighted_py = pygments.highlight(raw_py, PythonLexer(), formatter)
    
    return f"""
<h1>Module 05: Exploratory Data Analysis &amp; Behavioral Analytics</h1>

<h2>5.1 The Role of Behavioral EDA in Financial Cyber-Defense</h2>
<p>
Before training machine learning algorithms, quantitative fraud analysts must rigorously investigate the empirical distributions, temporal attack rhythms, and correlation matrices of the underlying data. Without deep exploratory analysis, practitioners risk deploying models trained on spurious correlations or failing to detect seasonal vulnerabilities.
</p>
<p>
The script <code>eda/run_eda.py</code> leverages <strong>Matplotlib</strong> and <strong>Seaborn</strong> with a headless rendering engine (<code>matplotlib.use('Agg')</code>) to generate publication-grade visualizations.
</p>

<h2>5.2 Complete Source Code: eda/run_eda.py</h2>
<div class="code-container">
    <div class="code-header">
        <span>eda/run_eda.py</span>
        <span class="lang-badge">PYTHON</span>
    </div>
    {highlighted_py}
</div>

<h2>5.3 Embedded Visualizations &amp; In-Depth Domain Interpretations</h2>

<!-- CHART 1 -->
<div class="chart-card">
    <img src="{img_class_imbalance}" alt="Class Imbalance Distribution">
    <div class="chart-caption">Figure 5.1: Empirical Class Imbalance Distribution across 45,000 Banking Records.</div>
</div>
<h3>1. Class Imbalance Analysis (Figure 5.1)</h3>
<p>
Figure 5.1 reveals the stark operational reality of payment security: genuine transactions dominate the space (43,110 samples, ~95.8%), while fraudulent transactions occupy a slim minority (1,890 samples, ~4.2%).
</p>
<ul>
    <li><strong>Mathematical Consequence:</strong> A standard Cross-Entropy loss function without class weighting would treat a false negative (failing to catch a \$4,000 fraud attack) with the exact same numerical penalty as a minor false positive on a \$10 purchase.</li>
    <li><strong>Mitigation Strategy:</strong> In Module 06, we counterbalance this asymmetry by dynamically configuring XGBoost's <code>scale_pos_weight</code> parameter to (N_neg / N_pos) = 22.8 and deploying cost-sensitive Support Vector classification.</li>
</ul>

<!-- CHART 2 -->
<div class="chart-card">
    <img src="{img_amount_dist}" alt="Transaction Amount Distribution">
    <div class="chart-caption">Figure 5.2: Probability Density of Transaction Amount (Log-Scale Transformation).</div>
</div>
<h3>2. Log-Scale Transaction Amount Dynamics (Figure 5.2)</h3>
<p>
Financial transactions follow a <strong>heavy-tailed Pareto (Power-Law) distribution</strong>: 80% of daily transactions are sub-$100 routine charges (coffee, groceries, fuel), while rare high-ticket purchases stretch out into thousands of dollars.
</p>
<ul>
    <li>Plotting this data on a linear axis compresses 95% of data points into a single unreadable bin at the left margin.</li>
    <li>By applying logarithmic binning (<code>np.logspace(np.log10(min), np.log10(max), 50)</code>), the comparative probability densities become clear: legitimate transactions follow a clean log-normal distribution centered around $45, while fraudulent transactions exhibit a distinct bimodal density with high-frequency surges in the $500–$2,500 corridor.</li>
</ul>

<!-- CHART 3 -->
<div class="chart-card">
    <img src="{img_corr_matrix}" alt="Correlation Matrix Heatmap">
    <div class="chart-caption">Figure 5.3: Seaborn Correlation Matrix of Behavioral Features and Anomaly Indicators.</div>
</div>
<h3>3. Behavioral Feature Correlation Matrix (Figure 5.3)</h3>
<p>
Figure 5.3 illustrates the Pearson correlation coefficients ($r$) across all continuous and engineered features:
</p>
<ul>
    <li><code>failed_pin_attempts</code> and <code>is_new_device</code> demonstrate strong positive correlations with <code>is_fraud</code> ($r = 0.42$ and $r = 0.58$), confirming that authentication failures and device novelty are top-tier predictors of account takeover.</li>
    <li><code>velocity_1h</code> and <code>cumulative_spend_24h</code> exhibit moderate positive collinearity ($r = 0.38$), which is effectively exploited by tree-based partitioning in XGBoost without suffering from the multicollinearity degradation that plagues traditional linear regression.</li>
</ul>

<!-- CHART 4 -->
<div class="chart-card">
    <img src="{img_hourly_anomaly}" alt="Hourly Fraud Attack Curve">
    <div class="chart-caption">Figure 5.4: Circadian Rhythm of Cyberattacks: Hourly Fraud Rate Distribution (UTC).</div>
</div>
<h3>4. Hourly Attack Surge &amp; Off-Peak Vulnerability (Figure 5.4)</h3>
<p>
Figure 5.4 displays the hourly attack percentage across the 24-hour daily cycle:
</p>
<ul>
    <li>Between 08:00 and 20:00 local time, fraud rates remain at a baseline of ~2.5% to 3.5% of total volume.</li>
    <li>Between <strong>01:00 and 04:00 UTC</strong>, the empirical fraud rate surges to <strong>over 12.8%</strong>.</li>
    <li><strong>Domain Insight:</strong> Automated criminal syndicates and credential-stuffing bots deliberately target the early morning hours when cardholders are asleep and unable to respond to real-time SMS one-time password (OTP) alerts or push notifications. To capture this temporal cycle, Module 06 encodes time using continuous cyclical trigonometry: sin(2&pi;h / 24) and cos(2&pi;h / 24).</li>
</ul>

<!-- CHART 5 & 6 -->
<div class="chart-card">
    <img src="{img_roc_pr}" alt="ROC and Precision-Recall Curves">
    <div class="chart-caption">Figure 5.5: Receiver Operating Characteristic (ROC) &amp; Precision-Recall (PR) Curves on Evaluation Test Set.</div>
</div>
<h3>5. Model ROC &amp; Precision-Recall Curves (Figure 5.5)</h3>
<p>
Figure 5.5 showcases the discriminatory power of our tuned dual-model ensemble:
</p>
<ul>
    <li><strong>ROC Curve:</strong> Achieves an <strong>AUC-ROC of 93.75% (~94%)</strong>, demonstrating excellent separation between the true-positive rate and false-positive rate across varying classification thresholds.</li>
    <li><strong>Precision-Recall Curve:</strong> Delivers an <strong>Area Under the PR Curve (PR-AUC) of 87.94%</strong>. The curve clearly demonstrates that at a decision threshold of $t = 0.2765$ (calibrated risk score of 35.0), the model sustains <strong>87.82% precision</strong> while maintaining <strong>85.09% recall</strong>.</li>
</ul>

<div class="chart-card">
    <img src="{img_feat_importance}" alt="XGBoost Feature Importance">
    <div class="chart-caption">Figure 5.6: XGBoost Gini Gain Predictive Feature Importance Ranking.</div>
</div>
<h3>6. XGBoost Feature Importance Breakdown (Figure 5.6)</h3>
<p>
Evaluates the relative contribution of each feature based on average split gain:
</p>
<ol>
    <li><code>is_new_device</code> (Importance: 76.75%): The single strongest split criterion. A new hardware fingerprint operating outside the customer's trusted device registry immediately isolates high-risk transactions.</li>
    <li><code>amount</code> (Importance: 3.78%): Raw monetary exposure.</li>
    <li><code>channel_MOBILE_APP</code> and <code>channel_POS_CHIP</code>: Channel security properties (chip transactions provide hardware cryptograms, making them inherently safer than web or mobile app channels).</li>
    <li><code>distance_from_home_km</code> &amp; <code>failed_pin_attempts</code>: Strong secondary risk contributors.</li>
</ol>
"""
