FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for layer caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    openai \
    python-dotenv \
    openenv-core \
    huggingface-hub \
    requests \
    python-multipart

# Copy all project files
COPY main.py .
COPY env.py .
COPY models.py .
COPY cases.json .
COPY openenv.yaml .
COPY inference.py .
COPY README.md .

# Copy static UI files
COPY static/ ./static/

# Environment variables (override at runtime)
ENV API_BASE_URL=https://api-inference.huggingface.co/v1
ENV MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
# Do NOT set a default HF_TOKEN or OPENAI_API_KEY in the image. Provide them at runtime / via Secrets.
ENV ENV_BASE_URL=http://localhost:7860

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]