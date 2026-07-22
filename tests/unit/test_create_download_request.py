"""Unit tests for CreateDownloadRequestUseCase."""

import pytest

from src.domain.entities.media_request import (
    AudioFormat,
    DownloadStatus,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.media_repository import MediaRepository
from src.domain.use_cases.create_download_request import (
    CreateDownloadRequestInput,
    CreateDownloadRequestOutput,
    CreateDownloadRequestUseCase,
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
class TestCreateDownloadRequestUseCase:
    """Tests for CreateDownloadRequestUseCase."""

    async def test_create_download_request_success(self) -> None:
        """Test successful creation of a download request."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            media_type="video_with_audio",
            video_quality="best",
            audio_format="mp3",
        )

        result = await use_case.execute(input_dto)

        assert isinstance(result, CreateDownloadRequestOutput)
        assert result.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result.media_type == "video_with_audio"
        assert result.video_quality == "best"
        assert result.audio_format == "mp3"
        assert result.status == "queued"
        assert result.id is not None

    async def test_create_download_request_with_custom_options(self) -> None:
        """Test creating a request with custom options."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://vimeo.com/123456",
            media_type="audio",
            video_quality="720p",
            audio_format="flac",
            output_directory="/custom/output",
            filename_template="%(title)s.%(ext)s",
        )

        result = await use_case.execute(input_dto)

        assert result.media_type == "audio"
        assert result.audio_format == "flac"
        assert result.status == "queued"

    async def test_create_download_request_invalid_url(self) -> None:
        """Test that invalid URL raises ValueError."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="not-a-valid-url",
            media_type="video",
            video_quality="best",
            audio_format="mp3",
        )

        with pytest.raises(ValueError):
            await use_case.execute(input_dto)

    async def test_create_download_request_persists_to_repository(self) -> None:
        """Test that the request is persisted to the repository."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://www.youtube.com/watch?v=test123",
            media_type="video",
            video_quality="1080p",
            audio_format="mp3",
        )

        result = await use_case.execute(input_dto)

        # Verify it's in the repository
        found = await repo.find_by_id(result.id)
        assert found is not None
        assert found.url == "https://www.youtube.com/watch?v=test123"
        assert found.status == DownloadStatus.QUEUED

    async def test_create_download_request_default_values(self) -> None:
        """Test that default values are applied correctly."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://example.com/video",
        )

        result = await use_case.execute(input_dto)

        assert result.media_type == "video_with_audio"
        assert result.video_quality == "best"
        assert result.audio_format == "mp3"
        assert result.status == "queued"

    async def test_create_download_request_audio_only(self) -> None:
        """Test creating an audio-only download request."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://www.youtube.com/watch?v=audio123",
            media_type="audio",
            audio_format="wav",
        )

        result = await use_case.execute(input_dto)

        assert result.media_type == "audio"
        assert result.audio_format == "wav"
        assert result.status == "queued"

    async def test_create_download_request_video_only(self) -> None:
        """Test creating a video-only download request."""
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)

        input_dto = CreateDownloadRequestInput(
            url="https://www.youtube.com/watch?v=video123",
            media_type="video",
            video_quality="480p",
        )

        result = await use_case.execute(input_dto)

        assert result.media_type == "video"
        assert result.video_quality == "480p"
        assert result.status == "queued"