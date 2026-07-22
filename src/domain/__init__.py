"""Domain layer package - framework-independent business logic."""

from src.domain.entities import (
    AudioFormat,
    DownloadStatus,
    InvalidStateTransitionError,
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces import DownloaderService, MediaRepository
from src.domain.use_cases import (
    CreateDownloadRequestInput,
    CreateDownloadRequestOutput,
    CreateDownloadRequestUseCase,
    DownloadListItem,
    DownloadNotFoundError,
    DownloadRequestNotFoundError,
    ExecuteDownloadInput,
    ExecuteDownloadOutput,
    ExecuteDownloadUseCase,
    GetDownloadStatusInput,
    GetDownloadStatusOutput,
    GetDownloadStatusUseCase,
    ListDownloadsInput,
    ListDownloadsOutput,
    ListDownloadsUseCase,
)

__all__ = [
    "AudioFormat",
    "DownloadStatus",
    "InvalidStateTransitionError",
    "MediaRequest",
    "MediaType",
    "VideoQuality",
    "DownloaderService",
    "MediaRepository",
    "CreateDownloadRequestInput",
    "CreateDownloadRequestOutput",
    "CreateDownloadRequestUseCase",
    "DownloadListItem",
    "DownloadNotFoundError",
    "DownloadRequestNotFoundError",
    "ExecuteDownloadInput",
    "ExecuteDownloadOutput",
    "ExecuteDownloadUseCase",
    "GetDownloadStatusInput",
    "GetDownloadStatusOutput",
    "GetDownloadStatusUseCase",
    "ListDownloadsInput",
    "ListDownloadsOutput",
    "ListDownloadsUseCase",
]