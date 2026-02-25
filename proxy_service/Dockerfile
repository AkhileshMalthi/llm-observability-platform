FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies for PII tools (Presidio/Spacy)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml .
# We'll create a dummy lock or just sync
RUN uv pip install --system --no-cache -r pyproject.toml

# We use --system inside a container because the container IS the environment
CMD ["tail", "-f", "/dev/null"]