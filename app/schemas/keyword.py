from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from .audio import AudioRead


class KeywordBase(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "en"
    pictogram_url: Optional[str] = None


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    pictogram_url: Optional[str] = None
    audio_id: Optional[int] = None


class KeywordRead(KeywordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    audio_id: Optional[int] = None

    model_config = {"from_attributes": True}


class KeywordReadDetailed(KeywordRead):
    audio: Optional[AudioRead] = Field(default=None)

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "extra": "ignore",
    }

    @model_validator(mode="before")
    @classmethod
    def validate_audio(cls, data: Any) -> Any:
        """Pre-validate audio data to handle different formats."""
        if isinstance(data, dict):
            # Handle case when data comes as a dictionary (e.g., from Supabase)
            audio_data = data.get("audio")

            # If audio is directly a dictionary, it can be used as is
            if audio_data and isinstance(audio_data, dict):
                # Ensure it has required fields for AudioRead
                if "id" not in audio_data and "keyword_id" not in audio_data:
                    data["audio"] = None
            elif audio_data is not None and not isinstance(audio_data, dict):
                # Set to None if not a valid dictionary
                data["audio"] = None

        return data
