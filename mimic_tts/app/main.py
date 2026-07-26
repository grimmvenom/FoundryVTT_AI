"""
Mimic-TTS application entry point.

The FastAPI application is defined in:
    app.api.main
"""

from app.api.main import app


__all__ = [
    "app",
]