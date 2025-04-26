from typing import Optional

from pydantic import BaseModel


class KeywordAudioResponse(BaseModel):
    """Custom response schema for keywords with audio URLs."""

    # Basic keyword fields
    id: int
    name: str
    language: str
    pictogram_url: Optional[str] = None

    # Audio information
    audio_id: Optional[int] = None
    voice_man_url: Optional[str] = None
    voice_woman_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 7,
                "name": "TV",
                "language": "en",
                "pictogram_url": "https://faac.fra1.cdn.digitaloceanspaces.com/pictograms/pic_TV_final.png",
                "audio_id": 4,
                "voice_man_url": "https://faac.fra1.cdn.digitaloceanspaces.com/voice_clips/TV_man.mp3",
                "voice_woman_url": "https://faac.fra1.cdn.digitaloceanspaces.com/voice_clips/TV_woman.mp3",
            }
        }
