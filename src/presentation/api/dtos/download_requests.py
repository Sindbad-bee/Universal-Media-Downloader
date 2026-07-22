"""Pydantic models for API request/response validation.

These DTOs are framework-aware (Pydantic/FastAPI) and represent the
API contract with external consumers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class CreateDownloadRequest(BaseModel):
    """Request body for creating a new download."""

    url: str = Field(
        ...,
        description="URL of the media to download.",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    media_type: str = Field(
        default="video_with_audio",
        description="Type of media: 'video', 'audio', or 'video_with_audio'.",
        pattern=r"^(video|audio|video_with_audio)$",
    )
    video_quality: str = Field(
        default="best",
        description="Video quality preset: best, 1080p, 720p, 480p, 360p, worst.",
        pattern=r"^(best|1080p|720p|480p|360p|worst)$",
    )
    audio_format: str = Field(
        default="mp3",
        description="Audio output format: mp3, m4a, opus, flac, wav.",
        pattern=r"^(mp3|m4a|opus|flac|wav)$",
    )
    output_directory: Optional[str] = Field(
        default=None,
        description="Custom output directory path override.",
    )
    filename_template: Optional[str] = Field(
        default=None,
        description="Custom filename template (e.g., '%(title)s.%(ext)s').",
    )


class DownloadRequestResponse(BaseModel):
    """Response returned after creating a download request."""

    id: str = Field(..., description="Unique identifier for the download request.")
    url: str = Field(..., description="The source URL being downloaded.")
    media_type: str = Field(..., description="Type of media being downloaded.")
    video_quality: str = Field(..., description="Video quality setting.")
    audio_format: str = Field(..., description="Audio format setting.")
    status: str = Field(..., description="Current status of the download.")
    message: str = Field(
        ...,
        description="Human-readable status message.",
    )


class DownloadStatusResponse(BaseModel):
    """Response containing the current status of a download."""

    id: str = Field(..., description="Unique identifier of the download.")
    url: str = Field(..., description="The source URL.")
    media_type: str = Field(..., description="Type of media.")
    video_quality: str = Field(..., description="Video quality setting.")
    audio_format: str = Field(..., description="Audio format setting.")
    status: str = Field(..., description="Current status of the download.")
    download_path: Optional[str] = Field(
        default=None,
        description="Path where the downloaded file is saved (only when completed).",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error description if the download failed.",
    )


class DownloadMetadataResponse(BaseModel):
    """Response containing media metadata from yt-dlp."""

    title: Optional[str] = Field(default=None, description="Media title.")
    duration: Optional[int] = Field(default=None, description="Duration in seconds.")
    uploader: Optional[str] = Field(default=None, description="Uploader/channel name.")
    upload_date: Optional[str] = Field(default=None, description="Upload date (YYYYMMDD).")
    extractor: Optional[str] = Field(default=None, description="Site extractor name.")
    webpage_url: Optional[str] = Field(default=None, description="Original webpage URL.")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail URL.")
    formats: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Available formats (summary).",
    )
    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full raw metadata from yt-dlp.",
    )


class PaginationInfo(BaseModel):
    """Pagination metadata included in list responses."""

    total: int = Field(..., description="Total number of records.")
    limit: int = Field(..., description="Maximum records returned in this page.")
    offset: int = Field(..., description="Offset used for this page.")
    has_more: bool = Field(..., description="Whether more records are available.")


class ListDownloadsResponse(BaseModel):
    """Response containing a paginated list of downloads."""

    items: List[DownloadStatusResponse] = Field(
        ...,
        description="List of download request summaries.",
    )
    pagination: PaginationInfo = Field(
        ...,
        description="Pagination metadata.",
    )


class CancelDownloadResponse(BaseModel):
    """Response indicating the result of a cancel operation."""

    id: str = Field(..., description="Unique identifier of the cancelled download.")
    status: str = Field(..., description="Updated status after cancellation.")
    message: str = Field(..., description="Human-readable cancellation message.")


class UrlValidateRequest(BaseModel):
    """Request body for URL validation."""

    url: str = Field(
        ...,
        description="URL to validate.",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class UrlValidateResponse(BaseModel):
    """Response indicating whether a URL is supported."""

    url: str = Field(..., description="The validated URL.")
    supported: bool = Field(..., description="Whether the URL is supported.")
    extractor: Optional[str] = Field(
        default=None,
        description="Name of the extractor that can handle this URL.",
    )
    title: Optional[str] = Field(
        default=None,
        description="Media title if available.",
    )