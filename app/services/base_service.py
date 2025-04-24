from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlmodel import SQLModel

from app.core import SupabaseCRUD, get_supabase_client

T = TypeVar("T", bound=SQLModel)


class SupabaseService:
    """Base service class for Supabase operations."""

    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class
        self.supabase_client = get_supabase_client()
        self.supabase_crud = SupabaseCRUD(self.supabase_client)

    def _convert_to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """Convert dictionary data to a model instance."""
        if not data:
            return None
        return self.model_class.model_validate(data)

    def _convert_list_to_models(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Convert a list of dictionaries to model instances."""
        return [self._convert_to_model(item) for item in data_list if item]

    def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create a new record."""
        result = self.supabase_crud.create(self.table_name, data)
        return self._convert_to_model(result)

    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by its ID."""
        result = self.supabase_crud.read(self.table_name, id)
        return self._convert_to_model(result)

    def get_by_name(self, name: str) -> Optional[T]:
        """Get a record by its name."""
        result = self.supabase_crud.read_by_name(self.table_name, name)
        return self._convert_to_model(result)

    def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get a list of records with pagination."""
        results = self.supabase_crud.read_all(
            self.table_name, limit=limit, offset=offset
        )
        return self._convert_list_to_models(results)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by its ID."""
        result = self.supabase_crud.update(self.table_name, id, data)
        return self._convert_to_model(result)

    def delete(self, id: int) -> bool:
        """Delete a record by its ID."""
        return self.supabase_crud.delete(self.table_name, id)

    def get_by_field(self, field: str, value: Any) -> List[T]:
        """Get records filtered by a field value."""
        results = self.supabase_crud.read_filtered(self.table_name, field, value)
        return self._convert_list_to_models(results)

    def get_related(
        self,
        id: int,
        related_table: str,
        foreign_key: str,
        related_model_class: Type[SQLModel],
    ) -> List[Any]:
        """Get related records from another table."""
        results = self.supabase_crud.get_related(
            self.table_name, id, related_table, foreign_key
        )
        if not related_model_class:
            return results
        return [related_model_class.model_validate(item) for item in results if item]
