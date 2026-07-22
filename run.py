"""Application entry point for development."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Now import and run the app
from src.presentation.app import app

__all__ = ["app"]