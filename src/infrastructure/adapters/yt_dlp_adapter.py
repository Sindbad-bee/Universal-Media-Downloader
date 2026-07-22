"""Adapter for yt-dlp CLI tool integration.

This adapter implements the DownloaderService interface by wrapping
the yt-dlp command-line tool via asyncio subprocess.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.domain.entities.media_request import (
    MediaRequest,
    MediaType,
    VideoQuality,
)
from src.domain.interfaces.downloader_service import DownloaderService
from src.infrastructure.errors.app_errors import DownloaderAdapterError
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class YtDlpAdapter(DownloaderService):
    """Adapter that delegates media downloads to the yt-dlp CLI.

    This adapter communicates with yt-dlp via subprocess, parsing its
    JSON output for metadata and progress tracking.
    """

    def __init__(
        self,
        yt_dlp_path: Optional[str] = None,
        ffmpeg_path: Optional[str] = None,
        default_output_dir: Optional[Path] = None,
        request_timeout: int = 600,
    ) -> None:
        self._yt_dlp_path = yt_dlp_path or self._find_executable("yt-dlp")
        self._ffmpeg_path = ffmpeg_path or self._find_executable("ffmpeg")
        self._default_output_dir = default_output_dir or Path.cwd() / "downloads"
        self._request_timeout = request_timeout
        self._active_processes: Dict[str, asyncio.subprocess.Process] = {}

        # Ensure output directory exists
        self._default_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "YtDlpAdapter initialized",
            yt_dlp_path=self._yt_dlp_path,
            ffmpeg_path=self._ffmpeg_path,
            output_dir=str(self._default_output_dir),
        )

    @staticmethod
    def _find_executable(name: str) -> str:
        """Locate an executable in the system PATH.

        Args:
            name: The executable name (e.g., 'yt-dlp', 'ffmpeg').

        Returns:
            The full path to the executable.

        Raises:
            DownloaderAdapterError: If the executable is not found.
        """
        path = shutil.which(name)
        if path is None:
            raise DownloaderAdapterError(
                f"Executable '{name}' not found in system PATH. "
                f"Please install it and ensure it is available.",
                command=name,
            )
        return path

    async def fetch_metadata(self, url: str) -> dict:
        """Retrieve metadata for a media URL using yt-dlp --dump-json.

        Args:
            url: The media URL to inspect.

        Returns:
            Dictionary containing parsed metadata from yt-dlp.

        Raises:
            DownloaderAdapterError: If metadata retrieval fails.
        """
        cmd = [
            self._yt_dlp_path,
            "--dump-json",
            "--no-download",
            "--no-warnings",
            url,
        ]

        logger.debug("Fetching metadata", url=url, command=" ".join(cmd))

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=30,
                )
            except asyncio.TimeoutError:
                proc.kill()
                raise DownloaderAdapterError(
                    "Metadata fetch timed out after 30 seconds",
                    command=" ".join(cmd),
                )

            if proc.returncode != 0:
                error_text = stderr.decode("utf-8", errors="replace").strip()
                raise DownloaderAdapterError(
                    f"yt-dlp metadata fetch failed: {error_text}",
                    command=" ".join(cmd),
                    exit_code=proc.returncode,
                )

            output = stdout.decode("utf-8", errors="replace").strip()
            if not output:
                raise DownloaderAdapterError(
                    "yt-dlp returned empty metadata output",
                    command=" ".join(cmd),
                )

            # yt-dlp outputs one JSON line per video (playlists have multiple)
            metadata = json.loads(output.splitlines()[0])
            logger.info("Metadata fetched successfully", url=url, title=metadata.get("title"))
            return metadata

        except DownloaderAdapterError:
            raise
        except Exception as exc:
            raise DownloaderAdapterError(
                f"Unexpected error fetching metadata: {str(exc)}",
                command=" ".join(cmd),
            ) from exc

    async def download(self, request: MediaRequest) -> str:
        """Execute a media download using yt-dlp.

        Args:
            request: The MediaRequest entity specifying download parameters.

        Returns:
            The absolute path to the downloaded file.

        Raises:
            DownloaderAdapterError: If the download fails.
        """
        output_dir = request.output_directory or str(self._default_output_dir)
        output_template = request.filename_template or "%(title)s.%(ext)s"
        output_path = os.path.join(output_dir, output_template)

        cmd = self._build_command(request, output_path)

        logger.info(
            "Starting download",
            request_id=request.id,
            url=request.url,
            command=" ".join(cmd),
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self._active_processes[request.id] = proc

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self._request_timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                raise DownloaderAdapterError(
                    f"Download timed out after {self._request_timeout} seconds",
                    command=" ".join(cmd),
                    request_id=request.id,
                )

            if proc.returncode != 0:
                error_text = stderr.decode("utf-8", errors="replace").strip()
                raise DownloaderAdapterError(
                    f"yt-dlp download failed: {error_text}",
                    command=" ".join(cmd),
                    exit_code=proc.returncode,
                    details={"request_id": request.id},
                )

            # Parse the final output file path from yt-dlp stdout
            std_output = stdout.decode("utf-8", errors="replace").strip()
            logger.info(
                "Download completed successfully",
                request_id=request.id,
                output=std_output,
            )

            # Find the actual output file
            actual_path = self._find_output_file(output_dir, request)
            return actual_path

        except DownloaderAdapterError:
            raise
        except Exception as exc:
            raise DownloaderAdapterError(
                f"Unexpected error during download: {str(exc)}",
                command=" ".join(cmd),
                details={"request_id": request.id},
            ) from exc
        finally:
            self._active_processes.pop(request.id, None)

    async def cancel_download(self, request_id: str) -> bool:
        """Cancel an in-progress download.

        Args:
            request_id: The ID of the download to cancel.

        Returns:
            True if the process was found and terminated.
        """
        proc = self._active_processes.get(request_id)
        if proc is None:
            logger.warning("No active process found for cancellation", request_id=request_id)
            return False

        try:
            proc.terminate()
            await asyncio.sleep(0.5)
            if proc.returncode is None:
                proc.kill()
            logger.info("Download cancelled", request_id=request_id)
            return True
        except ProcessLookupError:
            # Process already finished
            return True
        except Exception as exc:
            logger.error("Failed to cancel download", request_id=request_id, error=str(exc))
            return False

    async def validate_url(self, url: str) -> bool:
        """Check if a URL is supported by yt-dlp.

        Args:
            url: The URL to validate.

        Returns:
            True if the URL is supported, False otherwise.
        """
        try:
            metadata = await self.fetch_metadata(url)
            return bool(metadata and metadata.get("extractor"))
        except DownloaderAdapterError:
            return False
        except Exception:
            return False

    def _build_command(self, request: MediaRequest, output_path: str) -> List[str]:
        """Construct the yt-dlp command arguments based on the request.

        Args:
            request: The media download request.
            output_path: The output file path template.

        Returns:
            A list of command-line arguments.
        """
        cmd = [
            self._yt_dlp_path,
            "--no-warnings",
            "--print", "after_move:filepath",
            "-o", output_path,
        ]

        # Configure output format based on media type
        if request.media_type == MediaType.AUDIO:
            cmd.extend([
                "-x",  # Extract audio
                "--audio-format", request.audio_format.value,
                "--audio-quality", "0",  # Best quality
            ])
        elif request.media_type == MediaType.VIDEO:
            quality = request.video_quality.value
            if quality == "best":
                cmd.extend(["-f", "bestvideo[ext=mp4]/bestvideo"])
            elif quality == "worst":
                cmd.extend(["-f", "worstvideo[ext=mp4]/worstvideo"])
            else:
                height = quality.rstrip("p")
                cmd.extend([
                    "-f", f"bestvideo[height<={height}][ext=mp4]/bestvideo[height<={height}]",
                ])
        else:
            # VIDEO_WITH_AUDIO - merge best video + best audio
            quality = request.video_quality.value
            if quality == "best":
                cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
            elif quality == "worst":
                cmd.extend([
                    "-f",
                    "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst",
                ])
            else:
                height = quality.rstrip("p")
                cmd.extend([
                    "-f",
                    f"bestvideo[height<={height}][ext=mp4]+"
                    f"bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]",
                ])

        # Use ffmpeg for post-processing if available
        if self._ffmpeg_path:
            cmd.extend(["--ffmpeg-location", self._ffmpeg_path])

        # Add the URL
        cmd.append(request.url)

        return cmd

    @staticmethod
    def _find_output_file(output_dir: str, request: MediaRequest) -> str:
        """Locate the downloaded file in the output directory.

        This is a best-effort search since yt-dlp's actual filename
        depends on the template and available metadata.

        Args:
            output_dir: The directory where files were downloaded.
            request: The original download request.

        Returns:
            The absolute path to the downloaded file.
        """
        dir_path = Path(output_dir)
        if not dir_path.exists():
            return os.path.join(output_dir, "unknown")

        # List files sorted by modification time, newest first
        files = sorted(dir_path.iterdir(), key=os.path.getmtime, reverse=True)
        if files:
            return str(files[0])

        return os.path.join(output_dir, "unknown")