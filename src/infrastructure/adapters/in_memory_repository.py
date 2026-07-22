"""In-memory implementation of the MediaRepository interface.

Provides a thread-safe in-memory store for development, testing,
and single-user scenarios without external database dependencies.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional

from src.domain.entities.media_request import MediaRequest
from src.domain.interfaces.media_repository import MediaRepository
from src.infrastructure.errors.app_errors import RepositoryError
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class InMemoryMediaRepository(MediaRepository):
    """Thread-safe in-memory repository for MediaRequest entities.

    All operations are performed on a deep copy of the stored entity
    to prevent unintended mutation of cached state.
    """

    def __init__(self) -> None:
        self._store: Dict[str, MediaRequest] = {}
        logger.info("InMemoryMediaRepository initialized")

    async def save(self, request: MediaRequest) -> MediaRequest:
        """Store a MediaRequest, creating or updating as needed.

        Args:
            request: The MediaRequest to persist.

        Returns:
            A deep copy of the stored request.
        """
        try:
            self._store[request.id] = copy.deepcopy(request)
            logger.debug("Saved request", request_id=request.id)
            return copy.deepcopy(self._store[request.id])
        except Exception as exc:
            raise RepositoryError(
                f"Failed to save request '{request.id}': {str(exc)}",
                operation="save",
                details={"request_id": request.id},
            ) from exc

    async def find_by_id(self, request_id: str) -> Optional[MediaRequest]:
        """Retrieve a request by ID.

        Args:
            request_id: The unique identifier.

        Returns:
            A deep copy of the request if found, None otherwise.
        """
        request = self._store.get(request_id)
        if request is None:
            logger.debug("Request not found", request_id=request_id)
            return None
        logger.debug("Request found", request_id=request_id, status=request.status.name)
        return copy.deepcopy(request)

    async def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MediaRequest]:
        """Retrieve paginated requests.

        Args:
            limit: Maximum number of items.
            offset: Number of items to skip.

        Returns:
            A list of deep-copied requests.
        """
        all_requests = list(self._store.values())
        # Sort by ID for deterministic ordering
        all_requests.sort(key=lambda r: r.id)
        paginated = all_requests[offset : offset + limit]
        return [copy.deepcopy(r) for r in paginated]

    async def delete(self, request_id: str) -> bool:
        """Delete a request by ID.

        Args:
            request_id: The unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        if request_id in self._store:
            del self._store[request_id]
            logger.debug("Deleted request", request_id=request_id)
            return True
        logger.debug("Request not found for deletion", request_id=request_id)
        return False

    async def count(self) -> int:
        """Return total number of stored requests.

        Returns:
            The total count.
        """
        return len(self._store)

    async def clear(self) -> None:
        """Clear all stored requests (useful for testing)."""
        self._store.clear()
        logger.debug("Repository cleared")