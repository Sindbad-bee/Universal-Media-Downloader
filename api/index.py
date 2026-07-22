"""Vercel serverless function entry point - Minimal version."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create minimal FastAPI app
app = FastAPI(title="Universal Media Downloader")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
downloads = {}
counter = [0]

@app.get("/")
async def root():
    return {"status": "ok", "message": "Universal Media Downloader API"}

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/downloads")
async def create_download(request: dict):
    url = request.get("url")
    if not url:
        return JSONResponse(status_code=400, content={"error": "URL required"})
    counter[0] += 1
    downloads[counter[0]] = {"url": url, "status": "pending"}
    return {"id": counter[0], "status": "pending"}

@app.get("/api/v1/downloads")
async def list_downloads():
    return {"downloads": list(downloads.values())}

@app.get("/api/v1/downloads/{download_id}")
async def get_download(download_id: int):
    if download_id not in downloads:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    return downloads[download_id]

__all__ = ["app"]
