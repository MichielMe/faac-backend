from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.DEBUG,  # Log SQL queries when debugging
)


async def create_db_and_tables():
    """Create database tables from SQLModel models."""
    # Import all models here to ensure they're registered with SQLModel
    from app.models import Audio, Keyword  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a new database session."""
    with Session(engine) as session:
        yield session
