import pytest
from unittest.mock import MagicMock, ANY
from guardrails import (
    InjectionGuardrail,
    PIIGuardrail,
    GuardrailPipeline,
    GuardrailResult,
    Guardrail
)

# ==========================================
# 1. InjectionGuardrail Tests
# ==========================================

@pytest.mark.asyncio
async def test_injection_guardrail_clean_prompt(injection_blocklist, clean_prompt):
    guardrail = InjectionGuardrail(blocklist=injection_blocklist)
    result = await guardrail.process(clean_prompt)
    
    assert result.triggered is False
    assert result.should_block is False
    assert result.prompt == clean_prompt

@pytest.mark.asyncio
async def test_injection_guardrail_detected(injection_blocklist, injection_prompt):
    guardrail = InjectionGuardrail(blocklist=injection_blocklist)
    result = await guardrail.process(injection_prompt)
    
    # Should detect "ignore previous instructions" regardless of casing
    assert result.triggered is True
    assert result.should_block is True
    assert result.block_code == "prompt_injection_detected"

# ==========================================
# 2. PIIGuardrail Tests
# ==========================================

@pytest.mark.asyncio
async def test_pii_guardrail_clean_prompt(mock_analyzer, mock_anonymizer, clean_prompt):
    guardrail = PIIGuardrail(analyzer=mock_analyzer, anonymizer=mock_anonymizer)
    result = await guardrail.process(clean_prompt)
    
    assert result.triggered is False
    assert result.should_block is False
    assert result.prompt == clean_prompt
    mock_analyzer.analyze.assert_called_once_with(text=clean_prompt, language="en", entities=ANY)
    mock_anonymizer.anonymize.assert_not_called()

@pytest.mark.asyncio
async def test_pii_guardrail_detected_and_redacted(mock_analyzer, mock_anonymizer, pii_prompt):
    # Setup mock to simulate finding PII
    mock_analyzer.analyze.return_value = ["mock_pii_entity"]
    
    # Setup mock to simulate redaction
    mock_anonymized_result = MagicMock()
    mock_anonymized_result.text = "My email is [REDACTED]."
    mock_anonymizer.anonymize.return_value = mock_anonymized_result
    
    guardrail = PIIGuardrail(analyzer=mock_analyzer, anonymizer=mock_anonymizer)
    result = await guardrail.process(pii_prompt)
    
    assert result.triggered is True
    assert result.should_block is False # PII is redacted, not blocked!
    assert result.prompt == "My email is [REDACTED]."
    mock_anonymizer.anonymize.assert_called_once()

# ==========================================
# 3. GuardrailPipeline Tests
# ==========================================

class DummyGuardrail(Guardrail):
    """A simple mock guardrail for pipeline testing."""
    def __init__(self, name: str, return_result: GuardrailResult):
        self.name = name
        self.return_result = return_result
        self.called = False

    async def process(self, prompt: str) -> GuardrailResult:
        self.called = True
        return self.return_result
        
    @property
    def __class__(self):
        # Override class name so the pipeline telemetry uses our custom name
        type_mock = type(self.name, (object,), {})
        return type_mock

@pytest.mark.asyncio
async def test_pipeline_all_clean(clean_prompt):
    g1 = DummyGuardrail("CleanGuardrail1", GuardrailResult(prompt=clean_prompt, triggered=False))
    g2 = DummyGuardrail("CleanGuardrail2", GuardrailResult(prompt=clean_prompt, triggered=False))
    
    pipeline = GuardrailPipeline([g1, g2])
    result = await pipeline.run(clean_prompt)
    
    assert result["should_block"] is False
    assert result["processed_prompt"] == clean_prompt
    assert result["results"] == {"CleanGuardrail1": False, "CleanGuardrail2": False}
    assert g1.called is True
    assert g2.called is True

@pytest.mark.asyncio
async def test_pipeline_cascading_modifications(clean_prompt):
    prompt_v2 = "Modified prompt step 1"
    prompt_v3 = "Final modified prompt"
    
    g1 = DummyGuardrail("ModGuardrail1", GuardrailResult(prompt=prompt_v2, triggered=True))
    g2 = DummyGuardrail("ModGuardrail2", GuardrailResult(prompt=prompt_v3, triggered=True))
    
    pipeline = GuardrailPipeline([g1, g2])
    result = await pipeline.run(clean_prompt)
    
    # Ensure the prompt passed down the chain and the final prompt is returned
    assert result["processed_prompt"] == prompt_v3
    assert result["results"] == {"ModGuardrail1": True, "ModGuardrail2": True}

@pytest.mark.asyncio
async def test_pipeline_short_circuit_on_block(clean_prompt):
    g1 = DummyGuardrail("CleanGuardrail", GuardrailResult(prompt=clean_prompt, triggered=False))
    g2 = DummyGuardrail("BlockingGuardrail", GuardrailResult(prompt=clean_prompt, triggered=True, should_block=True, block_code="custom_block"))
    g3 = DummyGuardrail("NeverCalledGuardrail", GuardrailResult(prompt=clean_prompt, triggered=False))
    
    pipeline = GuardrailPipeline([g1, g2, g3])
    result = await pipeline.run(clean_prompt)
    
    assert result["should_block"] is True
    assert result["block_code"] == "custom_block"
    # Ensure g3 was never called because g2 blocked the request
    assert g1.called is True
    assert g2.called is True
    assert g3.called is False
    # Telemetry should only include guardrails that actually ran
    assert "NeverCalledGuardrail" not in result["results"]
