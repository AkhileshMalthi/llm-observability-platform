from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import logging

logger = logging.getLogger(__name__)

class GuardrailResult:
    """Encapsulates the result of a single guardrail execution."""
    def __init__(self, prompt: str, triggered: bool, should_block: bool = False, block_code: Optional[str] = None):
        self.prompt = prompt           # The potentially modifying prompt (e.g., PII redacted)
        self.triggered = triggered     # Did the guardrail find something? (for telemetry)
        self.should_block = should_block # Should the pipeline stop and return an error?
        self.block_code = block_code   # The error code to return (e.g., "prompt_injection_detected")

class Guardrail(ABC):
    @abstractmethod
    async def process(self, prompt: str) -> GuardrailResult:
        """Processes the prompt and returns the execution result."""
        pass

class PIIGuardrail(Guardrail):
    def __init__(self, analyzer: AnalyzerEngine, anonymizer: AnonymizerEngine):
        self.analyzer = analyzer
        self.anonymizer = anonymizer

    async def process(self, prompt: str) -> GuardrailResult:
        results = self.analyzer.analyze(text=prompt, language="en")
        if not results:
             return GuardrailResult(prompt=prompt, triggered=False)
             
        anonymized_result = self.anonymizer.anonymize(text=prompt, analyzer_results=results)
        return GuardrailResult(prompt=anonymized_result.text, triggered=True)

class InjectionGuardrail(Guardrail):
    def __init__(self, blocklist: List[str]):
        self.known_patterns = blocklist

    async def process(self, prompt: str) -> GuardrailResult:
        lower_prompt = prompt.lower()
        if any(pattern in lower_prompt for pattern in self.known_patterns):
            return GuardrailResult(
                prompt=prompt, 
                triggered=True, 
                should_block=True, 
                block_code="prompt_injection_detected"
            )
        return GuardrailResult(prompt=prompt, triggered=False)

class GuardrailPipeline:
    def __init__(self, guardrails: List[Guardrail]):
        self.guardrails = guardrails

    async def run(self, prompt: str) -> Dict[str, Any]:
        """
        Runs the prompt through all guardrails.
        Returns a dictionary formatted for main.py telemetry and response handling.
        """
        results = {}
        processed_prompt = prompt
        should_block = False
        block_code = None

        for guardrail in self.guardrails:
            guardrail_name = guardrail.__class__.__name__
            
            # 1. Execute standard interface
            result = await guardrail.process(processed_prompt)
            
            # 2. Update running state
            processed_prompt = result.prompt
            results[guardrail_name] = result.triggered
            
            # 3. Handle early exit if blocked
            if result.should_block:
                logger.warning(f"Guardrail {guardrail_name} blocked request: {result.block_code}")
                should_block = True
                block_code = result.block_code
                break

        return {
            "should_block": should_block,
            "block_code": block_code,
            "processed_prompt": processed_prompt,
            "results": results
        }
