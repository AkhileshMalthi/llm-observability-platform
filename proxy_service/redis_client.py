import redis.asyncio as redis
import os
import json

redis_client = None

async def init_redis():
    global redis_client
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    # Decode responses so we deal with strings instead of bytes
    redis_client = redis.from_url(redis_url, decode_responses=True)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()

async def get_redis():
    # Dependency injected into FastAPI routes
    return redis_client

async def publish_log(redis_conn: redis.Redis, log_event: dict):
    if not redis_conn:
        return
    await redis_conn.publish("llm-logs", json.dumps(log_event))
