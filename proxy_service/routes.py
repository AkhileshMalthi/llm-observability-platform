import time
from fastapi import APIRouter, Response, Depends, Request, HTTPException
import redis.asyncio as redis

from models import ChatCompletionRequest
from llm_client import LLMClient
from observability import ObservabilityService
import logging
from redis_client import get_redis
from guardrails import GuardrailPipeline

logger = logging.getLogger(__name__)

# Dependency mapping
def get_guardrail_pipeline(request: Request) -> GuardrailPipeline:
    return request.app.state.guardrail_pipeline

router = APIRouter()
llm_client = LLMClient()

@router.post("/v1/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest, 
    response: Response, 
    redis_conn: redis.Redis = Depends(get_redis),
    pipeline: GuardrailPipeline = Depends(get_guardrail_pipeline)
):
    trace_id = ObservabilityService.generate_trace_id()
    logger.info(f"Received completion request. Trace ID: {trace_id}")
    start_time = time.time()
    response.headers["X-Trace-ID"] = trace_id
    
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")
        
    original_prompt = req.messages[-1].content
    
    # 1. Run Guardrails Pipeline
    pipeline_result = await pipeline.run(original_prompt)
    
    if pipeline_result["should_block"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": {
                    "code": pipeline_result.get("block_code", "request_blocked"),
                    "message": "The provided prompt was blocked by a safety guardrail."
                }
            }
        )

    # 2. Call downstream LLM Service
    llm_data = await llm_client.generate_chat_completion(req, pipeline_result["processed_prompt"])
    
    # 3. Asynchronously map and publish telemetry
    ObservabilityService.log_interaction_async(
        redis_conn=redis_conn,
        trace_id=trace_id,
        start_time=start_time,
        request=req,
        original_prompt=original_prompt,
        pipeline_result=pipeline_result,
        llm_data=llm_data
    )
    
    return llm_data
