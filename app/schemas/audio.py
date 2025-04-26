from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AudioBase(BaseModel):
    voice_man: Optional[str] = None
    voice_woman: Optional[str] = None
    keyword_id: int


class AudioCreate(AudioBase):
    pass


class AudioUpdate(BaseModel):
    voice_man: Optional[str] = None
    voice_woman: Optional[str] = None
    keyword_id: Optional[int] = None


class AudioRead(AudioBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
