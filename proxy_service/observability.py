import uuid
import time
from datetime import datetime, timezone
import asyncio
from typing import Dict, Any

import redis.asyncio as redis
from models import LogEvent, LogRequestPayload, LogResponsePayload, LogGuardrails, ChatCompletionRequest
from redis_client import publish_log

class ObservabilityService:
    @staticmethod
    def generate_trace_id() -> str:
        return str(uuid.uuid4())
        
    @staticmethod
    def log_interaction_async(
        redis_conn: redis.Redis,
        trace_id: str,
        start_time: float,
        request: ChatCompletionRequest,
        original_prompt: str,
        pipeline_result: Dict[str, Any],
        llm_data: Dict[str, Any]
    ):
        """Asynchronously builds the observation log and publishes it to Redis."""
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        content = ""
        llm_id = None
        usage = {}

        if "choices" in llm_data and len(llm_data["choices"]) > 0:
            content = llm_data["choices"][0].get("message", {}).get("content", "")

        llm_id = llm_data.get("id")
        usage = llm_data.get("usage", {})

        is_injected = pipeline_result["results"].get("InjectionGuardrail", False)
        is_pii_redacted = pipeline_result["results"].get("PIIGuardrail", False)

        log_event = LogEvent(
            traceId=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request=LogRequestPayload(
                model=request.model,
                originalPrompt=original_prompt,
                processedPrompt=pipeline_result["processed_prompt"]
            ),
            response=LogResponsePayload(
                content=content,
                metadata={"llm_id": llm_id, "usage": usage}
            ),
            latencyMs=latency_ms,
            guardrails=LogGuardrails(
                piiRedacted=is_pii_redacted,
                promptInjectionDetected=is_injected
            )
        )
        
        # Fire and forget publishing
        asyncio.create_task(publish_log(redis_conn, log_event.model_dump()))
