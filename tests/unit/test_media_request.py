"""Unit tests for MediaRequest domain entity."""

import pytest

from src.domain.entities.media_request import (
    AudioFormat,
    DownloadStatus,
    InvalidStateTransitionError,
    MediaRequest,
    MediaType,
    VideoQuality,
)


class TestMediaRequestCreation:
    """Tests for MediaRequest entity creation and validation."""

    def test_create_valid_request(self) -> None:
        """Test creating a valid media request."""
        request = MediaRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            media_type=MediaType.VIDEO_WITH_AUDIO,
            video_quality=VideoQuality.BEST,
            audio_format=AudioFormat.MP3,
        )
        assert request.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert request.media_type == MediaType.VIDEO_WITH_AUDIO
        assert request.video_quality == VideoQuality.BEST
        assert request.audio_format == AudioFormat.MP3
        assert request.status == DownloadStatus.PENDING
        assert request.id is not None
        assert len(request.id) == 12

    def test_create_with_defaults(self) -> None:
        """Test creating a request with default values."""
        request = MediaRequest(url="https://example.com/video")
        assert request.media_type == MediaType.VIDEO_WITH_AUDIO
        assert request.video_quality == VideoQuality.BEST
        assert request.audio_format == AudioFormat.MP3
        assert request.output_directory is None
        assert request.filename_template is None
        assert request.error_message is None
        assert request.download_path is None

    def test_empty_url_raises_error(self) -> None:
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL must not be empty"):
            MediaRequest(url="")

    def test_whitespace_url_raises_error(self) -> None:
        """Test that whitespace-only URL raises ValueError."""
        with pytest.raises(ValueError, match="URL must not be empty"):
            MediaRequest(url="   ")

    def test_invalid_url_scheme_raises_error(self) -> None:
        """Test that URL without http/https raises ValueError."""
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            MediaRequest(url="ftp://example.com/file")


class TestMediaRequestStateTransitions:
    """Tests for state transition logic."""

    def test_pending_to_queued(self) -> None:
        """Test valid transition from PENDING to QUEUED."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        assert request.status == DownloadStatus.QUEUED

    def test_queued_to_in_progress(self) -> None:
        """Test valid transition from QUEUED to IN_PROGRESS."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        assert request.status == DownloadStatus.IN_PROGRESS

    def test_in_progress_to_completed(self) -> None:
        """Test valid transition from IN_PROGRESS to COMPLETED."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        request.mark_completed("/path/to/downloaded/file.mp4")
        assert request.status == DownloadStatus.COMPLETED
        assert request.download_path == "/path/to/downloaded/file.mp4"

    def test_in_progress_to_failed(self) -> None:
        """Test valid transition from IN_PROGRESS to FAILED."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        request.mark_failed("Network timeout")
        assert request.status == DownloadStatus.FAILED
        assert request.error_message == "Network timeout"

    def test_cancel_from_queued(self) -> None:
        """Test valid cancellation from QUEUED state."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.cancel()
        assert request.status == DownloadStatus.CANCELLED

    def test_cancel_from_in_progress(self) -> None:
        """Test valid cancellation from IN_PROGRESS state."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        request.cancel()
        assert request.status == DownloadStatus.CANCELLED

    def test_invalid_pending_to_completed_raises_error(self) -> None:
        """Test invalid transition from PENDING to COMPLETED raises error."""
        request = MediaRequest(url="https://example.com/video")
        with pytest.raises(InvalidStateTransitionError):
            request.mark_completed("/path/to/file.mp4")

    def test_invalid_queued_to_completed_raises_error(self) -> None:
        """Test invalid transition from QUEUED to COMPLETED raises error."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        with pytest.raises(InvalidStateTransitionError):
            request.mark_completed("/path/to/file.mp4")

    def test_invalid_completed_to_failed_raises_error(self) -> None:
        """Test invalid transition from COMPLETED to FAILED raises error."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        request.mark_completed("/path/to/file.mp4")
        with pytest.raises(InvalidStateTransitionError):
            request.mark_failed("Error")

    def test_invalid_cancelled_to_failed_raises_error(self) -> None:
        """Test invalid transition from CANCELLED to FAILED raises error."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.cancel()
        with pytest.raises(InvalidStateTransitionError):
            request.mark_failed("Error")

    def test_cancel_completed_raises_error(self) -> None:
        """Test that cancelling a completed request raises error."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.mark_in_progress()
        request.mark_completed("/path/to/file.mp4")
        with pytest.raises(InvalidStateTransitionError):
            request.cancel()

    def test_cancel_cancelled_raises_error(self) -> None:
        """Test that cancelling an already cancelled request raises error."""
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        request.cancel()
        with pytest.raises(InvalidStateTransitionError):
            request.cancel()


class TestMediaRequestEnums:
    """Tests for enum values."""

    def test_media_type_values(self) -> None:
        """Test MediaType enum has expected values."""
        assert MediaType.VIDEO.value == 1
        assert MediaType.AUDIO.value == 2
        assert MediaType.VIDEO_WITH_AUDIO.value == 3

    def test_download_status_values(self) -> None:
        """Test DownloadStatus enum has expected values."""
        assert DownloadStatus.PENDING.value == 1
        assert DownloadStatus.QUEUED.value == 2
        assert DownloadStatus.IN_PROGRESS.value == 3
        assert DownloadStatus.COMPLETED.value == 4
        assert DownloadStatus.FAILED.value == 5
        assert DownloadStatus.CANCELLED.value == 6

    def test_video_quality_values(self) -> None:
        """Test VideoQuality enum has expected string values."""
        assert VideoQuality.BEST.value == "best"
        assert VideoQuality.HD_1080P.value == "1080p"
        assert VideoQuality.HD_720P.value == "720p"
        assert VideoQuality.SD_480P.value == "480p"
        assert VideoQuality.SD_360P.value == "360p"
        assert VideoQuality.LOWEST.value == "worst"

    def test_audio_format_values(self) -> None:
        """Test AudioFormat enum has expected string values."""
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.M4A.value == "m4a"
        assert AudioFormat.OPUS.value == "opus"
        assert AudioFormat.FLAC.value == "flac"
        assert AudioFormat.WAV.value == "wav"