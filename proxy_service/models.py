from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    
# --- Redis Log Event Models ---

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

class LogEvent(BaseModel):
    traceId: str
    timestamp: str 
    request: LogRequestPayload
    response: LogResponsePayload
    latencyMs: float
    guardrails: LogGuardrails
