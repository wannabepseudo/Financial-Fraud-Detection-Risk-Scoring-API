"""
Module 12: Containerization, Docker Orchestration & Cloud Deployment
"""
import pygments
from pygments.lexers import DockerLexer, YamlLexer, TextLexer
from pygments.formatters import HtmlFormatter

def get_content(raw_dockerfile, raw_compose, raw_reqs):
    formatter = HtmlFormatter(style="one-dark", linenos="inline", noclasses=False)
    h_docker = pygments.highlight(raw_dockerfile, DockerLexer(), formatter)
    h_compose = pygments.highlight(raw_compose, YamlLexer(), formatter)
    h_reqs = pygments.highlight(raw_reqs, TextLexer(), formatter)
    
    return f"""
<h1>Module 12: Containerization, Docker Orchestration &amp; Cloud Deployment</h1>

<h2>12.1 Deployment Paradigms: Why Containerized Microservice vs Serverless?</h2>
<p>
Deploying real-time machine learning pipelines in banking environments involves critical architectural trade-offs between cold-start latency, resource isolation, and operational cost:
</p>

<table>
    <thead>
        <tr>
            <th>Deployment Paradigm</th>
            <th>Cold-Start Latency</th>
            <th>Predictability &amp; SLAs</th>
            <th>Cost at Scale</th>
            <th>Production Suitability</th>
        </tr>
    </thead>
    <tbody>
        <tr class="comparison-winner">
            <td><strong>Containerized Microservice (Docker + ECS / K8s / Cloud Run)</strong></td>
            <td>Zero cold-start once initialized; warm in-memory model inference executes in <strong>3.16 ms</strong>.</td>
            <td>100% predictable; meets sub-50ms payment SLA on every single request.</td>
            <td>Fixed compute instance pricing; highly cost-effective for continuous 24/7 transaction streams.</td>
            <td><strong>Optimal:</strong> Essential for payment rails where a 500ms timeout halts card checkout.</td>
        </tr>
        <tr>
            <td><strong>Serverless Functions (AWS Lambda / Google Cloud Functions)</strong></td>
            <td>Severe cold-starts (<strong>500 ms to 3,500 ms</strong>) when downloading and unpickling Scikit-Learn/XGBoost models from S3.</td>
            <td>Unacceptable latency spikes violate payment card network authorization SLAs.</td>
            <td>Cost scales with execution duration; expensive for continuous multi-million transaction streams.</td>
            <td><strong>Fatal Flaw:</strong> Cold-start timeouts directly violate the payment gateway SLA.</td>
        </tr>
        <tr>
            <td><strong>Managed ML Endpoints (AWS SageMaker / Google Vertex AI)</strong></td>
            <td>Low latency, but relies on proprietary wrappers and vendor-locked container runtime harnesses.</td>
            <td>Good SLA adherence, but debugging internal preprocessors is difficult.</td>
            <td>Extremely expensive (2x–4x markup over raw EC2 / GCE compute instances).</td>
            <td><strong>High Cost:</strong> Adds significant cloud expense without architectural advantages over a lean FastAPI container.</td>
        </tr>
    </tbody>
</table>

<h2>12.2 Complete Source Code: Dockerfile</h2>
<div class="code-container">
    <div class="code-header">
        <span>Dockerfile</span>
        <span class="lang-badge">DOCKER</span>
    </div>
    {h_docker}
</div>

<h3>Walkthrough: Dockerfile</h3>
<ul>
    <li><code>FROM python:3.12-slim</code>: Uses a minimal Debian-based Linux image, stripping out non-essential utilities to minimize the container attack surface and reduce image size to &lt;350 MB.</li>
    <li><code>ENV PYTHONDONTWRITEBYTECODE=1, PYTHONUNBUFFERED=1</code>: Prevents Python from writing <code>.pyc</code> cache files inside ephemeral container layers and ensures logs flush immediately to stdout/stderr for real-time monitoring via Datadog, Prometheus, or AWS CloudWatch.</li>
    <li><strong>Optimized Layer Caching (Lines 23–25):</strong> Copies <code>requirements.txt</code> and installs pip packages <em>before</em> copying the application source code. Docker caches the heavy dependency layer; modifying application Python code does not trigger package re-installation during rebuilds.</li>
    <li><strong>Self-Healing Artifact Generation (Lines 35–41):</strong> Automatically verifies that the database, model artifacts, and static EDA plots exist. If building from a fresh repository clone, Docker autonomously synthesizes the data and trains the models during image build time.</li>
    <li><strong>Integrated Health Check (Lines 47–48):</strong>
        <pre><code>HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1</code></pre>
        Allows container orchestrators (Kubernetes, Docker Swarm, AWS ECS) to detect frozen workers and automatically restart unhealthy containers.
    </li>
</ul>

<h2>12.3 Complete Source Code: docker-compose.yml</h2>
<div class="code-container">
    <div class="code-header">
        <span>docker-compose.yml</span>
        <span class="lang-badge">YAML</span>
    </div>
    {h_compose}
</div>

<h3>Walkthrough: docker-compose.yml</h3>
<ul>
    <li><strong>Port Forwarding (Line 10):</strong> Maps container port <code>8000</code> to host port <code>8000</code>, exposing both the REST API and the interactive dashboard.</li>
    <li><strong>Environment Variable Injection (Lines 11–14):</strong> Injects security secrets (<code>FRAUD_API_KEY</code>) and SLA latency ceilings without hardcoding credentials into the image.</li>
    <li><strong>Volume Mounts (Lines 15–18):</strong> Mounts host directories for <code>data</code>, <code>model_artifacts</code>, and <code>static/eda</code>. This allows persisting generated transactions and updated model weights without rebuilding the container.</li>
    <li><code>restart: unless-stopped</code>: Ensures the microservice automatically recovers from host reboots or unexpected process termination.</li>
</ul>

<h2>12.4 Complete Source Code: requirements.txt</h2>
<div class="code-container">
    <div class="code-header">
        <span>requirements.txt</span>
        <span class="lang-badge">TEXT</span>
    </div>
    {h_reqs}
</div>
"""
