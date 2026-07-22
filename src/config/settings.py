"""Strongly-typed application configuration using Pydantic Settings.

All environment variables are validated and typed at startup.
Uses pydantic-settings for automatic .env file loading.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files.

    All configuration is strongly typed and validated at startup.
    Sensitive defaults are provided for development; customize via .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = Field(
        default="Universal Media Downloader",
        description="Application name for logging and display.",
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Semantic version of the application.",
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging.",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Runtime environment: development, staging, production.",
    )

    # ── Server ───────────────────────────────────────────────────
    HOST: str = Field(
        default="0.0.0.0",
        description="Host address for the HTTP server.",
    )
    PORT: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Port for the HTTP server.",
    )
    WORKERS: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Number of uvicorn worker processes.",
    )
    CORS_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins.",
    )

    # ── Downloader ───────────────────────────────────────────────
    YT_DLP_PATH: Optional[str] = Field(
        default=None,
        description="Custom path to yt-dlp executable. Auto-detected if None.",
    )
    FFMPEG_PATH: Optional[str] = Field(
        default=None,
        description="Custom path to ffmpeg executable. Auto-detected if None.",
    )
    DOWNLOAD_DIR: str = Field(
        default="./downloads",
        description="Default directory for downloaded media files.",
    )
    DOWNLOAD_TIMEOUT_SECONDS: int = Field(
        default=600,
        ge=30,
        description="Maximum time in seconds for a single download.",
    )

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )
    LOG_FILE_PATH: Optional[Path] = Field(
        default=None,
        description="Path to log file. Logs go to stdout only if None.",
    )

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=30,
        ge=1,
        description="Maximum API requests per minute per client.",
    )

    # ── Derived Properties ───────────────────────────────────────

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS comma-separated string into a list."""
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return origins if origins else ["*"]

    @property
    def download_path(self) -> Path:
        """Get the download directory as a Path, creating it if needed."""
        path = Path(self.DOWNLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings.

    Uses lru_cache to ensure settings are loaded only once per process.
    """
    return Settings()