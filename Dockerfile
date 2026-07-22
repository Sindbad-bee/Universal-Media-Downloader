# ═══════════════════════════════════════════════════════════════════
# Universal Media Downloader - Dockerfile
# Multi-stage build for production
# ═══════════════════════════════════════════════════════════════════

# ── Stage 1: Base ──────────────────────────────────────────────────
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for yt-dlp and ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod a+rx /usr/local/bin/yt-dlp

# ── Stage 2: Dependencies ──────────────────────────────────────────
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 3: Production ────────────────────────────────────────────
FROM base AS production

COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p /app/downloads

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application with uvicorn
CMD ["uvicorn", "src.presentation.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]