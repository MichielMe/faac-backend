from typing import List, Optional

from sqlmodel import Session, select

from app.models import Audio
from app.schemas import AudioCreate, AudioUpdate


class AudioService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, audio: AudioCreate) -> Audio:
        """Create a new audio record in the database."""
        db_audio = Audio.model_validate(audio.model_dump())
        self.db.add(db_audio)
        self.db.commit()
        self.db.refresh(db_audio)
        return db_audio

    def get_by_id(self, audio_id: int) -> Optional[Audio]:
        """Get an audio record by its ID."""
        return self.db.get(Audio, audio_id)

    def list(self, skip: int = 0, limit: int = 100) -> List[Audio]:
        """Get a list of audio records with pagination."""
        statement = select(Audio).offset(skip).limit(limit)
        return self.db.exec(statement).all()

    def get_by_keyword_id(self, keyword_id: int) -> List[Audio]:
        """Get all audio records for a specific keyword."""
        statement = select(Audio).where(Audio.keyword_id == keyword_id)
        return self.db.exec(statement).all()

    def get_by_language_id(self, language_id: int) -> List[Audio]:
        """Get all audio records for a specific language."""
        statement = select(Audio).where(Audio.language_id == language_id)
        return self.db.exec(statement).all()

    def get_by_audio_type_id(self, audio_type_id: int) -> List[Audio]:
        """Get all audio records for a specific audio type."""
        statement = select(Audio).where(Audio.audio_type_id == audio_type_id)
        return self.db.exec(statement).all()

    def get_by_keyword_and_language(
        self, keyword_id: int, language_id: int
    ) -> List[Audio]:
        """Get all audio records for a specific keyword and language."""
        statement = select(Audio).where(
            Audio.keyword_id == keyword_id, Audio.language_id == language_id
        )
        return self.db.exec(statement).all()

    def update(self, audio_id: int, audio_update: AudioUpdate) -> Optional[Audio]:
        """Update an audio record by its ID."""
        db_audio = self.get_by_id(audio_id)
        if not db_audio:
            return None

        # Filter out None values to avoid overwriting with None
        update_data = {
            k: v for k, v in audio_update.model_dump().items() if v is not None
        }

        for key, value in update_data.items():
            setattr(db_audio, key, value)

        self.db.add(db_audio)
        self.db.commit()
        self.db.refresh(db_audio)
        return db_audio

    def delete(self, audio_id: int) -> bool:
        """Delete an audio record by its ID."""
        db_audio = self.get_by_id(audio_id)
        if not db_audio:
            return False

        self.db.delete(db_audio)
        self.db.commit()
        return True
