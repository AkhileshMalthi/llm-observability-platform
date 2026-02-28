# Proxy Service

A high-performance FastAPI proxy designed to sit between your downstream applications and your Large Language Model API (e.g., OpenAI). The proxy is responsible for processing requests and ensuring security, privacy, and observability.

## Key Features

1. **OpenAI Chat Completions Compatible**: The core endpoint, `/v1/chat/completions`, mocks the OpenAI API structure.
2. **PII Redaction**: Analyzes prompts using Presidio to automatically detect and redact Personally Identifiable Information before it touches the LLM provider. Replaces detected PII with labels (e.g., `[REDACTED_EMAIL]`).
3. **Prompt Injection Detection**: Includes an active guardrail to detect and completely block malicious prompt injection attempts before forwarding anything to the downstream API. Returns a `400 Bad Request` on detection.
4. **Asynchronous Redis Logging**: Publishes every interaction—both successful requests and blocked ones—to a Redis Pub/Sub channel (`llm-logs`) to be processed efficiently by the Analytics Worker.

## Usage

### Endpoints

- `POST /v1/chat/completions`
  Mimics the OpenAI standard schema.
  
  **Headers Structure:**
  Outputs a custom `X-Trace-ID` response header for tracing observability.
  
- `GET /health`
  Returns the health status of the service (`{"status": "ok"}`).

### Dependencies

This service requires a functioning Redis instance accessible on the configured port.

### Development

The proxy service runs inside Docker as orchestrated by the root `docker-compose.yml`. Please refer to the root `README.md` for startup instructions.
