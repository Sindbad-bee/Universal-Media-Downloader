"""Use case for creating a new media download request.

This use case encapsulates the business logic of validating and creating
a download request before delegating to any infrastructure concerns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.domain.entities.media_request import (
    AudioFormat,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.media_repository import MediaRepository


@dataclass
class CreateDownloadRequestInput:
    """Input data for creating a download request.

    This is a plain data transfer object with no framework dependencies.
    """

    url: str
    media_type: str = "video_with_audio"
    video_quality: str = "best"
    audio_format: str = "mp3"
    output_directory: Optional[str] = None
    filename_template: Optional[str] = None


@dataclass
class CreateDownloadRequestOutput:
    """Output data returned after creating a download request."""

    id: str
    url: str
    media_type: str
    video_quality: str
    audio_format: str
    status: str


class CreateDownloadRequestUseCase:
    """Business logic for creating a new download request.

    This use case validates inputs, constructs a domain entity, persists it,
    and returns the result. It depends only on abstractions (interfaces).
    """

    def __init__(self, repository: MediaRepository) -> None:
        self._repository = repository

    async def execute(
        self, input_dto: CreateDownloadRequestInput
    ) -> CreateDownloadRequestOutput:
        """Execute the use case to create a new download request.

        Args:
            input_dto: Validated input parameters for the request.

        Returns:
            Output DTO containing the created request details.

        Raises:
            ValueError: If the input URL or parameters are invalid.
        """
        # Map string media_type to enum
        media_type_map = {
            "video": MediaType.VIDEO,
            "audio": MediaType.AUDIO,
            "video_with_audio": MediaType.VIDEO_WITH_AUDIO,
        }
        mapped_media_type = media_type_map.get(
            input_dto.media_type, MediaType.VIDEO_WITH_AUDIO
        )

        # Map string video_quality to enum
        quality_map = {
            "best": VideoQuality.BEST,
            "1080p": VideoQuality.HD_1080P,
            "720p": VideoQuality.HD_720P,
            "480p": VideoQuality.SD_480P,
            "360p": VideoQuality.SD_360P,
            "worst": VideoQuality.LOWEST,
        }
        mapped_quality = quality_map.get(
            input_dto.video_quality, VideoQuality.BEST
        )

        # Map string audio_format to enum
        audio_format_map = {
            "mp3": AudioFormat.MP3,
            "m4a": AudioFormat.M4A,
            "opus": AudioFormat.OPUS,
            "flac": AudioFormat.FLAC,
            "wav": AudioFormat.WAV,
        }
        mapped_audio_format = audio_format_map.get(
            input_dto.audio_format, AudioFormat.MP3
        )

        # Create domain entity (validation happens in __post_init__)
        request = MediaRequest(
            url=input_dto.url,
            media_type=mapped_media_type,
            video_quality=mapped_quality,
            audio_format=mapped_audio_format,
            output_directory=input_dto.output_directory,
            filename_template=input_dto.filename_template,
        )

        # Mark as queued (business rule: request starts preparing)
        request.mark_queued()

        # Persist via the repository interface
        persisted = await self._repository.save(request)

        # Return output DTO
        return CreateDownloadRequestOutput(
            id=persisted.id,
            url=persisted.url,
            media_type=persisted.media_type.name.lower(),
            video_quality=persisted.video_quality.value,
            audio_format=persisted.audio_format.value,
            status=persisted.status.name.lower(),
        )