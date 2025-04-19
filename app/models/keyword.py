from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class KeywordBase(SQLModel):
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    pictogram_url: Optional[str] = None
    language: str = Field(default="en")


class Keyword(KeywordBase, table=True):
    __tablename__ = "keywords"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    audio_id: Optional[int] = Field(default=None, foreign_key="audio_files.id")

    def __repr__(self):
        return (
            f"<Keyword(id={self.id}, name='{self.name}', language='{self.language}')>"
        )


class Audio(SQLModel, table=True):
    __tablename__ = "audio_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    voice_man: Optional[str] = None
    voice_woman: Optional[str] = None
    keyword_id: int = Field(foreign_key="keywords.id")
    created_at: datetime = Field(default_factory=datetime.now)

    def __repr__(self):
        return f"<Audio(id={self.id}, keyword_id={self.keyword_id})>"


# Add relationships after both classes are defined
Keyword.audio = Relationship(back_populates="keyword")
Audio.keyword = Relationship(back_populates="audio")
