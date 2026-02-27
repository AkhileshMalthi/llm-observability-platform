import asyncio
import os
import json
import logging
import sys
from pydantic import ValidationError

import redis.asyncio as redis
from models import IncomingLogPayload, ClickHouseLogRow
from database import ClickHouseClient
from calculator import TokenAndCostCalculator

# Standardized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Analytics Worker...")
    
    # 1. Initialize Business Logic
    calculator = TokenAndCostCalculator()
    
    # 2. Initialize Database Connection
    db_client = ClickHouseClient()
    
    # 3. Connect to Redis
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    redis_conn = redis.from_url(redis_url)
    pubsub = redis_conn.pubsub()
    
    await pubsub.subscribe("llm-logs")
    logger.info(f"Subscribed to Redis channel 'llm-logs' at {redis_url}. Waiting for logs...")

    # 4. Continuous listening loop
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue # Ignore Redis subscription confirmation messages
                
            try:
                raw_data = message["data"].decode("utf-8")
                
                # A: Validate payload via Pydantic
                payload_dict = json.loads(raw_data)
                incoming_log = IncomingLogPayload.model_validate(payload_dict)
                
                # B: Calculate tokens and cost
                in_tokens, out_tokens, cost_usd = calculator.calculate(
                    prompt=incoming_log.request.originalPrompt,
                    response=incoming_log.response.content
                )
                
                # C: Transform to flat ClickHouse Schema
                ch_row = ClickHouseLogRow(
                    trace_id=incoming_log.traceId,
                    timestamp=incoming_log.timestamp,
                    model=incoming_log.request.model,
                    original_prompt=incoming_log.request.originalPrompt,
                    response_content=incoming_log.response.content,
                    latency_ms=int(incoming_log.latencyMs),
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_cost_usd=cost_usd
                )
                
                # D: Persist
                db_client.insert_log(ch_row)
                logger.info(f"Processed trace {ch_row.trace_id}: {in_tokens}in {out_tokens}out (${cost_usd:.4f})")
                
            except ValidationError as ve:
                logger.error(f"Pydantic validation failed for incoming log payload: {ve.errors()}")
            except json.JSONDecodeError:
                logger.error("Failed to decode Redis message as JSON.")
            except Exception as e:
                logger.error(f"Unexpected error processing log message: {str(e)}", exc_info=True)
                
    except asyncio.CancelledError:
        logger.info("Worker gracefully shutting down...")
    finally:
        await pubsub.unsubscribe("llm-logs")
        await redis_conn.aclose()
        logger.info("Connections closed.")

if __name__ == "__main__":
    asyncio.run(main())
