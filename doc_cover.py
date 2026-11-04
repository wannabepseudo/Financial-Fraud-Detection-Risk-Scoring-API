"""
Cover Page, Table of Contents & Global Typography / Print Styling
"""
import pygments
from pygments.formatters import HtmlFormatter

formatter = HtmlFormatter(style="one-dark", linenos="inline")
PYGMENTS_CSS = formatter.get_style_defs(".highlight")

def get_header_and_cover():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Financial Fraud Detection &amp; Risk Scoring API - Complete Architecture &amp; Code Guide</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800&display=swap');

@page {{
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-right {{
        content: counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #64748b;
    }}
    @bottom-left {{
        content: "Financial Fraud Detection API - Technical Architecture Manual";
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #64748b;
    }}
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.65;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
}}

h1, h2, h3, h4, h5 {{
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.6em;
    margin-bottom: 0.6em;
    page-break-after: avoid;
    break-after: avoid;
}}

h1 {{
    font-size: 20pt;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 2.2em;
    page-break-before: always;
    break-before: page;
}}

h1:first-of-type {{
    page-break-before: avoid;
    break-before: avoid;
}}

h2 {{
    font-size: 14pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    color: #1e3a8a;
}}

h3 {{
    font-size: 11.5pt;
    color: #0369a1;
}}

h4 {{
    font-size: 10.5pt;
    color: #334155;
}}

p {{
    margin-top: 0;
    margin-bottom: 0.9em;
    text-align: justify;
}}

ul, ol {{
    margin-top: 0;
    margin-bottom: 1em;
    padding-left: 1.6em;
}}

li {{
    margin-bottom: 0.35em;
}}

code {{
    font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}}

.cover-page {{
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    page-break-after: always;
    break-after: page;
    padding: 40px 20px;
}}

.cover-badge {{
    display: inline-block;
    background: #0284c7;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 6px 14px;
    border-radius: 20px;
    margin-bottom: 24px;
    width: fit-content;
}}

.cover-title {{
    font-size: 28pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin-bottom: 16px;
    border-bottom: none;
    padding-bottom: 0;
    page-break-before: avoid;
    break-before: avoid;
}}

.cover-subtitle {{
    font-size: 13.5pt;
    color: #475569;
    font-weight: 400;
    line-height: 1.45;
    margin-bottom: 35px;
}}

.cover-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 25px;
    margin-bottom: 40px;
}}

.metric-card {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #0284c7;
    border-radius: 6px;
    padding: 12px 14px;
}}

.metric-value {{
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}}

.metric-label {{
    font-size: 7.8pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 4px;
}}

.cover-footer {{
    margin-top: auto;
    border-top: 1px solid #cbd5e1;
    padding-top: 18px;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: #64748b;
}}

/* Callout Box */
.callout {{
    background: #f8fafc;
    border-left: 4px solid #3b82f6;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 12px 16px;
    margin: 14px 0;
    page-break-inside: avoid;
    break-inside: avoid;
}}

.callout-title {{
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 6px;
    font-size: 9.5pt;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.callout-warning {{
    border-left-color: #ef4444;
    background: #fff5f5;
}}
.callout-warning .callout-title {{
    color: #b91c1c;
}}

.callout-success {{
    border-left-color: #10b981;
    background: #f0fdf4;
}}
.callout-success .callout-title {{
    color: #047857;
}}

.callout-why {{
    border-left-color: #8b5cf6;
    background: #faf5ff;
}}
.callout-why .callout-title {{
    color: #6d28d9;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
    break-inside: avoid;
}}

th, td {{
    padding: 8px 10px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
}}

th {{
    background: #0f172a;
    color: #ffffff;
    font-weight: 600;
    border: none;
    font-size: 8.5pt;
    letter-spacing: 0.3px;
}}

tr:nth-child(even) td {{
    background: #f8fafc;
}}

/* Code Highlights Container */
.code-container {{
    background: #1e1e1e;
    border-radius: 6px;
    margin: 14px 0 18px 0;
    overflow: hidden;
    page-break-inside: avoid;
    break-inside: avoid;
    border: 1px solid #334155;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}}

.code-header {{
    background: #0f172a;
    color: #94a3b8;
    padding: 6px 14px;
    font-size: 8pt;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #334155;
    font-family: 'Fira Code', monospace;
}}

.code-header .lang-badge {{
    background: #0284c7;
    color: #ffffff;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 7pt;
    text-transform: uppercase;
}}

.highlight {{
    padding: 12px 14px;
    overflow-x: auto;
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 8pt;
    line-height: 1.5;
    color: #abb2bf;
    background: #282c34 !important;
}}

.highlight pre {{
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
}}

.linenodiv pre, .lineno {{
    color: #5c6370;
    margin-right: 12px;
    user-select: none;
}}

{PYGMENTS_CSS}

/* Chart Cards */
.chart-card {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px;
    margin: 18px 0;
    page-break-inside: avoid;
    break-inside: avoid;
    box-shadow: 0 2px 5px rgba(0,0,0,0.04);
}}

.chart-card img {{
    width: 100%;
    max-height: 380px;
    object-fit: contain;
    border-radius: 4px;
    background: #0b0f19;
}}

.chart-caption {{
    font-size: 8.5pt;
    color: #475569;
    margin-top: 8px;
    text-align: center;
    font-style: italic;
}}

.toc-item {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    border-bottom: 1px dotted #cbd5e1;
    padding-bottom: 2px;
    font-size: 9pt;
}}

.toc-title {{
    font-weight: 500;
    color: #0f172a;
}}

.toc-page {{
    font-weight: 600;
    color: #0284c7;
}}

.badge {{
    display: inline-block;
    padding: 2px 7px;
    font-size: 7.5pt;
    font-weight: 700;
    border-radius: 12px;
    text-transform: uppercase;
}}
.badge-pass {{ background: #dcfce7; color: #15803d; }}
.badge-warn {{ background: #fef3c7; color: #b45309; }}
.badge-crit {{ background: #fee2e2; color: #b91c1c; }}
.badge-info {{ background: #e0f2fe; color: #0369a1; }}

.tree-view {{
    font-family: 'Fira Code', monospace;
    font-size: 8.2pt;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 12px 16px;
    line-height: 1.5;
    margin: 14px 0;
    page-break-inside: avoid;
    break-inside: avoid;
}}

.comparison-winner {{
    background: #ecfdf5 !important;
    font-weight: 600;
    color: #065f46;
}}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div class="cover-badge">Enterprise Fintech &amp; Cybersecurity Architecture</div>
    <div class="cover-title">Financial Fraud Detection &amp; Real-Time Risk Scoring API</div>
    <div class="cover-subtitle">
        A Complete Engineering Manual: Every Line of Code, Mathematical Foundations,
        Comparative Architectural Trade-offs ("Why This vs That"), and Production Operations
    </div>

    <div class="cover-grid">
        <div class="metric-card">
            <div class="metric-value">93.75%</div>
            <div class="metric-label">AUC-ROC (Target ~94%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">87.82%</div>
            <div class="metric-label">Precision (Target ~88%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">3.16 ms</div>
            <div class="metric-label">P95 Latency (&lt;50ms SLA)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">45,000+</div>
            <div class="metric-label">Transactions Processed</div>
        </div>
    </div>

    <div style="background: #f1f5f9; padding: 16px; border-radius: 6px; font-size: 9pt; color: #334155; margin-bottom: 25px;">
        <strong>Document Summary &amp; Scope:</strong> This manual provides an exhaustive, line-by-line and concept-by-concept analysis of the containerized financial microservice. It covers relational SQL schema design, rolling window velocity aggregations, synthetic data engineering, XGBoost and SVM dual-model ensembling, threshold calibration for severe class imbalance, sub-50ms FastAPI inference serving, regulatory adverse action explainability, automated test verification, and Docker orchestration. Every technological choice is critically evaluated against alternative paradigms.
    </div>

    <div class="cover-footer">
        <div><strong>System:</strong> FinSecure AI Engine v2026.1.0</div>
        <div><strong>Language &amp; Frameworks:</strong> Python 3.12 | FastAPI | XGBoost | Scikit-Learn | SQLite | Docker</div>
        <div><strong>Status:</strong> Production Ready (All 10 Tests Passed)</div>
    </div>
</div>

<!-- TABLE OF CONTENTS -->
<h1>Table of Contents</h1>
<div style="margin-top: 20px;">
    <div class="toc-item"><span class="toc-title">1. Executive Overview &amp; Payment Gateway Economics</span><span class="toc-page">Module 01</span></div>
    <div class="toc-item"><span class="toc-title">2. Relational Database Schema &amp; Storage Architecture (schema.sql)</span><span class="toc-page">Module 02</span></div>
    <div class="toc-item"><span class="toc-title">3. Complex SQL Analytical Feature Engineering (queries.sql)</span><span class="toc-page">Module 03</span></div>
    <div class="toc-item"><span class="toc-title">4. Synthetic Banking Transaction Data Generator (generate_synthetic_data.py)</span><span class="toc-page">Module 04</span></div>
    <div class="toc-item"><span class="toc-title">5. Exploratory Data Analysis &amp; Behavioral Analytics (run_eda.py)</span><span class="toc-page">Module 05</span></div>
    <div class="toc-item"><span class="toc-title">6. Machine Learning Pipeline, Training &amp; Calibration (train.py)</span><span class="toc-page">Module 06</span></div>
    <div class="toc-item"><span class="toc-title">7. Production Inference Pipeline &amp; Explainability Engine (pipeline.py)</span><span class="toc-page">Module 07</span></div>
    <div class="toc-item"><span class="toc-title">8. Application Configuration, Schemas &amp; DB Connectors (config, schemas, db)</span><span class="toc-page">Module 08</span></div>
    <div class="toc-item"><span class="toc-title">9. High-Performance FastAPI Microservice &amp; API Routing (main.py, routes)</span><span class="toc-page">Module 09</span></div>
    <div class="toc-item"><span class="toc-title">10. Interactive Cybersecurity &amp; Fintech Dashboard (static frontend)</span><span class="toc-page">Module 10</span></div>
    <div class="toc-item"><span class="toc-title">11. Automated Testing, SLA Benchmarks &amp; Quality Assurance (tests)</span><span class="toc-page">Module 11</span></div>
    <div class="toc-item"><span class="toc-title">12. Containerization, Docker Orchestration &amp; Cloud Deployment</span><span class="toc-page">Module 12</span></div>
    <div class="toc-item"><span class="toc-title">13. Master Architectural Decision Matrix: "Why This vs Other?"</span><span class="toc-page">Module 13</span></div>
    <div class="toc-item"><span class="toc-title">14. Production Operations Runbook &amp; Quickstart Verification</span><span class="toc-page">Module 14</span></div>
</div>

<div class="tree-view">
<strong>Repository File Tree:</strong><br>
fraud-detection-api/<br>
├── data/<br>
│   ├── schema.sql                     (Production relational DB schema: users, devices, merchants, transactions)<br>
│   ├── queries.sql                    (Complex analytical SQL window functions &amp; velocity queries)<br>
│   ├── generate_synthetic_data.py     (Synthesizes 45,000+ realistic transactions with imbalanced fraud noise)<br>
│   └── transactions.db                (SQLite relational database generated by pipeline)<br>
├── models/<br>
│   ├── train.py                       (ML training: XGBoost + SVM ensemble, threshold calibration, evaluation)<br>
│   └── model_artifacts/               (Serialized pipelines, scalers, and JSON evaluation metrics)<br>
│       ├── xgb_model.joblib<br>
│       ├── svm_model.joblib<br>
│       ├── preprocessor.joblib<br>
│       └── metrics.json<br>
├── eda/<br>
│   ├── run_eda.py                     (Matplotlib + Seaborn EDA script generating publication-grade plots)<br>
│   └── plots/                         (High-resolution visualization PNGs)<br>
├── app/<br>
│   ├── main.py                        (FastAPI microservice entrypoint, CORS, latency middleware, lifespan)<br>
│   ├── config.py                      (Application configuration, SLAs, thresholds, and paths)<br>
│   ├── schemas.py                     (Pydantic v2 validation models for requests, responses, and metrics)<br>
│   ├── pipeline.py                    (Inference pipeline, feature extraction, ensemble scoring, explainability)<br>
│   ├── db.py                          (Database connectors and analytical query executors)<br>
│   └── routes/<br>
│       ├── score.py                   (/api/v1/score &amp; /api/v1/score/batch)<br>
│       ├── metrics.py                 (/api/v1/metrics)<br>
│       ├── analytics.py               (/api/v1/analytics/stats &amp; /api/v1/analytics/recent)<br>
│       └── sql_inspector.py           (/api/v1/sql/execute &amp; /api/v1/sql/queries)<br>
├── static/                            (Interactive glassmorphism web dashboard with speedometer &amp; live stream)<br>
├── tests/                             (Unit &amp; integration test suites verifying sub-50ms execution)<br>
├── Dockerfile                         (Production-ready Python 3.12 container with health checks)<br>
├── docker-compose.yml                 (Multi-container orchestration)<br>
├── requirements.txt                   (Pinned Python package dependencies)<br>
└── README.md                          (Project documentation)
</div>
"""
