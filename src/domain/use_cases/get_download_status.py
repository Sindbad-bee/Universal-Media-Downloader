"""Use case for retrieving the status of a download request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.domain.entities.media_request import DownloadStatus
from src.domain.interfaces.media_repository import MediaRepository


class DownloadRequestNotFoundError(Exception):
    """Raised when the requested download ID does not exist."""

    pass


@dataclass
class GetDownloadStatusInput:
    """Input data for fetching a download's status."""

    request_id: str


@dataclass
class GetDownloadStatusOutput:
    """Output data containing the download request details."""

    id: str
    url: str
    media_type: str
    video_quality: str
    audio_format: str
    status: str
    download_path: Optional[str] = None
    error_message: Optional[str] = None


class GetDownloadStatusUseCase:
    """Business logic for retrieving download request status."""

    def __init__(self, repository: MediaRepository) -> None:
        self._repository = repository

    async def execute(
        self, input_dto: GetDownloadStatusInput
    ) -> GetDownloadStatusOutput:
        """Retrieve the current status of a download request.

        Args:
            input_dto: Contains the request ID to look up.

        Returns:
            Output DTO with the current state of the request.

        Raises:
            DownloadRequestNotFoundError: If the request ID does not exist.
        """
        request = await self._repository.find_by_id(input_dto.request_id)
        if request is None:
            raise DownloadRequestNotFoundError(
                f"Download request '{input_dto.request_id}' not found."
            )

        return GetDownloadStatusOutput(
            id=request.id,
            url=request.url,
            media_type=request.media_type.name.lower(),
            video_quality=request.video_quality.value,
            audio_format=request.audio_format.value,
            status=request.status.name.lower(),
            download_path=request.download_path,
            error_message=request.error_message,
        )