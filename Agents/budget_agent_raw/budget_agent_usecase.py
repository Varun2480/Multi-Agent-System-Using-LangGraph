# --- Top-level functions for handling operations ---

from typing import Any, Dict, List
from pydantic import ValidationError
from sqlalchemy.orm import Session
from db_context import DatabaseCRUD
from schemas import TableNameEnum
from settings import LOGGER

class BudgetAgentUsecase:
    """
    This class encapsulates the business logic for budget-related operations.
    It orchestrates interactions with the database CRUD operations.
    """
    def __init__(self, db: Session):
        """
        Initializes the use case with a database session.

        Args:
            db (Session): The SQLAlchemy Session object.
        """
        self.crud = DatabaseCRUD(db)

    def handle_create_tables(self) -> Dict[str, str]:
        """Handles the 'create_tables' operation."""
        self.crud.create_all_tables()
        return {"message": "All tables checked/created successfully."}

    def handle_add_item(self, table: TableNameEnum, payload: Dict[str, Any]) -> Any:
        """Handles the 'add' operation."""
        PydanticResponseModel = self.crud.get_pydantic_model(table, "response")

        if payload is None:
            LOGGER.error("Payload missing for 'add' operation.")
            raise ValueError("Payload is required for add operation.")
        
        try:
            created_item_dict = self.crud.add_item(table, payload)
            return PydanticResponseModel(**created_item_dict)
        except ValidationError as e:
            LOGGER.error(f"Pydantic validation error for add operation: {e.errors()}", exc_info=True)
            raise ValueError(f"Validation error: {e.errors()}")
        except Exception as e:
            LOGGER.error(f"An unexpected error occurred during add operation: {e}", exc_info=True)
            raise RuntimeError(f"Failed to add item: {e}")

    def handle_get_one_item(self, table: TableNameEnum, payload: Dict[str, Any]) -> Any:
        """Handles the 'get_one' operation."""
        PydanticResponseModel = self.crud.get_pydantic_model(table, "response")

        if payload is None or "id" not in payload:
            LOGGER.error("Payload with 'id' missing for 'get_one' operation.")
            raise ValueError("Payload with 'id' is required for get_one operation.")
        
        item_id = payload["id"]
        db_item_dict = self.crud.get_item_by_id(table, item_id)
        if db_item_dict is None:
            LOGGER.warning(f"Item not found for 'get_one': table='{table.value}', id='{item_id}'.")
            raise ValueError(f"{table.value} item not found")
        return PydanticResponseModel(**db_item_dict)

    def handle_get_all_items(self, table: TableNameEnum) -> List[Any]:
        """Handles the 'get_all' operation."""
        PydanticResponseModel = self.crud.get_pydantic_model(table, "response")
        items_list = self.crud.get_all_items(table)
        return [PydanticResponseModel(**item_dict) for item_dict in items_list]

    def handle_update_item(self, table: TableNameEnum, payload: Dict[str, Any]) -> Any:
        """Handles the 'update' operation."""
        PydanticResponseModel = self.crud.get_pydantic_model(table, "response")

        if payload is None or "id" not in payload or "update_data" not in payload:
            LOGGER.error("Payload with 'id' and 'update_data' missing for 'update' operation.")
            raise ValueError("Payload with 'id' and 'update_data' is required for update operation.")
        
        item_id = payload["id"]
        update_data = payload["update_data"]
        
        try:
            updated_item_dict = self.crud.update_item(table, item_id, update_data)
            if updated_item_dict is None:
                LOGGER.warning(f"Item not found or no changes made for 'update': table='{table.value}', id='{item_id}'.")
                raise ValueError(f"{table.value} item not found or no changes made")
            return PydanticResponseModel(**updated_item_dict)
        except ValidationError as e:
            LOGGER.error(f"Pydantic validation error for update operation: {e.errors()}", exc_info=True)
            raise ValueError(f"Validation error: {e.errors()}")
        except Exception as e:
            LOGGER.error(f"An unexpected error occurred during update operation: {e}", exc_info=True)
            raise RuntimeError(f"Failed to update item: {e}")

    def handle_delete_item(self, table: TableNameEnum, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handles the 'delete' operation."""
        if payload is None or "id" not in payload:
            LOGGER.error("Payload with 'id' missing for 'delete' operation.")
            raise ValueError("Payload with 'id' is required for delete operation.")
        
        item_id = payload["id"]
        if not self.crud.delete_item(table, item_id):
            LOGGER.warning(f"Item not found for 'delete': table='{table.value}', id='{item_id}'.")
            raise ValueError(f"{table.value} item not found")
        return {"message": f"{table.value} item deleted successfully", "id": item_id}
