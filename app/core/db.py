from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from app.core.config import settings


# Supabase Client
def get_supabase_client() -> Client:
    """Get a new Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# CRUD operations
class SupabaseCRUD:
    """CRUD operations for Supabase."""

    def __init__(self, client: Client):
        self.client = client

    def create(self, table: str, data: dict) -> Dict[str, Any]:
        """Create a new record in the specified table."""
        result = self.client.table(table).insert(data).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return {}

    def read(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Get a record by its ID."""
        result = self.client.table(table).select("*").eq("id", id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    def update(self, table: str, id: int, data: dict) -> Optional[Dict[str, Any]]:
        """Update a record by its ID."""
        result = self.client.table(table).update(data).eq("id", id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    def delete(self, table: str, id: int) -> bool:
        """Delete a record by its ID."""
        result = self.client.table(table).delete().eq("id", id).execute()
        return len(result.data) > 0

    def read_all(
        self, table: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all records from the specified table with pagination."""
        return (
            self.client.table(table)
            .select("*")
            .range(offset, offset + limit - 1)
            .execute()
            .data
        )

    def read_filtered(
        self, table: str, column: str, value: any
    ) -> List[Dict[str, Any]]:
        """Get records filtered by a column value."""
        return self.client.table(table).select("*").eq(column, value).execute().data

    def read_by_name(self, table: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a record by its name column."""
        result = self.client.table(table).select("*").eq("name", name).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    def get_related(
        self, table: str, id: int, related_table: str, foreign_key: str
    ) -> List[Dict[str, Any]]:
        """Get related records from another table."""
        return (
            self.client.table(related_table)
            .select("*")
            .eq(foreign_key, id)
            .execute()
            .data
        )
