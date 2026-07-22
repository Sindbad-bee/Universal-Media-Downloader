"""Vercel serverless function entry point.

This is a simplified version of the app specifically for Vercel deployment.
Vercel serverless functions have limitations, so we create a minimal app here.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create a minimal FastAPI app for Vercel
app = FastAPI(
    title="Universal Media Downloader",
    version="1.0.0",
    description="Download videos and audio from various platforms",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple in-memory storage for serverless
class ServerlessStorage:
    """Simple storage for serverless environment."""
    
    def __init__(self):
        self.downloads = {}
        self.counter = 0
    
    def create(self, data):
        self.counter += 1
        self.downloads[self.counter] = data
        return self.counter
    
    def get(self, id):
        return self.downloads.get(id)
    
    def list_all(self):
        return list(self.downloads.values())


storage = ServerlessStorage()


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Universal Media Downloader is running"}


# Download endpoints
@app.post("/api/v1/downloads")
async def create_download(request: dict):
    """Create a new download request."""
    try:
        url = request.get("url")
        format_type = request.get("format", "video")
        
        if not url:
            return JSONResponse(
                status_code=400,
                content={"error": "URL is required"}
            )
        
        # Create download record
        download_id = storage.create({
            "url": url,
            "format": format_type,
            "status": "pending",
            "progress": 0,
        })
        
        return {
            "id": download_id,
            "url": url,
            "format": format_type,
            "status": "pending",
            "message": "Download request created (Note: Actual download requires server with yt-dlp)"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/v1/downloads")
async def list_downloads():
    """List all downloads."""
    return {"downloads": storage.list_all()}


@app.get("/api/v1/downloads/{download_id}")
async def get_download(download_id: int):
    """Get download status."""
    download = storage.get(download_id)
    if not download:
        return JSONResponse(
            status_code=404,
            content={"error": "Download not found"}
        )
    return download


@app.get("/")
async def root():
    """Root endpoint - serve info."""
    return {
        "name": "Universal Media Downloader",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "note": "This is a demo deployment. Full functionality requires a server with yt-dlp and ffmpeg installed."
    }


# For Vercel
__all__ = ["app"]