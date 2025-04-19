from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_session
from app.services.audio_service import AudioService
from app.services.keyword_content_generator import KeywordContentGenerator
from app.services.keyword_service import KeywordService


# Database dependency
def get_db():
    """Dependency for database session."""
    return next(get_session())


# Service dependencies
def get_keyword_service(db: Session = Depends(get_db)) -> KeywordService:
    """Dependency for KeywordService."""
    return KeywordService(db)


def get_audio_service(db: Session = Depends(get_db)) -> AudioService:
    """Dependency for AudioService."""
    return AudioService(db)


def get_keyword_content_generator(
    db: Session = Depends(get_db),
) -> KeywordContentGenerator:
    """Dependency for KeywordContentGenerator."""
    return KeywordContentGenerator(db=db)
