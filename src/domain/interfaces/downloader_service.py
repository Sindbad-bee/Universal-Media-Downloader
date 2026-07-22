"""Interface for the external media downloader service.

This abstraction allows the domain layer to define the contract for
downloading media without depending on any specific CLI tool or library.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.media_request import MediaRequest


class DownloaderService(ABC):
    """Abstract interface for executing media downloads."""

    @abstractmethod
    async def fetch_metadata(self, url: str) -> dict:
        """Retrieve metadata about a media URL without downloading.

        Args:
            url: The media URL to inspect.

        Returns:
            A dictionary containing metadata (title, duration, formats, etc.).

        Raises:
            DownloaderError: If metadata cannot be retrieved.
        """
        raise NotImplementedError

    @abstractmethod
    async def download(self, request: MediaRequest) -> str:
        """Execute a media download based on the provided request.

        Args:
            request: The MediaRequest entity specifying download parameters.

        Returns:
            The file path where the downloaded media was saved.

        Raises:
            DownloaderError: If the download fails for any reason.
        """
        raise NotImplementedError

    @abstractmethod
    async def cancel_download(self, request_id: str) -> bool:
        """Attempt to cancel an in-progress download.

        Args:
            request_id: The unique identifier of the download to cancel.

        Returns:
            True if the download was successfully cancelled, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """Check if a given URL is supported by the downloader.

        Args:
            url: The URL to validate.

        Returns:
            True if the URL is supported, False otherwise.
        """
        raise NotImplementedError