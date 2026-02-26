from fastapi import FastAPI
from contextlib import asynccontextmanager

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from guardrails import GuardrailPipeline, PIIGuardrail, InjectionGuardrail
from redis_client import init_redis, close_redis
from routes import router
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base dependencies
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    
    # Register core pipeline to application state
    app.state.guardrail_pipeline = GuardrailPipeline([
        InjectionGuardrail(blocklist=settings.INJECTION_BLOCKLIST),
        PIIGuardrail(analyzer=analyzer, anonymizer=anonymizer)
    ])
    
    # Initialize background connections
    await init_redis()
    yield
    
    # Shutdown routines
    await close_redis()

app = FastAPI(title="LLM Proxy Service", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

# Register routes
app.include_router(router)
