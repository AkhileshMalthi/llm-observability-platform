import tiktoken
import logging

logger = logging.getLogger(__name__)

class TokenAndCostCalculator:
    """
    Pure Python calculator with zero external dependencies aside from the stateless math operations.
    Complies with Single Responsibility Principle.
    """
    
    # Hardcoded pricing as per project requirements
    COST_PER_1K_INPUT = 0.03
    COST_PER_1K_OUTPUT = 0.06

    def __init__(self, model_encoding: str = "gpt-4"):
        try:
            self.encoding = tiktoken.encoding_for_model(model_encoding)
        except KeyError:
            logger.warning(f"Tiktoken encoding not found for {model_encoding}. Falling back to cl100k_base.")
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def calculate(self, prompt: str, response: str) -> tuple[int, int, float]:
        """
        Returns (input_tokens, output_tokens, total_cost_usd)
        """
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(response)

        input_cost = (input_tokens / 1000.0) * self.COST_PER_1K_INPUT
        output_cost = (output_tokens / 1000.0) * self.COST_PER_1K_OUTPUT
        
        total_cost = input_cost + output_cost
        
        return input_tokens, output_tokens, total_cost
