"""Unit tests for ListDownloadsUseCase."""

import pytest

from src.domain.entities.media_request import (
    DownloadStatus,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.media_repository import MediaRepository
from src.domain.use_cases.list_downloads import (
    ListDownloadsInput,
    ListDownloadsOutput,
    ListDownloadsUseCase,
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
        items = list(self._store.values())
        items.sort(key=lambda r: r.id)
        return items[offset : offset + limit]

    async def delete(self, request_id: str) -> bool:
        if request_id in self._store:
            del self._store[request_id]
            return True
        return False

    async def count(self) -> int:
        return len(self._store)


@pytest.mark.asyncio
class TestListDownloadsUseCase:
    """Tests for ListDownloadsUseCase."""

    async def test_list_downloads_empty(self) -> None:
        """Test listing downloads when repository is empty."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        input_dto = ListDownloadsInput(limit=50, offset=0)
        result = await use_case.execute(input_dto)

        assert isinstance(result, ListDownloadsOutput)
        assert result.items == []
        assert result.total == 0
        assert result.limit == 50
        assert result.offset == 0

    async def test_list_downloads_with_items(self) -> None:
        """Test listing downloads with multiple items."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        # Create and save multiple requests
        for i in range(3):
            request = MediaRequest(
                url=f"https://example.com/video{i}",
                media_type=MediaType.VIDEO_WITH_AUDIO,
                video_quality=VideoQuality.BEST,
            )
            request.mark_queued()
            await repo.save(request)

        input_dto = ListDownloadsInput(limit=50, offset=0)
        result = await use_case.execute(input_dto)

        assert len(result.items) == 3
        assert result.total == 3
        assert result.limit == 50
        assert result.offset == 0

    async def test_list_downloads_pagination(self) -> None:
        """Test pagination works correctly."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        # Create 10 requests
        for i in range(10):
            request = MediaRequest(
                url=f"https://example.com/video{i}",
                media_type=MediaType.VIDEO,
                video_quality=VideoQuality.HD_720P,
            )
            request.mark_queued()
            await repo.save(request)

        # Get first page
        page1 = await use_case.execute(ListDownloadsInput(limit=3, offset=0))
        assert len(page1.items) == 3
        assert page1.total == 10
        assert page1.limit == 3
        assert page1.offset == 0

        # Get second page
        page2 = await use_case.execute(ListDownloadsInput(limit=3, offset=3))
        assert len(page2.items) == 3
        assert page2.total == 10
        assert page2.offset == 3

        # Get last page
        page4 = await use_case.execute(ListDownloadsInput(limit=3, offset=9))
        assert len(page4.items) == 1
        assert page4.total == 10
        assert page4.offset == 9

    async def test_list_downloads_default_parameters(self) -> None:
        """Test listing with default parameters."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        for i in range(5):
            request = MediaRequest(url=f"https://example.com/video{i}")
            request.mark_queued()
            await repo.save(request)

        input_dto = ListDownloadsInput()  # Uses defaults
        result = await use_case.execute(input_dto)

        assert result.limit == 50
        assert result.offset == 0
        assert result.total == 5
        assert len(result.items) == 5

    async def test_list_downloads_items_have_correct_fields(self) -> None:
        """Test that list items contain expected fields."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        request = MediaRequest(
            url="https://www.youtube.com/watch?v=test123",
            media_type=MediaType.AUDIO,
            audio_format=MediaRequest.audio_format.value,
        )
        request.mark_queued()
        await repo.save(request)

        input_dto = ListDownloadsInput(limit=50, offset=0)
        result = await use_case.execute(input_dto)

        assert len(result.items) == 1
        item = result.items[0]
        assert item.id == request.id
        assert item.url == request.url
        assert item.media_type == "audio"
        assert item.status == "queued"
        assert item.download_path is None
        assert item.error_message is None

    async def test_list_downloads_with_different_statuses(self) -> None:
        """Test listing downloads with various statuses."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        # Create requests with different statuses
        request1 = MediaRequest(url="https://example.com/video1")
        request1.mark_queued()
        await repo.save(request1)

        request2 = MediaRequest(url="https://example.com/video2")
        request2.mark_queued()
        await repo.save(request2)
        request2.mark_in_progress()
        await repo.save(request2)

        request3 = MediaRequest(url="https://example.com/video3")
        request3.mark_queued()
        await repo.save(request3)
        request3.mark_completed("/downloads/video3.mp4")
        await repo.save(request3)

        input_dto = ListDownloadsInput(limit=50, offset=0)
        result = await use_case.execute(input_dto)

        assert len(result.items) == 3
        statuses = [item.status for item in result.items]
        assert "queued" in statuses
        assert "in_progress" in statuses
        assert "completed" in statuses

    async def test_list_downloads_offset_beyond_range(self) -> None:
        """Test listing with offset beyond available items."""
        repo = MockRepository()
        use_case = ListDownloadsUseCase(repository=repo)

        for i in range(3):
            request = MediaRequest(url=f"https://example.com/video{i}")
            request.mark_queued()
            await repo.save(request)

        input_dto = ListDownloadsInput(limit=10, offset=100)
        result = await use_case.execute(input_dto)

        assert len(result.items) == 0
        assert result.total == 3