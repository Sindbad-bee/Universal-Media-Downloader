"""API DTOs package."""

from src.presentation.api.dtos.download_requests import (
    CancelDownloadResponse,
    CreateDownloadRequest,
    DownloadMetadataResponse,
    DownloadRequestResponse,
    DownloadStatusResponse,
    ListDownloadsResponse,
    PaginationInfo,
    UrlValidateRequest,
    UrlValidateResponse,
)

__all__ = [
    "CancelDownloadResponse",
    "CreateDownloadRequest",
    "DownloadMetadataResponse",
    "DownloadRequestResponse",
    "DownloadStatusResponse",
    "ListDownloadsResponse",
    "PaginationInfo",
    "UrlValidateRequest",
    "UrlValidateResponse",
]