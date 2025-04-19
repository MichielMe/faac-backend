from datetime import datetime
from typing import Optional

from pydantic import BaseModel

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
    audio: Optional[AudioRead] = None

    model_config = {"from_attributes": True}
