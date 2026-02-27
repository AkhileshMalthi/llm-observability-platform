import pytest
from pydantic import ValidationError
from models import IncomingLogPayload, ClickHouseLogRow
from calculator import TokenAndCostCalculator

def test_token_and_cost_calculator():
    calc = TokenAndCostCalculator(model_encoding="gpt-4")
    
    # 1. Test token counting
    # "Hello world!" is typically 3 tokens: ["Hello", " world", "!"]
    tokens = calc.count_tokens("Hello world!")
    assert tokens == 3
    
    # 2. Test cost output
    in_t, out_t, cost = calc.calculate("Hello world!", "Hi there!")
    # "Hi there!" is 3 tokens. input=3, output=3
    assert in_t == 3
    assert out_t == 3
    
    expected_cost = (3 / 1000.0 * 0.03) + (3 / 1000.0 * 0.06)
    assert abs(cost - expected_cost) < 1e-9

def test_pydantic_schema_mapping():
    valid_json_dict = {
        "traceId": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2023-10-27T10:00:00Z",
        "request": {
            "model": "gpt-4",
            "originalPrompt": "What is 2+2?",
            "processedPrompt": "What is 2+2?"
        },
        "response": {
            "content": "4",
            "metadata": {"usage": {"total_tokens": 10}}
        },
        "latencyMs": 150.5,
        "guardrails": {
            "piiRedacted": False,
            "promptInjectionDetected": False
        }
    }
    
    # Assert successful validation
    payload = IncomingLogPayload.model_validate(valid_json_dict)
    assert payload.traceId == "123e4567-e89b-12d3-a456-426614174000"
    assert payload.latencyMs == 150.5
    assert payload.request.model == "gpt-4"
    assert payload.response.metadata["usage"]["total_tokens"] == 10

def test_pydantic_schema_mapping_failure():
    invalid_json_dict = {
        "traceId": "123",
        # Missing required nested objects
    }
    with pytest.raises(ValidationError):
        IncomingLogPayload.model_validate(invalid_json_dict)
