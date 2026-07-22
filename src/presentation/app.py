"""FastAPI application factory and dependency container.

This module wires together all layers of the application:
Domain → Infrastructure → Presentation (API + Web UI).

Uses dependency injection to provide singleton services.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config.settings import get_settings
from src.infrastructure.adapters.in_memory_repository import (
    InMemoryMediaRepository,
)
from src.infrastructure.adapters.yt_dlp_adapter import YtDlpAdapter
from src.infrastructure.logging.logger import get_logger
from src.presentation.api.controllers.download_controller import router
from src.presentation.api.middleware.error_handler import (
    register_error_handlers,
)
from src.presentation.api.middleware.logging_middleware import (
    register_logging_middleware,
)

logger = get_logger(__name__)

# ── Singleton instances ───────────────────────────────────────────

_repository: InMemoryMediaRepository
_downloader: YtDlpAdapter


def get_repository() -> InMemoryMediaRepository:
    """Return the singleton repository instance."""
    global _repository
    return _repository


def get_downloader() -> YtDlpAdapter:
    """Return the singleton downloader instance."""
    global _downloader
    return _downloader


# ── Application Factory ───────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler for startup and shutdown events."""
    global _repository, _downloader

    settings = get_settings()
    logger.info(
        "Starting Universal Media Downloader",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize singleton services
    _repository = InMemoryMediaRepository()

    try:
        _downloader = YtDlpAdapter(
            yt_dlp_path=settings.YT_DLP_PATH,
            ffmpeg_path=settings.FFMPEG_PATH,
            default_output_dir=settings.download_path,
            request_timeout=settings.DOWNLOAD_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        logger.warning(
            "Downloader initialization failed (yt-dlp/ffmpeg may not be installed)",
            error=str(exc),
        )
        # Create a fallback that will raise clear errors
        _downloader = YtDlpAdapter.__new__(YtDlpAdapter)
        _downloader._yt_dlp_path = None
        _downloader._ffmpeg_path = None
        _downloader._default_output_dir = settings.download_path
        _downloader._request_timeout = settings.DOWNLOAD_TIMEOUT_SECONDS
        _downloader._active_processes = {}

    logger.info("Application started successfully")
    yield

    logger.info("Shutting down Universal Media Downloader")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        A fully configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Universal Media Downloader - Download videos and audio from various platforms.",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware ───────────────────────────────────────────────
    register_logging_middleware(app)
    register_error_handlers(app)

    # ── API Routes ───────────────────────────────────────────────
    app.include_router(router)

    # ── Web UI (Static Files) ────────────────────────────────────
    web_dir = Path(__file__).parent / "web"
    if web_dir.exists():
        app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")
        logger.info("Web UI mounted", path=str(web_dir))

    return app


# ── Entry point for uvicorn ───────────────────────────────────────

app = create_app()