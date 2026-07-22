"""Repository interface for MediaRequest persistence.

This interface defines the contract for storing and retrieving MediaRequest
entities. Implementations belong in the infrastructure layer, keeping the
domain layer completely framework-independent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.media_request import MediaRequest


class MediaRepository(ABC):
    """Abstract repository for MediaRequest persistence operations."""

    @abstractmethod
    async def save(self, request: MediaRequest) -> MediaRequest:
        """Persist a new or updated MediaRequest.

        Args:
            request: The MediaRequest entity to persist.

        Returns:
            The persisted MediaRequest with any generated fields populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, request_id: str) -> Optional[MediaRequest]:
        """Retrieve a MediaRequest by its unique identifier.

        Args:
            request_id: The unique identifier of the request.

        Returns:
            The MediaRequest if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MediaRequest]:
        """Retrieve a paginated list of all MediaRequests.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip for pagination.

        Returns:
            A list of MediaRequest entities.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, request_id: str) -> bool:
        """Delete a MediaRequest by its unique identifier.

        Args:
            request_id: The unique identifier of the request to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of MediaRequest records.

        Returns:
            Total count of persisted requests.
        """
        raise NotImplementedError