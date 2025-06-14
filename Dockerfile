FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y poppler-utils

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the application into the container.
COPY app/ /app/app/

# Copy dependency files
COPY pyproject.toml uv.lock /app/

# Install the application dependencies.
RUN uv sync --frozen --no-cache

# Set environment variable for OpenAI API key (override at runtime for security)
ENV OPENAI_API_KEY='your_openai_api_key_here'

# Run the application.
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]