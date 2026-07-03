FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for psycopg2 (and curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash app_user

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application code, model artifacts, and DB
COPY backend/ /app/backend/
COPY ml/ /app/ml/
COPY chances.db /app/chances.db

# Environment Configuration
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Ensure permissions
RUN chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Add Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Expose port (Documentation purpose, actual port mapped dynamically by Render)
EXPOSE 8000

# Run Uvicorn using the PORT environment variable
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
