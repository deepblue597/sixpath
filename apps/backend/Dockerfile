# Backend Dockerfile using uv
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy workspace files for dependency resolution
COPY pyproject.toml uv.lock /app/
COPY packages/models /app/packages/models/

# Copy backend-specific files
COPY apps/backend/pyproject.toml /app/apps/backend/

# Change to backend directory
WORKDIR /app/apps/backend

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the rest of the backend code
COPY apps/backend /app/apps/backend/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with uv
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
