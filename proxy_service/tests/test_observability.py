import pytest
from unittest.mock import patch, MagicMock
from models import ChatCompletionRequest, Message
from observability import ObservabilityService

@pytest.fixture
def sample_request():
    return ChatCompletionRequest(
        model="gpt-test",
        messages=[
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Original user prompt")
        ]
    )

@pytest.fixture
def sample_llm_response():
    return {
        "id": "chatcmpl-123",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is the LLM response."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }

@pytest.fixture
def pipeline_result_clean():
    return {
        "should_block": False,
        "processed_prompt": "Original user prompt",
        "results": {
            "PIIGuardrail": False,
            "InjectionGuardrail": False
        }
    }

@pytest.mark.asyncio
async def test_log_interaction_async_metrics(sample_request, sample_llm_response, pipeline_result_clean):
    # Setup mock redis connection
    mock_redis = MagicMock()
    trace_id = "test-trace-uuid"
    
    # We patch publish_log to intercept what ObservabilityService is trying to send
    with patch('observability.publish_log') as mock_publish_log, \
         patch('observability.asyncio.create_task') as mock_create_task:
         
        ObservabilityService.log_interaction_async(
            redis_conn=mock_redis,
            trace_id=trace_id,
            start_time=1000.0, # fake start time
            request=sample_request,
            original_prompt="Original user prompt",
            pipeline_result=pipeline_result_clean,
            llm_data=sample_llm_response
        )
        
        # Verify that it attempted to schedule a background task
        assert mock_create_task.called

        # Extract the args it passed to publish_log
        call_args = mock_publish_log.call_args
        assert call_args is not None
        
        redis_arg, log_event_dict = call_args[0]
        
        # Verify telemetry mapping (Req 7)
        assert log_event_dict["traceId"] == trace_id
        assert log_event_dict["request"]["model"] == "gpt-test"
        assert log_event_dict["request"]["originalPrompt"] == "Original user prompt"
        assert log_event_dict["response"]["content"] == "This is the LLM response."
        assert log_event_dict["response"]["metadata"]["llm_id"] == "chatcmpl-123"
        assert log_event_dict["response"]["metadata"]["usage"]["total_tokens"] == 15
        
        # Guardrail state verification
        assert log_event_dict["guardrails"]["piiRedacted"] is False
        assert log_event_dict["guardrails"]["promptInjectionDetected"] is False
