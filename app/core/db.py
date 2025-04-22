import json

from sqlmodel import Session, SQLModel, create_engine
from supabase import Client, create_client

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
        yield session


# Supabase Client
def get_supabase_client():
    """Get a new Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# CRUD operations
class SupabaseCRUD:
    """CRUD operations for Supabase."""

    def __init__(self, client: Client):
        self.client = client

    def create(self, table: str, data: json):
        return self.client.table(table).insert(data).execute()

    def read(self, table: str, id: int):
        return self.client.table(table).select("*").eq("id", id).execute().data[0]

    def update(self, table: str, id: int, data: json):
        return self.client.table(table).update(data).eq("id", id).execute()

    def delete(self, table: str, id: int):
        return self.client.table(table).delete().eq("id", id).execute()

    def read_all(self, table: str):
        return self.client.table(table).select("*").execute().data

    def read_filtered(self, table: str, filters: dict):
        return self.client.table(table).select("*").eq(filters).execute().data
