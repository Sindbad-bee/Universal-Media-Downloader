"""Global error handler middleware for FastAPI.

Catches all AppError exceptions and returns structured JSON error
responses with appropriate HTTP status codes.
"""

from __future__ import annotations

from typing import Callable, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.errors.app_errors import AppError
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware that catches AppError exceptions and returns
    standardized JSON error responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> JSONResponse:
        """Process the request, catching any AppError.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            A JSON response (error or normal).
        """
        try:
            response = await call_next(request)
            return response
        except AppError as exc:
            logger.error(
                "Application error",
                error_code=exc.code,
                error_message=exc.message,
                status_code=exc.status_code,
                path=str(request.url),
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
            )
        except Exception as exc:
            logger.exception(
                "Unhandled exception",
                error=str(exc),
                path=str(request.url),
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected internal error occurred.",
                        "details": {},
                    }
                },
            )


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(ErrorHandlerMiddleware)