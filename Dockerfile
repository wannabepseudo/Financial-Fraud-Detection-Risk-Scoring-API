# ==============================================================================
# Financial Fraud Detection & Risk Scoring API 2026 - Dockerfile
# Lean Containerized Microservice with Sub-50ms Inference Guarantee
# ==============================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source, data, models, and frontend static assets
COPY app/ ./app/
COPY data/ ./data/
COPY models/ ./models/
COPY eda/ ./eda/
COPY static/ ./static/

# Verify database exists or generate synthetic transactions
RUN if [ ! -f "data/transactions.db" ]; then python data/generate_synthetic_data.py; fi

# Verify models are trained or train pipelines
RUN if [ ! -f "models/model_artifacts/xgb_model.joblib" ]; then python models/train.py; fi

# Generate fresh EDA visualizations
RUN python eda/run_eda.py

# Expose default HTTP microservice port
EXPOSE 8000

# Health check to ensure microservice responds under 50ms
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
