import httpx
from fastapi import HTTPException
from models import ChatCompletionRequest
from config import settings
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.base_url = settings.LLM_API_BASE_URL
        self.api_key = settings.LLM_API_KEY
    
    async def generate_chat_completion(self, request: ChatCompletionRequest, processed_prompt: str) -> dict:
        """
        Calls the downstream LLM using the provided request context and processed prompt.
        """
        # Ensure nested objects (like Message objects in the messages list) are fully serialized to dicts
        payload = request.model_dump(mode='json', exclude_unset=True)
        
        # Inject the guardrail-processed prompt into the last message
        if payload.get("messages"):
            payload["messages"][-1]["content"] = processed_prompt
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Forwarding prompt to upstream LLM model: {payload.get('model')}")
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                res.raise_for_status()
                return res.json()
        except httpx.HTTPError as e:
            error_details = getattr(e, "response", None)
            if error_details:
                logger.error(f"Upstream LLM rejected payload. Reason: {error_details.text}")
            raise HTTPException(status_code=502, detail=f"Error communicating with upstream LLM: {str(e)}")
