"""Unit tests for GetDownloadStatusUseCase."""

import pytest

from src.domain.entities.media_request import (
    DownloadStatus,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.media_repository import MediaRepository
from src.domain.use_cases.get_download_status import (
    DownloadRequestNotFoundError,
    GetDownloadStatusInput,
    GetDownloadStatusOutput,
    GetDownloadStatusUseCase,
)


class MockRepository(MediaRepository):
    """Mock repository for testing."""

    def __init__(self) -> None:
        self._store: dict[str, MediaRequest] = {}

    async def save(self, request: MediaRequest) -> MediaRequest:
        self._store[request.id] = request
        return request

    async def find_by_id(self, request_id: str):
        return self._store.get(request_id)

    async def find_all(self, limit: int = 50, offset: int = 0):
        return list(self._store.values())[offset : offset + limit]

    async def delete(self, request_id: str) -> bool:
        if request_id in self._store:
            del self._store[request_id]
            return True
        return False

    async def count(self) -> int:
        return len(self._store)


@pytest.mark.asyncio
class TestGetDownloadStatusUseCase:
    """Tests for GetDownloadStatusUseCase."""

    async def test_get_status_success(self) -> None:
        """Test successfully retrieving download status."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(
            url="https://www.youtube.com/watch?v=test123",
            media_type=MediaType.VIDEO_WITH_AUDIO,
            video_quality=VideoQuality.BEST,
        )
        request.mark_queued()
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert isinstance(result, GetDownloadStatusOutput)
        assert result.id == request.id
        assert result.url == request.url
        assert result.media_type == "video_with_audio"
        assert result.video_quality == "best"
        assert result.status == "queued"
        assert result.download_path is None
        assert result.error_message is None

    async def test_get_status_completed_with_path(self) -> None:
        """Test retrieving status of a completed download."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)
        request.mark_in_progress()
        await repo.save(request)
        request.mark_completed("/downloads/video.mp4")
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.status == "completed"
        assert result.download_path == "/downloads/video.mp4"
        assert result.error_message is None

    async def test_get_status_failed_with_error(self) -> None:
        """Test retrieving status of a failed download."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)
        request.mark_in_progress()
        await repo.save(request)
        request.mark_failed("Network timeout")
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.status == "failed"
        assert result.error_message == "Network timeout"
        assert result.download_path is None

    async def test_get_status_not_found(self) -> None:
        """Test that requesting status of non-existent ID raises error."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        input_dto = GetDownloadStatusInput(request_id="nonexistent-id")

        with pytest.raises(DownloadRequestNotFoundError):
            await use_case.execute(input_dto)

    async def test_get_status_audio_only(self) -> None:
        """Test retrieving status of an audio-only request."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(
            url="https://example.com/audio",
            media_type=MediaType.AUDIO,
            audio_format=MediaRequest.audio_format.value,
        )
        request.mark_queued()
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.media_type == "audio"
        assert result.audio_format == "mp3"

    async def test_get_status_video_only(self) -> None:
        """Test retrieving status of a video-only request."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(
            url="https://example.com/video",
            media_type=MediaType.VIDEO,
            video_quality=VideoQuality.HD_1080P,
        )
        request.mark_queued()
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.media_type == "video"
        assert result.video_quality == "1080p"

    async def test_get_status_cancelled(self) -> None:
        """Test retrieving status of a cancelled request."""
        repo = MockRepository()
        use_case = GetDownloadStatusUseCase(repository=repo)

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)
        request.cancel()
        await repo.save(request)

        # Get status
        input_dto = GetDownloadStatusInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.status == "cancelled"