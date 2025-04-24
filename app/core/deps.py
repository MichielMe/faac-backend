
from app.services.audio_service import AudioService
from app.services.keyword_content_generator import KeywordContentGenerator
from app.services.keyword_service import KeywordService


# Service dependencies
def get_keyword_service() -> KeywordService:
    """Dependency for KeywordService."""
    return KeywordService()


def get_audio_service() -> AudioService:
    """Dependency for AudioService."""
    return AudioService()


def get_keyword_content_generator() -> KeywordContentGenerator:
    """Dependency for KeywordContentGenerator."""
    # Note: KeywordContentGenerator will need to be updated separately
    # to remove local database dependency
    return KeywordContentGenerator()
