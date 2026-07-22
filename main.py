"""Main entry point for running the application."""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    import uvicorn
    from src.presentation.app import app
    
    uvicorn.run(
        "src.presentation.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )