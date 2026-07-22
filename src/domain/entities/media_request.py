"""Domain entity representing a media download request.

This entity is completely framework-independent and represents the core
business concept of a media download operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from uuid import uuid4


class MediaType(Enum):
    """Supported media types for download."""

    VIDEO = auto()
    AUDIO = auto()
    VIDEO_WITH_AUDIO = auto()


class DownloadStatus(Enum):
    """Possible states of a download request through its lifecycle."""

    PENDING = auto()
    QUEUED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class VideoQuality(Enum):
    """Standard video quality presets."""

    BEST = "best"
    HD_1080P = "1080p"
    HD_720P = "720p"
    SD_480P = "480p"
    SD_360P = "360p"
    LOWEST = "worst"


class AudioFormat(Enum):
    """Supported audio output formats."""

    MP3 = "mp3"
    M4A = "m4a"
    OPUS = "opus"
    FLAC = "flac"
    WAV = "wav"


@dataclass
class MediaRequest:
    """Core domain entity representing a request to download media.

    Attributes:
        id: Unique identifier for the request.
        url: Source URL of the media to download.
        media_type: Type of media to extract (video, audio, or both).
        video_quality: Desired video quality (only relevant for video types).
        audio_format: Desired audio output format (only relevant for audio types).
        output_directory: Custom output directory path override.
        filename_template: Custom filename template (e.g. '%(title)s.%(ext)s').
        status: Current lifecycle status of the request.
        error_message: Human-readable error message if status is FAILED.
        download_path: Path where the downloaded file was saved upon completion.
    """

    url: str
    media_type: MediaType = MediaType.VIDEO_WITH_AUDIO
    video_quality: VideoQuality = VideoQuality.BEST
    audio_format: AudioFormat = AudioFormat.MP3
    output_directory: Optional[str] = None
    filename_template: Optional[str] = None
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    status: DownloadStatus = DownloadStatus.PENDING
    error_message: Optional[str] = None
    download_path: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the entity upon creation."""
        self._validate()

    def _validate(self) -> None:
        """Perform domain validation rules."""
        if not self.url or not self.url.strip():
            raise ValueError("URL must not be empty")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

    def mark_queued(self) -> None:
        """Transition status to QUEUED."""
        if self.status != DownloadStatus.PENDING:
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status.name} to QUEUED"
            )
        self.status = DownloadStatus.QUEUED

    def mark_in_progress(self) -> None:
        """Transition status to IN_PROGRESS."""
        if self.status != DownloadStatus.QUEUED:
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status.name} to IN_PROGRESS"
            )
        self.status = DownloadStatus.IN_PROGRESS

    def mark_completed(self, download_path: str) -> None:
        """Transition status to COMPLETED with the final file path."""
        if self.status != DownloadStatus.IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status.name} to COMPLETED"
            )
        self.status = DownloadStatus.COMPLETED
        self.download_path = download_path

    def mark_failed(self, error_message: str) -> None:
        """Transition status to FAILED with an error description."""
        if self.status in (DownloadStatus.COMPLETED, DownloadStatus.CANCELLED):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status.name} to FAILED"
            )
        self.status = DownloadStatus.FAILED
        self.error_message = error_message

    def cancel(self) -> None:
        """Cancel this download request."""
        if self.status in (DownloadStatus.COMPLETED, DownloadStatus.CANCELLED):
            raise InvalidStateTransitionError(
                f"Cannot cancel a download in {self.status.name} state"
            )
        self.status = DownloadStatus.CANCELLED


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted on a MediaRequest."""

    pass