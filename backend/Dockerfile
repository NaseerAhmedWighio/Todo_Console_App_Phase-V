# Production Dockerfile for FastAPI Todo Backend - Optimized for size
FROM python:3.11-alpine

# Build arguments for pip configuration (build-time only)
ARG PIP_DEFAULT_TIMEOUT=100
ARG PIP_RETRIES=5

# Set environment variables (runtime)
ENV PIP_DEFAULT_TIMEOUT=${PIP_DEFAULT_TIMEOUT}
ENV PIP_RETRIES=${PIP_RETRIES}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies (minimal set)
RUN apk add --no-cache \
    curl \
    postgresql-client \
    libpq \
    && rm -rf /var/cache/apk/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --retries ${PIP_RETRIES} --timeout ${PIP_DEFAULT_TIMEOUT} -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run database migrations and start the application
CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 7860"]
