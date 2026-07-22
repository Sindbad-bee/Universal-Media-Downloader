"""Unit tests for InMemoryMediaRepository."""

import pytest

from src.domain.entities.media_request import (
    AudioFormat,
    DownloadStatus,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.infrastructure.adapters.in_memory_repository import InMemoryMediaRepository


@pytest.mark.asyncio
class TestInMemoryMediaRepository:
    """Tests for InMemoryMediaRepository."""

    async def test_save_and_find_by_id(self) -> None:
        """Test saving and retrieving a request by ID."""
        repo = InMemoryMediaRepository()
        request = MediaRequest(
            url="https://www.youtube.com/watch?v=test123",
            media_type=MediaType.VIDEO_WITH_AUDIO,
            video_quality=VideoQuality.BEST,
            audio_format=AudioFormat.MP3,
        )
        request.mark_queued()

        saved = await repo.save(request)
        assert saved.id == request.id
        assert saved.status == DownloadStatus.QUEUED

        found = await repo.find_by_id(request.id)
        assert found is not None
        assert found.id == request.id
        assert found.url == request.url
        assert found.status == DownloadStatus.QUEUED

    async def test_find_by_id_not_found(self) -> None:
        """Test finding a non-existent request returns None."""
        repo = InMemoryMediaRepository()
        found = await repo.find_by_id("nonexistent-id")
        assert found is None

    async def test_save_updates_existing_request(self) -> None:
        """Test that saving an existing request updates it."""
        repo = InMemoryMediaRepository()
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        # Update the request
        request.mark_in_progress()
        await repo.save(request)

        found = await repo.find_by_id(request.id)
        assert found is not None
        assert found.status == DownloadStatus.IN_PROGRESS

    async def test_find_all_empty(self) -> None:
        """Test find_all returns empty list when repository is empty."""
        repo = InMemoryMediaRepository()
        requests = await repo.find_all()
        assert requests == []

    async def test_find_all_with_pagination(self) -> None:
        """Test find_all with pagination parameters."""
        repo = InMemoryMediaRepository()

        # Create 10 requests
        for i in range(10):
            request = MediaRequest(
                url=f"https://example.com/video{i}",
                media_type=MediaType.VIDEO,
                video_quality=VideoQuality.HD_720P,
                audio_format=AudioFormat.MP3,
            )
            request.mark_queued()
            await repo.save(request)

        # Test pagination
        page1 = await repo.find_all(limit=3, offset=0)
        assert len(page1) == 3

        page2 = await repo.find_all(limit=3, offset=3)
        assert len(page2) == 3

        page3 = await repo.find_all(limit=3, offset=6)
        assert len(page3) == 3

        page4 = await repo.find_all(limit=3, offset=9)
        assert len(page4) == 1

    async def test_delete_existing_request(self) -> None:
        """Test deleting an existing request."""
        repo = InMemoryMediaRepository()
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        result = await repo.delete(request.id)
        assert result is True

        found = await repo.find_by_id(request.id)
        assert found is None

    async def test_delete_nonexistent_request(self) -> None:
        """Test deleting a non-existent request returns False."""
        repo = InMemoryMediaRepository()
        result = await repo.delete("nonexistent-id")
        assert result is False

    async def test_count_empty(self) -> None:
        """Test count returns 0 for empty repository."""
        repo = InMemoryMediaRepository()
        count = await repo.count()
        assert count == 0

    async def test_count_with_requests(self) -> None:
        """Test count returns correct number of requests."""
        repo = InMemoryMediaRepository()

        for i in range(5):
            request = MediaRequest(url=f"https://example.com/video{i}")
            request.mark_queued()
            await repo.save(request)

        count = await repo.count()
        assert count == 5

    async def test_deep_copy_prevents_mutation(self) -> None:
        """Test that returned requests are deep copies."""
        repo = InMemoryMediaRepository()
        request = MediaRequest(url="https://example.com/video")
        request.mark_queued()
        await repo.save(request)

        # Retrieve and modify the returned request
        found = await repo.find_by_id(request.id)
        assert found is not None
        found.mark_in_progress()

        # Original should not be affected
        original = await repo.find_by_id(request.id)
        assert original.status == DownloadStatus.QUEUED

    async def test_clear(self) -> None:
        """Test clearing all requests."""
        repo = InMemoryMediaRepository()

        for i in range(3):
            request = MediaRequest(url=f"https://example.com/video{i}")
            request.mark_queued()
            await repo.save(request)

        assert await repo.count() == 3

        await repo.clear()
        assert await repo.count() == 0
        requests = await repo.find_all()
        assert requests == []