from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLM_API_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Default injection blocklist
    INJECTION_BLOCKLIST: list[str] = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore all previous",
        "system prompt",
        "forget previous",
        "forget your instructions"
    ]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
