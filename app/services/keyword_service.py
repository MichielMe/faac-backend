from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.models import Keyword
from app.schemas import KeywordCreate, KeywordUpdate


class KeywordService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, keyword: KeywordCreate) -> Keyword:
        """Create a new keyword in the database."""
        db_keyword = Keyword.model_validate(keyword.model_dump())
        self.db.add(db_keyword)
        self.db.commit()
        self.db.refresh(db_keyword)
        return db_keyword

    def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Get a keyword by its ID."""
        return self.db.get(Keyword, keyword_id)

    def get_by_name(self, name: str) -> Optional[Keyword]:
        """Get a keyword by its name."""
        statement = select(Keyword).where(Keyword.name == name)
        return self.db.exec(statement).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Keyword]:
        """Get a list of keywords with pagination."""
        statement = select(Keyword).offset(skip).limit(limit)
        return self.db.exec(statement).all()

    def update(
        self, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Optional[Keyword]:
        """Update a keyword by its ID."""
        db_keyword = self.get_by_id(keyword_id)
        if not db_keyword:
            return None

        # Filter out None values to avoid overwriting with None
        update_data = {
            k: v for k, v in keyword_update.model_dump().items() if v is not None
        }

        for key, value in update_data.items():
            setattr(db_keyword, key, value)

        # Update the updated_at timestamp
        db_keyword.updated_at = datetime.now()

        self.db.add(db_keyword)
        self.db.commit()
        self.db.refresh(db_keyword)
        return db_keyword

    def delete(self, keyword_id: int) -> bool:
        """Delete a keyword by its ID."""
        db_keyword = self.get_by_id(keyword_id)
        if not db_keyword:
            return False

        self.db.delete(db_keyword)
        self.db.commit()
        return True
