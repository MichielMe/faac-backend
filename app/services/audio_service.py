from datetime import datetime
from typing import List, Optional

from app.models import Audio
from app.schemas import AudioCreate, AudioUpdate
from app.services.base_service import SupabaseService


class AudioService(SupabaseService):
    def __init__(self):
        super().__init__(table_name="audio_files", model_class=Audio)

    def create(self, audio: AudioCreate) -> Optional[Audio]:
        """Create a new audio record in Supabase."""
        # Convert pydantic model to dict
        audio_data = audio.model_dump()

        # Add timestamp field
        audio_data["created_at"] = datetime.now().isoformat()

        # Create in Supabase
        return super().create(audio_data)

    def get_by_id(self, audio_id: int) -> Optional[Audio]:
        """Get an audio record by its ID from Supabase."""
        return super().get_by_id(audio_id)

    def list(self, skip: int = 0, limit: int = 100) -> List[Audio]:
        """Get a list of audio records with pagination from Supabase."""
        return super().list(limit=limit, offset=skip)

    def get_by_keyword_id(self, keyword_id: int) -> List[Audio]:
        """Get all audio records for a specific keyword from Supabase."""
        return self.get_by_field("keyword_id", keyword_id)

    def get_by_language_id(self, language_id: int) -> List[Audio]:
        """Get all audio records for a specific language from Supabase."""
        return self.get_by_field("language_id", language_id)

    def get_by_audio_type_id(self, audio_type_id: int) -> List[Audio]:
        """Get all audio records for a specific audio type from Supabase."""
        return self.get_by_field("audio_type_id", audio_type_id)

    def get_by_keyword_and_language(
        self, keyword_id: int, language_id: int
    ) -> List[Audio]:
        """Get all audio records for a specific keyword and language from Supabase."""
        # This requires a more complex query that filters on two conditions
        # We'll use the raw Supabase client for this
        result = (
            self.supabase_client.table("audio_files")
            .select("*")
            .eq("keyword_id", keyword_id)
            .eq("language_id", language_id)
            .execute()
        )

        return self._convert_list_to_models(result.data)

    def update(self, audio_id: int, audio_update: AudioUpdate) -> Optional[Audio]:
        """Update an audio record by its ID in Supabase."""
        # Filter out None values to avoid overwriting with None
        update_data = {
            k: v for k, v in audio_update.model_dump().items() if v is not None
        }

        # Update in Supabase
        return super().update(audio_id, update_data)

    def delete(self, audio_id: int) -> bool:
        """Delete an audio record by its ID from Supabase."""
        return super().delete(audio_id)
