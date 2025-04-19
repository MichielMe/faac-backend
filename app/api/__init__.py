from .keyword import router as keyword_router
from .pictogram import router as pictogram_router
from .voice import router as voice_router

__all__ = [
    "pictogram_router",
    "keyword_router",
    "voice_router",
]
