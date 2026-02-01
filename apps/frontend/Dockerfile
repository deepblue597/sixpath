# Frontend Dockerfile using uv
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy workspace files for dependency resolution
COPY pyproject.toml uv.lock /app/
COPY packages/models /app/packages/models/

# Copy frontend-specific files
COPY apps/frontend/pyproject.toml /app/apps/frontend/

# Change to frontend directory
WORKDIR /app/apps/frontend

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the rest of the frontend code
COPY apps/frontend /app/apps/frontend/

# Copy static and lib folders (if they're needed by frontend)
COPY static /app/static/
COPY lib /app/lib/

# Expose Streamlit port
EXPOSE 8501

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit with uv (port and address configured via environment variables)
CMD ["uv", "run", "streamlit", "run", "app.py"]
