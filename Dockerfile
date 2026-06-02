# ============================================================
# CIForge Backend — Dockerfile
# Demonstrates: Unit II — Image Building & Container Management
#
# Concepts covered:
#   - Multi-stage builds (builder + runtime stages)
#   - Image layering (each instruction = one layer)
#   - FROM, RUN, COPY, WORKDIR, ENV, EXPOSE, CMD
#   - .dockerignore (build context optimization)
#   - Non-root user for security
# ============================================================

# ── Stage 1: Builder ─────────────────────────────────────────
# Use a full Python image to install dependencies
FROM python:3.12-slim AS builder

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed to compile Python packages
# Combining RUN commands reduces image layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (Python dependency manager)
RUN pip install --no-cache-dir poetry==1.8.3

# Copy only dependency files first (layer caching optimization)
# If pyproject.toml hasn't changed, Docker reuses this cached layer
COPY pyproject.toml poetry.lock* ./

# Install production dependencies only (no dev tools)
# --no-root: don't install the package itself yet
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi --no-root

# ── Stage 2: Runtime ─────────────────────────────────────────
# Start fresh from a slim image — excludes build tools
FROM python:3.12-slim AS runtime

# Labels for image metadata (OCI standard)
LABEL org.opencontainers.image.title="CIForge Backend"
LABEL org.opencontainers.image.description="AI-Powered CI/CD Pipeline Generator"
LABEL org.opencontainers.image.version="1.0.0"

# Environment variables
# PYTHONDONTWRITEBYTECODE: don't create .pyc files
# PYTHONUNBUFFERED: print logs immediately (no buffering)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install only runtime system deps (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY src/ ./src/

# Create a non-root user for security (never run as root in production)
RUN groupadd -r ciforge && useradd -r -g ciforge ciforge \
    && chown -R ciforge:ciforge /app

USER ciforge

# Expose the port the app listens on
# (documentation only — actual port mapping is done at runtime)
EXPOSE 8000

# Health check — Docker will restart container if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command to start the FastAPI server
CMD ["uvicorn", "src.api.server:create_api", "--factory", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
