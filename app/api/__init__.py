"""
API routes for the FAAC backend application.

This module exports the FastAPI routers for different parts of the application.
Each router is responsible for a specific aspect of functionality.
"""

from .keyword import router as keyword_router
from .pictogram import router as pictogram_router
from .voice import router as voice_router

__all__ = [
    "keyword_router",  # Routes for keyword CRUD operations
    "pictogram_router",  # Routes for pictogram generation
    "voice_router",  # Routes for voice generation
]
