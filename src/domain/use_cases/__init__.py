"""Domain use cases package."""

from src.domain.use_cases.create_download_request import (
    CreateDownloadRequestInput,
    CreateDownloadRequestOutput,
    CreateDownloadRequestUseCase,
)
from src.domain.use_cases.execute_download import (
    DownloadNotFoundError,
    ExecuteDownloadInput,
    ExecuteDownloadOutput,
    ExecuteDownloadUseCase,
)
from src.domain.use_cases.get_download_status import (
    DownloadRequestNotFoundError,
    GetDownloadStatusInput,
    GetDownloadStatusOutput,
    GetDownloadStatusUseCase,
)
from src.domain.use_cases.list_downloads import (
    DownloadListItem,
    ListDownloadsInput,
    ListDownloadsOutput,
    ListDownloadsUseCase,
)

__all__ = [
    "CreateDownloadRequestInput",
    "CreateDownloadRequestOutput",
    "CreateDownloadRequestUseCase",
    "DownloadNotFoundError",
    "ExecuteDownloadInput",
    "ExecuteDownloadOutput",
    "ExecuteDownloadUseCase",
    "DownloadRequestNotFoundError",
    "GetDownloadStatusInput",
    "GetDownloadStatusOutput",
    "GetDownloadStatusUseCase",
    "DownloadListItem",
    "ListDownloadsInput",
    "ListDownloadsOutput",
    "ListDownloadsUseCase",
]