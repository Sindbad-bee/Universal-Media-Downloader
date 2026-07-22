"""Unit tests for ExecuteDownloadUseCase."""

import pytest

from src.domain.entities.media_request import (
    DownloadStatus,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.downloader_service import DownloaderService
from src.domain.interfaces.media_repository import MediaRepository
from src.domain.use_cases.execute_download import (
    DownloadNotFoundError,
    ExecuteDownloadInput,
    ExecuteDownloadOutput,
    ExecuteDownloadUseCase,
)


class MockDownloader(DownloaderService):
    """Mock downloader for testing."""

    def __init__(self) -> None:
        self.should_fail = False
        self.downloaded_files: dict[str, str] = {}

    async def fetch_metadata(self, url: str) -> dict:
        return {"title": "Test Video", "extractor": "youtube"}

    async def download(self, request: MediaRequest) -> str:
        if self.should_fail:
            raise Exception("Download failed")
        path = f"/downloads/{request.id}.mp4"
        self.downloaded_files[request.id] = path
        return path

    async def cancel_download(self, request_id: str) -> bool:
        return True

    async def validate_url(self, url: str) -> bool:
        return True


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
class TestExecuteDownloadUseCase:
    """Tests for ExecuteDownloadUseCase."""

    async def test_execute_download_success(self) -> None:
        """Test successful download execution."""
        repo = MockRepository()
        downloader = MockDownloader()
        use_case = ExecuteDownloadUseCase(
            repository=repo,
            downloader=downloader,
        )

        # Create and save a request
        request = MediaRequest(
            url="https://www.youtube.com/watch?v=test123",
            media_type=MediaType.VIDEO_WITH_AUDIO,
            video_quality=VideoQuality.BEST,
        )
        request.mark_queued()
        await repo.save(request)

        # Execute the download
        input_dto = ExecuteDownloadInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert isinstance(result, ExecuteDownloadOutput)
        assert result.id == request.id
        assert result.status == "completed"
        assert result.download_path is not None
        assert result.error_message is None

    async def test_execute_download_not_found(self) -> None:
        """Test executing a non-existent download raises error."""
        repo = MockRepository()
        downloader = MockDownloader()
        use_case = ExecuteDownloadUseCase(
            repository=repo,
            downloader=downloader,
        )

        input_dto = ExecuteDownloadInput(request_id="nonexistent-id")

        with pytest.raises(DownloadNotFoundError):
            await use_case.execute(input_dto)

    async def test_execute_download_failure(self) -> None:
        """Test handling of download failure."""
        repo = MockRepository()
        downloader = MockDownloader()
        downloader.should_fail = True
        use_case = ExecuteDownloadUseCase(
            repository=repo,
            downloader=downloader,
        )

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        # Execute the download
        input_dto = ExecuteDownloadInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.id == request.id
        assert result.status == "failed"
        assert result.error_message is not None
        assert "Download failed" in result.error_message

    async def test_execute_download_status_transitions(self) -> None:
        """Test that status transitions correctly during download."""
        repo = MockRepository()
        downloader = MockDownloader()
        use_case = ExecuteDownloadUseCase(
            repository=repo,
            downloader=downloader,
        )

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        # Verify initial status
        assert request.status == DownloadStatus.QUEUED

        # Execute the download
        input_dto = ExecuteDownloadInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        # Verify final status
        assert result.status == "completed"

        # Verify the persisted request has correct status
        updated = await repo.find_by_id(request.id)
        assert updated.status == DownloadStatus.COMPLETED
        assert updated.download_path is not None

    async def test_execute_download_sets_download_path(self) -> None:
        """Test that download path is set on completion."""
        repo = MockRepository()
        downloader = MockDownloader()
        use_case = ExecuteDownloadUseCase(
            repository=repo,
            downloader=downloader,
        )

        # Create and save a request
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        # Execute the download
        input_dto = ExecuteDownloadInput(request_id=request.id)
        result = await use_case.execute(input_dto)

        assert result.download_path is not None
        assert request.id in result.download_path