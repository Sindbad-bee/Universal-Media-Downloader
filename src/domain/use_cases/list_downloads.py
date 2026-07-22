"""Use case for listing all download requests with pagination."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.domain.interfaces.media_repository import MediaRepository


@dataclass
class ListDownloadsInput:
    """Input data for listing download requests."""

    limit: int = 50
    offset: int = 0


@dataclass
class DownloadListItem:
    """Summary of a single download request for list display."""

    id: str
    url: str
    media_type: str
    status: str
    download_path: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ListDownloadsOutput:
    """Output data containing a paginated list of downloads."""

    items: List[DownloadListItem]
    total: int
    limit: int
    offset: int


class ListDownloadsUseCase:
    """Business logic for listing download requests."""

    def __init__(self, repository: MediaRepository) -> None:
        self._repository = repository

    async def execute(
        self, input_dto: ListDownloadsInput
    ) -> ListDownloadsOutput:
        """Retrieve a paginated list of all download requests.

        Args:
            input_dto: Pagination parameters.

        Returns:
            Output DTO with the list and total count.
        """
        requests = await self._repository.find_all(
            limit=input_dto.limit,
            offset=input_dto.offset,
        )
        total = await self._repository.count()

        items = [
            DownloadListItem(
                id=req.id,
                url=req.url,
                media_type=req.media_type.name.lower(),
                status=req.status.name.lower(),
                download_path=req.download_path,
                error_message=req.error_message,
            )
            for req in requests
        ]

        return ListDownloadsOutput(
            items=items,
            total=total,
            limit=input_dto.limit,
            offset=input_dto.offset,
        )