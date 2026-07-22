"""Use case for executing a media download.

This use case orchestrates the actual download operation by coordinating
the MediaRepository and DownloaderService abstractions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.domain.entities.media_request import MediaRequest
from src.domain.interfaces.downloader_service import DownloaderService
from src.domain.interfaces.media_repository import MediaRepository


class DownloadNotFoundError(Exception):
    """Raised when the requested download ID does not exist."""

    pass


@dataclass
class ExecuteDownloadInput:
    """Input data for executing a download."""

    request_id: str


@dataclass
class ExecuteDownloadOutput:
    """Output data after executing a download."""

    id: str
    status: str
    download_path: Optional[str] = None
    error_message: Optional[str] = None


class ExecuteDownloadUseCase:
    """Business logic for executing a media download.

    This use case retrieves a persisted request and delegates the actual
    download to the DownloaderService, then updates the request status.
    """

    def __init__(
        self,
        repository: MediaRepository,
        downloader: DownloaderService,
    ) -> None:
        self._repository = repository
        self._downloader = downloader

    async def execute(
        self, input_dto: ExecuteDownloadInput
    ) -> ExecuteDownloadOutput:
        """Execute the download for a given request ID.

        Args:
            input_dto: Contains the request ID to process.

        Returns:
            Output DTO with the final status and download path.

        Raises:
            DownloadNotFoundError: If the request ID does not exist.
        """
        request = await self._repository.find_by_id(input_dto.request_id)
        if request is None:
            raise DownloadNotFoundError(
                f"Download request '{input_dto.request_id}' not found."
            )

        try:
            request.mark_in_progress()
            await self._repository.save(request)

            download_path = await self._downloader.download(request)

            request.mark_completed(download_path)
            await self._repository.save(request)

            return ExecuteDownloadOutput(
                id=request.id,
                status=request.status.name.lower(),
                download_path=download_path,
            )

        except Exception as exc:
            error_message = str(exc)
            request.mark_failed(error_message)
            await self._repository.save(request)

            return ExecuteDownloadOutput(
                id=request.id,
                status=request.status.name.lower(),
                error_message=error_message,
            )