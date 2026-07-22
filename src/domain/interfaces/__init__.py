"""Domain interfaces package."""

from src.domain.interfaces.downloader_service import DownloaderService
from src.domain.interfaces.media_repository import MediaRepository

__all__ = [
    "DownloaderService",
    "MediaRepository",
]