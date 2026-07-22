"""Request logging middleware for FastAPI.

Logs incoming requests and outgoing responses with timing information.
"""

from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all HTTP requests with timing information."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Log the request, time it, and log the response.

        Args:
            request: Incoming HTTP request.
            call_next: Next handler in the chain.

        Returns:
            The HTTP response.
        """
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        query_params = str(request.url.query) if request.url.query else ""

        logger.info(
            "Incoming request",
            method=method,
            path=path,
            client=client_host,
            query=query_params,
        )

        try:
            response = await call_next(request)
            elapsed = time.time() - start_time

            logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                elapsed_ms=round(elapsed * 1000, 2),
            )

            return response

        except Exception as exc:
            elapsed = time.time() - start_time
            logger.exception(
                "Request failed",
                method=method,
                path=path,
                elapsed_ms=round(elapsed * 1000, 2),
                error=str(exc),
            )
            raise


def register_logging_middleware(app: "FastAPI") -> None:
    """Register the logging middleware on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(LoggingMiddleware)