"""
FastAPI Microservice Entrypoint
Production-grade Financial Fraud Detection & Risk Scoring API 2026
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_TITLE, APP_VERSION, API_PREFIX, STATIC_DIR, SLA_MAX_LATENCY_MS
from app.pipeline import engine
from app.routes.score import router as score_router
from app.routes.metrics import router as metrics_router
from app.routes.analytics import router as analytics_router
from app.routes.sql_inspector import router as sql_router
from app.schemas import HealthResponse


# Auto-initialize models on import if not already loaded
if not engine.loaded:
    engine.load_artifacts()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models, scalers, and warm up inference engine
    print(f"[*] Starting {APP_TITLE} v{APP_VERSION}...")
    if not engine.loaded:
        engine.load_artifacts()
    # Warm-up inference
    if engine.loaded:
        from app.schemas import TransactionInput
        warmup_tx = TransactionInput(amount=50.0, channel="WEB", merchant_category="grocery")
        _ = engine.score(warmup_tx)
        print("[+] Inference engine warmed up and ready for sub-50ms requests.")
    yield
    # Shutdown
    print("[*] Shutting down Fraud Detection Microservice.")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Containerized microservice delivering real-time transaction fraud scoring with sub-50ms latency using tuned XGBoost and SVM anomaly detection pipelines.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Sub-50ms Latency Benchmark Middleware
@app.middleware("http")
async def add_latency_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    response.headers["X-SLA-Status"] = "PASS" if duration_ms < SLA_MAX_LATENCY_MS else "WARN"
    return response


# Include API Routers
app.include_router(score_router, prefix=API_PREFIX)
app.include_router(metrics_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(sql_router, prefix=API_PREFIX)

# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serves the interactive frontend web dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "Dashboard not found, see /docs for API documentation."})


@app.get("/health", response_model=HealthResponse, tags=["System Health"])
async def health_check():
    """Microservice health check endpoint."""
    return HealthResponse(
        status="HEALTHY",
        version=APP_VERSION,
        models_loaded=engine.loaded,
        database_connected=os.path.exists(os.path.join(os.path.dirname(__file__), "..", "data", "transactions.db")),
        sla_target_ms=SLA_MAX_LATENCY_MS,
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
