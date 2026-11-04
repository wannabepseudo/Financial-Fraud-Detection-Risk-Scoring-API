"""
Master Compilation Script:
Assembles all 14 modules, source files, and base64 plots into a single
monolithic publication-grade HTML document, then invokes Microsoft Edge
headless to compile the final PDF:
'Financial_Fraud_Detection_Full_Guide_and_Codebook.pdf'
"""

import os
import sys
import base64
import subprocess
import fitz  # PyMuPDF

import doc_cover
import doc_module_1_overview
import doc_module_2_schema
import doc_module_3_queries
import doc_module_4_synthetic
import doc_module_5_eda
import doc_module_6_ml
import doc_module_7_inference
import doc_module_8_app_core
import doc_module_9_api
import doc_module_10_frontend
import doc_module_11_testing
import doc_module_12_docker
import doc_module_13_comparisons
import doc_module_14_runbook

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(BASE_DIR, "financial_fraud_full_guide.html")
OUTPUT_PDF = os.path.join(BASE_DIR, "Financial_Fraud_Detection_Full_Guide_and_Codebook.pdf")

def read_text(rel_path):
    p = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(p):
        print(f"[!] Warning: missing {p}")
        return ""
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def get_b64_image(rel_path):
    p = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(p):
        print(f"[!] Warning: missing image {p}")
        return ""
    with open(p, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"

print("[*] Reading source code files...")
raw_schema = read_text("data/schema.sql")
raw_queries = read_text("data/queries.sql")
raw_synthetic = read_text("data/generate_synthetic_data.py")
raw_eda = read_text("eda/run_eda.py")
raw_train = read_text("models/train.py")
raw_pipeline = read_text("app/pipeline.py")
raw_config = read_text("app/config.py")
raw_schemas = read_text("app/schemas.py")
raw_db = read_text("app/db.py")
raw_main = read_text("app/main.py")
raw_score = read_text("app/routes/score.py")
raw_analytics = read_text("app/routes/analytics.py")
raw_metrics = read_text("app/routes/metrics.py")
raw_sql = read_text("app/routes/sql_inspector.py")
raw_test_model = read_text("tests/test_model.py")
raw_test_api = read_text("tests/test_api.py")
raw_dockerfile = read_text("Dockerfile")
raw_compose = read_text("docker-compose.yml")
raw_reqs = read_text("requirements.txt")

print("[*] Loading and serializing EDA charts to base64...")
img_class_imbalance = get_b64_image("eda/plots/class_imbalance.png")
img_amount_dist = get_b64_image("eda/plots/amount_distribution_log.png")
img_corr_matrix = get_b64_image("eda/plots/correlation_matrix.png")
img_hourly_anomaly = get_b64_image("eda/plots/hourly_anomaly_curve.png")
img_roc_pr = get_b64_image("eda/plots/roc_pr_curves.png")
img_feat_importance = get_b64_image("eda/plots/feature_importance.png")

print("[*] Assembling HTML document sections...")
with open(OUTPUT_HTML, "w", encoding="utf-8") as out:
    out.write(doc_cover.get_header_and_cover())
    out.write("\n")
    out.write(doc_module_1_overview.get_content())
    out.write("\n")
    out.write(doc_module_2_schema.get_content(raw_schema))
    out.write("\n")
    out.write(doc_module_3_queries.get_content(raw_queries))
    out.write("\n")
    out.write(doc_module_4_synthetic.get_content(raw_synthetic))
    out.write("\n")
    out.write(doc_module_5_eda.get_content(
        raw_eda,
        img_class_imbalance,
        img_amount_dist,
        img_corr_matrix,
        img_hourly_anomaly,
        img_roc_pr,
        img_feat_importance
    ))
    out.write("\n")
    out.write(doc_module_6_ml.get_content(raw_train))
    out.write("\n")
    out.write(doc_module_7_inference.get_content(raw_pipeline))
    out.write("\n")
    out.write(doc_module_8_app_core.get_content(raw_config, raw_schemas, raw_db))
    out.write("\n")
    out.write(doc_module_9_api.get_content(raw_main, raw_score, raw_analytics, raw_metrics, raw_sql))
    out.write("\n")
    out.write(doc_module_10_frontend.get_content())
    out.write("\n")
    out.write(doc_module_11_testing.get_content(raw_test_model, raw_test_api))
    out.write("\n")
    out.write(doc_module_12_docker.get_content(raw_dockerfile, raw_compose, raw_reqs))
    out.write("\n")
    out.write(doc_module_13_comparisons.get_content())
    out.write("\n")
    out.write(doc_module_14_runbook.get_content())

html_size_kb = os.path.getsize(OUTPUT_HTML) / 1024.0
print(f"[+] Successfully wrote {OUTPUT_HTML} ({html_size_kb:.1f} KB).")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

print(f"[*] Compiling PDF using headless Microsoft Edge from {edge_path}...")
cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    OUTPUT_HTML
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"[!] Error invoking Edge: {result.stderr}")
    sys.exit(result.returncode)

if os.path.exists(OUTPUT_PDF):
    pdf_size_mb = os.path.getsize(OUTPUT_PDF) / (1024.0 * 1024.0)
    doc = fitz.open(OUTPUT_PDF)
    page_count = len(doc)
    doc.close()
    print(f"\n==================================================================")
    print(f"[SUCCESS] Generated: {OUTPUT_PDF}")
    print(f"[SUCCESS] Total Pages: {page_count} pages")
    print(f"[SUCCESS] File Size:   {pdf_size_mb:.2f} MB")
    print(f"==================================================================\n")
else:
    print(f"[!] Failed to produce PDF.")
    sys.exit(1)
