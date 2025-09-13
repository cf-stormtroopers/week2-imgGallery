FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock ./

# Configure poetry: don't create virtual environment (we're in container)
# and install dependencies without dev dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi

# Copy Makefile and source code
COPY Makefile ./
COPY src/ ./src/

# Create directory for SQLite database (if using SQLite)
RUN mkdir -p /app/data

# Expose the port the app runs on
EXPOSE 8011

# Set environment variables from .env
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Environment variables that the app expects (from backend/.env)
ENV DATABASE_URL=""
ENV SECRET_KEY=""
ENV DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=8011
ENV ALLOWED_HOSTS=""
ENV SESSION_EXPIRE_HOURS=24
ENV MINIO_HOST=""
ENV MINIO_ROOT_USER=""
ENV MINIO_ROOT_PASSWORD=""
ENV MINIO_BUCKET=""
ENV QDRANT_HOST=""
ENV QDRANT_API_KEY=""
ENV REPLICATE_API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8011/health || exit 1

# Run the application using Makefile
CMD ["make", "run"]