from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LogRequestPayload(BaseModel):
    model: str
    originalPrompt: str
    processedPrompt: str

class LogResponsePayload(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LogGuardrails(BaseModel):
    piiRedacted: bool
    promptInjectionDetected: bool

class IncomingLogPayload(BaseModel):
    """
    Validates the nested JSON payload dispatched by the proxy service via Redis Pub/Sub.
    """
    traceId: str
    timestamp: str
    request: LogRequestPayload
    response: LogResponsePayload
    latencyMs: float
    guardrails: LogGuardrails

class ClickHouseLogRow(BaseModel):
    """
    The flattened representation of the log data guaranteed to match the ClickHouse `llm_logs` table schema.
    """
    trace_id: str
    timestamp: datetime
    model: str
    original_prompt: str
    response_content: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
