"""Shared test fixtures and configuration."""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities.media_request import (
    MediaRequest,
    MediaType,
    VideoQuality,
    AudioFormat,
    DownloadStatus,
)
from src.infrastructure.adapters.in_memory_repository import (
    InMemoryMediaRepository,
)


@pytest.fixture
def sample_url() -> str:
    """Return a standard test URL."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_media_request() -> MediaRequest:
    """Create a sample MediaRequest entity for testing."""
    return MediaRequest(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        media_type=MediaType.VIDEO_WITH_AUDIO,
        video_quality=VideoQuality.BEST,
        audio_format=AudioFormat.MP3,
    )


@pytest_asyncio.fixture
async def empty_repository() -> AsyncGenerator[InMemoryMediaRepository, None]:
    """Provide an empty in-memory repository."""
    repo = InMemoryMediaRepository()
    yield repo
    await repo.clear()


@pytest_asyncio.fixture
async def populated_repository() -> AsyncGenerator[InMemoryMediaRepository, None]:
    """Provide a repository pre-populated with sample data."""
    repo = InMemoryMediaRepository()

    requests = [
        MediaRequest(
            url="https://www.youtube.com/watch?v=video1",
            media_type=MediaType.VIDEO_WITH_AUDIO,
            video_quality=VideoQuality.BEST,
            audio_format=AudioFormat.MP3,
        ),
        MediaRequest(
            url="https://vimeo.com/video2",
            media_type=MediaType.AUDIO,
            video_quality=VideoQuality.HD_720P,
            audio_format=AudioFormat.FLAC,
        ),
        MediaRequest(
            url="https://www.tiktok.com/video3",
            media_type=MediaType.VIDEO,
            video_quality=VideoQuality.HD_1080P,
            audio_format=AudioFormat.M4A,
        ),
    ]

    for req in requests:
        req.mark_queued()
        await repo.save(req)

    yield repo
    await repo.clear()