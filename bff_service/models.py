from pydantic import BaseModel
from typing import List

class HealthResponse(BaseModel):
    status: str

class SummaryMetricsResponse(BaseModel):
    totalRequests: int
    averageLatencyMs: float
    totalCostUsd: float

class TraceItem(BaseModel):
    traceId: str
    timestamp: str
    model: str
    latencyMs: int
    costUsd: float
    statusCode: int

class TracesResponse(BaseModel):
    traces: List[TraceItem]
    total: int
