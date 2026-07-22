"""Centralized application error hierarchy.

All custom exceptions inherit from AppError, providing a consistent
error structure across all layers of the application.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base exception for all application-level errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize error to a dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ConfigurationError(AppError):
    """Raised when application configuration is invalid or missing."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )


class ValidationError(AppError):
    """Raised when input data fails validation."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ResourceNotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> None:
        details: Dict[str, Any] = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details,
        )


class ExternalServiceError(AppError):
    """Raised when an external service (yt-dlp, ffmpeg) fails."""

    def __init__(
        self,
        message: str,
        service_name: str = "external_service",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status_code,
            details={
                "service": service_name,
                **(details or {}),
            },
        )


class DownloaderAdapterError(ExternalServiceError):
    """Raised when the yt-dlp adapter encounters an error."""

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            service_name="yt-dlp",
            status_code=502,
            details={
                "command": command,
                "exit_code": exit_code,
                **(details or {}),
            },
        )


class DownloadExecutionError(AppError):
    """Raised when a download operation fails during execution."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="DOWNLOAD_EXECUTION_ERROR",
            status_code=500,
            details={
                "request_id": request_id,
                **(details or {}),
            },
        )


class FileSystemError(AppError):
    """Raised when file system operations (read/write/delete) fail."""

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="FILE_SYSTEM_ERROR",
            status_code=500,
            details={
                "path": path,
                "operation": operation,
                **(details or {}),
            },
        )


class RepositoryError(AppError):
    """Raised when a repository operation fails."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="REPOSITORY_ERROR",
            status_code=500,
            details={
                "operation": operation,
                **(details or {}),
            },
        )