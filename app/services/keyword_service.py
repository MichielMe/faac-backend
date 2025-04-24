from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models import Keyword
from app.schemas import KeywordCreate, KeywordUpdate
from app.services.base_service import SupabaseService


class KeywordService(SupabaseService):
    def __init__(self):
        super().__init__(table_name="keywords", model_class=Keyword)

    def _ensure_audio_loaded(self, keyword: Optional[Keyword]) -> Optional[Keyword]:
        """Helper method to ensure the audio relationship is loaded for a keyword."""
        if not keyword or not keyword.audio_id:
            return keyword

        # Get audio data from Supabase
        audio_data = self.supabase_crud.read("audio_files", keyword.audio_id)

        # Return keyword with audio data as a separate property
        # We can't set keyword.audio directly in SQLModel due to how it handles relationships
        if keyword:
            # Create a dictionary representation of the keyword
            keyword_dict = keyword.model_dump()

            # Add audio data to the dictionary
            if audio_data:
                keyword_dict["audio"] = audio_data
            else:
                keyword_dict["audio"] = None

            # Convert back to a Keyword model
            return Keyword.model_validate(keyword_dict)

        return keyword

    def create(self, keyword: KeywordCreate) -> Optional[Keyword]:
        """Create a new keyword in Supabase."""
        # Convert pydantic model to dict
        keyword_data = keyword.model_dump()

        # Add timestamp fields
        now = datetime.now().isoformat()
        keyword_data["created_at"] = now
        keyword_data["updated_at"] = now

        # Create in Supabase
        result = super().create(keyword_data)
        return result

    def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Get a keyword by its ID from Supabase."""
        keyword = super().get_by_id(keyword_id)
        return self._ensure_audio_loaded(keyword)

    def get_by_name(self, name: str) -> Optional[Keyword]:
        """Get a keyword by its name from Supabase."""
        keyword = super().get_by_name(name)
        return self._ensure_audio_loaded(keyword)

    def get_keyword_with_audio_urls(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a keyword by name with audio URLs.
        Returns a dictionary formatted for the KeywordAudioResponse schema.
        """
        # Get the keyword with basic info
        keyword = self.get_by_name(name)
        if not keyword:
            return None

        # Prepare the base response
        response = {
            "id": keyword.id,
            "name": keyword.name,
            "language": keyword.language,
            "pictogram_url": keyword.pictogram_url,
            "audio_id": keyword.audio_id,
            "voice_man_url": None,
            "voice_woman_url": None,
        }

        # If we have an audio_id, fetch the audio record to get URLs
        if keyword.audio_id:
            audio_data = self.supabase_crud.read("audio_files", keyword.audio_id)
            if audio_data:
                response["voice_man_url"] = audio_data.get("voice_man")
                response["voice_woman_url"] = audio_data.get("voice_woman")

        return response

    def list(self, skip: int = 0, limit: int = 100) -> List[Keyword]:
        """Get a list of keywords with pagination from Supabase."""
        return super().list(limit=limit, offset=skip)

    def update(
        self, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Optional[Keyword]:
        """Update a keyword by its ID in Supabase."""
        # Get current keyword
        keyword = self.get_by_id(keyword_id)
        if not keyword:
            return None

        # Convert update model to dict, filtering out None values
        update_data = {
            k: v for k, v in keyword_update.model_dump().items() if v is not None
        }

        # Add updated timestamp
        update_data["updated_at"] = datetime.now().isoformat()

        # Update in Supabase
        updated_keyword = super().update(keyword_id, update_data)
        return self._ensure_audio_loaded(updated_keyword)

    def delete(self, keyword_id: int) -> bool:
        """Delete a keyword by its ID from Supabase."""
        return super().delete(keyword_id)
