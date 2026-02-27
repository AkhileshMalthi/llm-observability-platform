from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from models import HealthResponse, SummaryMetricsResponse, TracesResponse
from database import get_db, ClickHouseDb

# Standardized logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Observability Dashboard BFF")

# Allow the React frontend to fetch metrics
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_endpoint():
    """Confirms the BFF service is active and responsive."""
    return {"status": "ok"}

@app.get("/api/metrics/summary", response_model=SummaryMetricsResponse)
def get_metrics_summary(db: ClickHouseDb = Depends(get_db)):
    """
    Returns real-time aggregated system metrics (Latency, Costs, Total Requests) 
    over the entire LLM Log database.
    """
    try:
        metrics = db.get_summary_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to fetch summary metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error connecting to Analytics Database.")

@app.get("/api/traces", response_model=TracesResponse)
def get_traces_paginated(
    limit: int = Query(20, ge=1, le=100, description="Amount of traces to return"),
    offset: int = Query(0, ge=0, description="Pagination cursor offset"),
    db: ClickHouseDb = Depends(get_db)
):
    """
    Returns paginated raw trace details for the frontend dashboard timeline.
    Ordered descending by timestamp.
    """
    try:
        traces = db.get_recent_traces(limit=limit, offset=offset)
        total = db.get_total_traces_count()
        return {"traces": traces, "total": total}
    except Exception as e:
        logger.error(f"Failed to fetch paginated traces: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error connecting to Analytics Database.")
