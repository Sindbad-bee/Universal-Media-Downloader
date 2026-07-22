"""REST API controller for media download operations.

This controller defines all HTTP endpoints and delegates business logic
to the appropriate use cases via dependency injection.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.domain.use_cases.create_download_request import (
    CreateDownloadRequestInput,
    CreateDownloadRequestUseCase,
)
from src.domain.use_cases.execute_download import (
    DownloadNotFoundError,
    ExecuteDownloadInput,
    ExecuteDownloadUseCase,
)
from src.domain.use_cases.get_download_status import (
    DownloadRequestNotFoundError,
    GetDownloadStatusInput,
    GetDownloadStatusUseCase,
)
from src.domain.use_cases.list_downloads import (
    ListDownloadsInput,
    ListDownloadsUseCase,
)
from src.infrastructure.adapters.in_memory_repository import InMemoryMediaRepository
from src.infrastructure.adapters.yt_dlp_adapter import YtDlpAdapter
from src.infrastructure.errors.app_errors import ResourceNotFoundError, ValidationError
from src.infrastructure.logging.logger import get_logger
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

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Downloads"])


# ── Dependency Injection ──────────────────────────────────────────

def _get_repository() -> InMemoryMediaRepository:
    """Provide the repository singleton.

    In production, this would be replaced with a database-backed repository.
    """
    from src.presentation.app import get_repository
    return get_repository()


def _get_downloader() -> YtDlpAdapter:
    """Provide the downloader service singleton."""
    from src.presentation.app import get_downloader
    return get_downloader()


def _get_create_use_case(
    repo: InMemoryMediaRepository = Depends(_get_repository),
) -> CreateDownloadRequestUseCase:
    return CreateDownloadRequestUseCase(repository=repo)


def _get_execute_use_case(
    repo: InMemoryMediaRepository = Depends(_get_repository),
    downloader: YtDlpAdapter = Depends(_get_downloader),
) -> ExecuteDownloadUseCase:
    return ExecuteDownloadUseCase(repository=repo, downloader=downloader)


def _get_status_use_case(
    repo: InMemoryMediaRepository = Depends(_get_repository),
) -> GetDownloadStatusUseCase:
    return GetDownloadStatusUseCase(repository=repo)


def _get_list_use_case(
    repo: InMemoryMediaRepository = Depends(_get_repository),
) -> ListDownloadsUseCase:
    return ListDownloadsUseCase(repository=repo)


# ── Endpoints ─────────────────────────────────────────────────────


@router.post(
    "/downloads",
    response_model=DownloadRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new download request",
    description="Submit a URL and configuration to create a download request.",
)
async def create_download(
    body: CreateDownloadRequest,
    use_case: CreateDownloadRequestUseCase = Depends(_get_create_use_case),
) -> DownloadRequestResponse:
    """Create a new download request and return its details."""
    logger.info("POST /downloads", url=body.url, media_type=body.media_type)

    input_dto = CreateDownloadRequestInput(
        url=body.url,
        media_type=body.media_type,
        video_quality=body.video_quality,
        audio_format=body.audio_format,
        output_directory=body.output_directory,
        filename_template=body.filename_template,
    )

    try:
        result = await use_case.execute(input_dto)
    except ValueError as exc:
        raise ValidationError(message=str(exc))

    return DownloadRequestResponse(
        id=result.id,
        url=result.url,
        media_type=result.media_type,
        video_quality=result.video_quality,
        audio_format=result.audio_format,
        status=result.status,
        message="Download request created and queued successfully.",
    )


@router.get(
    "/downloads/{request_id}",
    response_model=DownloadStatusResponse,
    summary="Get download status",
    description="Retrieve the current status and details of a download request.",
)
async def get_download_status(
    request_id: str,
    use_case: GetDownloadStatusUseCase = Depends(_get_status_use_case),
) -> DownloadStatusResponse:
    """Get the current status of a download by its ID."""
    logger.info("GET /downloads/{request_id}", request_id=request_id)

    input_dto = GetDownloadStatusInput(request_id=request_id)

    try:
        result = await use_case.execute(input_dto)
    except DownloadRequestNotFoundError as exc:
        raise ResourceNotFoundError(
            message=str(exc),
            resource_type="download_request",
            resource_id=request_id,
        )

    return DownloadStatusResponse(
        id=result.id,
        url=result.url,
        media_type=result.media_type,
        video_quality=result.video_quality,
        audio_format=result.audio_format,
        status=result.status,
        download_path=result.download_path,
        error_message=result.error_message,
    )


@router.post(
    "/downloads/{request_id}/execute",
    response_model=DownloadStatusResponse,
    summary="Execute a download",
    description="Start the actual download process for a previously created request.",
)
async def execute_download(
    request_id: str,
    use_case: ExecuteDownloadUseCase = Depends(_get_execute_use_case),
) -> DownloadStatusResponse:
    """Execute a download request by its ID."""
    logger.info("POST /downloads/{request_id}/execute", request_id=request_id)

    input_dto = ExecuteDownloadInput(request_id=request_id)

    try:
        result = await use_case.execute(input_dto)
    except DownloadNotFoundError as exc:
        raise ResourceNotFoundError(
            message=str(exc),
            resource_type="download_request",
            resource_id=request_id,
        )

    return DownloadStatusResponse(
        id=result.id,
        url="",  # Will be populated from the status endpoint
        media_type="",
        video_quality="",
        audio_format="",
        status=result.status,
        download_path=result.download_path,
        error_message=result.error_message,
    )


@router.get(
    "/downloads",
    response_model=ListDownloadsResponse,
    summary="List all downloads",
    description="Retrieve a paginated list of all download requests.",
)
async def list_downloads(
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    use_case: ListDownloadsUseCase = Depends(_get_list_use_case),
) -> ListDownloadsResponse:
    """List all download requests with pagination."""
    logger.info("GET /downloads", limit=limit, offset=offset)

    input_dto = ListDownloadsInput(limit=limit, offset=offset)
    result = await use_case.execute(input_dto)

    items = [
        DownloadStatusResponse(
            id=item.id,
            url=item.url,
            media_type=item.media_type,
            video_quality="",
            audio_format="",
            status=item.status,
            download_path=item.download_path,
            error_message=item.error_message,
        )
        for item in result.items
    ]

    return ListDownloadsResponse(
        items=items,
        pagination=PaginationInfo(
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            has_more=(result.offset + result.limit) < result.total,
        ),
    )


@router.post(
    "/downloads/{request_id}/cancel",
    response_model=CancelDownloadResponse,
    summary="Cancel a download",
    description="Cancel an in-progress or queued download request.",
)
async def cancel_download(
    request_id: str,
    downloader: YtDlpAdapter = Depends(_get_downloader),
    repo: InMemoryMediaRepository = Depends(_get_repository),
) -> CancelDownloadResponse:
    """Cancel a download by its ID."""
    logger.info("POST /downloads/{request_id}/cancel", request_id=request_id)

    # Cancel the active process
    cancelled = await downloader.cancel_download(request_id)

    # Update the request status in the repository
    request = await repo.find_by_id(request_id)
    if request is None:
        raise ResourceNotFoundError(
            message=f"Download request '{request_id}' not found.",
            resource_type="download_request",
            resource_id=request_id,
        )

    request.cancel()
    await repo.save(request)

    return CancelDownloadResponse(
        id=request_id,
        status="cancelled",
        message="Download cancelled successfully."
        if cancelled
        else "No active download process found.",
    )


@router.post(
    "/validate-url",
    response_model=UrlValidateResponse,
    summary="Validate a URL",
    description="Check if a URL is supported by the downloader.",
)
async def validate_url(
    body: UrlValidateRequest,
    downloader: YtDlpAdapter = Depends(_get_downloader),
) -> UrlValidateResponse:
    """Validate whether a URL is supported for downloading."""
    logger.info("POST /validate-url", url=body.url)

    try:
        metadata = await downloader.fetch_metadata(body.url)
        return UrlValidateResponse(
            url=body.url,
            supported=True,
            extractor=metadata.get("extractor"),
            title=metadata.get("title"),
        )
    except Exception:
        return UrlValidateResponse(
            url=body.url,
            supported=False,
            extractor=None,
            title=None,
        )


@router.get(
    "/metadata",
    response_model=DownloadMetadataResponse,
    summary="Fetch media metadata",
    description="Retrieve metadata about a media URL without downloading.",
)
async def fetch_metadata(
    url: str = Query(..., description="The media URL to inspect"),
    downloader: YtDlpAdapter = Depends(_get_downloader),
) -> DownloadMetadataResponse:
    """Fetch metadata for a given URL."""
    logger.info("GET /metadata", url=url)

    try:
        metadata = await downloader.fetch_metadata(url)
    except Exception as exc:
        raise ValidationError(
            message=f"Failed to fetch metadata: {str(exc)}",
            details={"url": url},
        )

    return DownloadMetadataResponse(
        title=metadata.get("title"),
        duration=metadata.get("duration"),
        uploader=metadata.get("uploader"),
        upload_date=metadata.get("upload_date"),
        extractor=metadata.get("extractor"),
        webpage_url=metadata.get("webpage_url"),
        thumbnail=metadata.get("thumbnail"),
        formats=metadata.get("formats"),
        raw=metadata,
    )


@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint.",
)
async def health_check() -> dict:
    """Return a simple health check response."""
    return {
        "status": "healthy",
        "service": "universal-media-downloader",
    }