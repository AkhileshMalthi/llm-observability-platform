import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from llm_client import LLMClient
from models import ChatCompletionRequest, Message

@pytest.fixture
def sample_request():
    return ChatCompletionRequest(
        model="gpt-test",
        messages=[
            Message(role="user", content="Original user prompt")
        ]
    )

@pytest.mark.asyncio
async def test_generate_chat_completion_success(sample_request):
    client = LLMClient()
    
    expected_response = {"choices": [{"message": {"content": "Hello"}}]}
    processed_prompt = "Processed prompt"
    
    # Mock httpx.AsyncClient to intercept network call
    
    mock_response = MagicMock()
    mock_response.json.return_value = expected_response
    mock_response.raise_for_status.return_value = None
    
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    
    with patch('llm_client.httpx.AsyncClient', return_value=mock_client_instance) as mock_client_class:
        
        result = await client.generate_chat_completion(sample_request, processed_prompt)
        
        # Assertions
        assert result == expected_response
        
        # Verify the outgoing payload injected the processed prompt!
        mock_client_instance.post.assert_called_once()
        call_kwargs = mock_client_instance.post.call_args.kwargs
        sent_json = call_kwargs["json"]
        
        # Important: the LLM should receive the processed prompt, not the original
        assert sent_json["messages"][-1]["content"] == "Processed prompt"

@pytest.mark.asyncio
async def test_generate_chat_completion_http_error(sample_request):
    client = LLMClient()
    
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    
    with patch('llm_client.httpx.AsyncClient', return_value=mock_client_instance) as mock_client_class:
        from httpx import RequestError, Request
        mock_req = Request("POST", "http://test")
        mock_client_instance.post.side_effect = RequestError("API down", request=mock_req)
        
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_chat_completion(sample_request, "prompt")
            
        assert exc_info.value.status_code == 502
        assert "API down" in str(exc_info.value.detail)
