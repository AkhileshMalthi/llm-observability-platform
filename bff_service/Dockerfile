FROM python:3.12.2-slim-bookworm

WORKDIR /app

# Install system dependencies if required, update CA certs
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:0.3.0 /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY ./ ./

# Install dependencies directly into the system python using uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Expose the API port
EXPOSE 8001

# Start the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
