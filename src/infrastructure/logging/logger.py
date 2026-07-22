"""Structured logging service for the application.

Uses Loguru for intuitive, structured logging with rotation and formatting.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.config.settings import get_settings


class AppLogger:
    """Application logger wrapper providing structured logging capabilities.

    This class wraps Loguru to provide a consistent logging interface
    across all layers of the application.
    """

    def __init__(
        self,
        name: str = "universal-media-downloader",
        log_level: Optional[str] = None,
        log_file: Optional[Path] = None,
    ) -> None:
        self._name = name
        self._logger = logger.bind(name=name)

        # Remove default handler
        self._logger.remove()

        # Determine log level from config or default to INFO
        try:
            settings = get_settings()
            level = log_level or settings.LOG_LEVEL
            log_path = log_file or settings.LOG_FILE_PATH
        except Exception:
            level = log_level or "INFO"
            log_path = log_file

        # Add console handler with colorized output
        self._logger.add(
            sys.stdout,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

        # Add file handler with rotation
        if log_path:
            log_dir = Path(log_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            self._logger.add(
                str(log_path),
                level=level,
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                    "{name}:{function}:{line} | {message}"
                ),
                rotation="10 MB",
                retention="30 days",
                compression="gz",
                backtrace=True,
                diagnose=False,
            )

    @property
    def native(self):
        """Access the underlying Loguru logger for advanced use."""
        return self._logger

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message with optional structured context."""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message with optional structured context."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message with optional structured context."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message with optional structured context."""
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message with optional structured context."""
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log an exception with full traceback."""
        self._logger.exception(message, **kwargs)


# Module-level cache for created loggers
_loggers: dict = {}


def get_logger(name: str = "universal-media-downloader") -> AppLogger:
    """Get or create a named application logger.

    Args:
        name: The name for the logger instance.

    Returns:
        An AppLogger instance.
    """
    if name not in _loggers:
        _loggers[name] = AppLogger(name=name)
    return _loggers[name]