import os
from typing import List, Optional, Any, Union, Dict
from pydantic import BaseModel, ValidationError, Field
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, Float, Date
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv
from schemas import (TableNameEnum, 
                      CategoryBudgetOverviewCreate, 
                      CategoryBudgetOverviewUpdate, 
                      CategoryBudgetOverview, 
                      TransactionDetailCreate, 
                      TransactionDetailUpdate, 
                      TransactionDetail)
from settings import LOGGER
load_dotenv()  # load environment variables from .env

# --- Database Configuration ---
NEW_DB_USER_NAME = os.getenv("NEW_DB_USER_NAME")
NEW_DB_PASSWORD = os.getenv("NEW_DB_PASSWORD")
NEW_DB_HOST = os.getenv("NEW_DB_HOST")
NEW_DB_PORT = os.getenv("NEW_DB_PORT")
NEW_DB_NAME = os.getenv("NEW_DB_NAME")

# Validate essential environment variables
if not all([NEW_DB_USER_NAME, NEW_DB_HOST, NEW_DB_NAME]):
    missing_vars = [
        var_name
        for var_name, var_value in {
            "NEW_DB_USER_NAME": NEW_DB_USER_NAME,
            "NEW_DB_HOST": NEW_DB_HOST,
            "NEW_DB_NAME": NEW_DB_NAME,
        }.items()
        if not var_value
    ]
    raise EnvironmentError(
        f"Missing critical database environment variables: {', '.join(missing_vars)}"
    )

# Replace with your actual PostgreSQL connection string
DATABASE_URL = f"postgresql://{NEW_DB_USER_NAME}:{NEW_DB_PASSWORD}@{NEW_DB_HOST}:{NEW_DB_PORT}/{NEW_DB_NAME}" # Removed echo=True for production
# Example for SQLite (for quick testing if needed, but features might differ):
# DATABASE_URL = "sqlite:///./budget_app.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()


# --- SQLAlchemy Table Definitions ---

category_budget_table = Table(
    "category_budget_overview",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("category", String, index=True, nullable=False),
    Column("budget_inr", Float, nullable=False),
    Column("total_spent_inr", Float, default=0.0),
    Column("remaining_budget_inr", Float), # Can be derived or stored
)
# {
#   "table": "category_budget_overview",
#   "query_type": "add",
#   "payload": {
#     "category": "shopping",
#     "budget_inr": 500,
#     "total_spent_inr": 200
#   }
# }

transaction_details_table = Table(
    "transaction_details",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("transaction_date", Date, nullable=False, index=True), # Changed from 'data'
    Column("category", String, index=True, nullable=False),
    Column("description", String, nullable=True),
    Column("amount_inr", Float, nullable=False),
    Column("type", String, nullable=False),  # E.g., 'income', 'expense'
    Column("location", String, nullable=True),
)

# {
#   "table": "transaction_details",
#   "query_type": "add",
#   "payload": {
#     "transaction_date": "2025-06-20",
#     "category": "shopping",
#     "description": "testing",
#     "amount_inr": 300,
#     "type": "expense",
#     "location": "hyd"
#   }
# }



# --- Database CRUD Class ---
class DatabaseCRUD:
    def __init__(self, db: Session):
        self.db = db
        self.table_map = {
            TableNameEnum.CATEGORY_BUDGET_OVERVIEW: category_budget_table,
            TableNameEnum.TRANSACTION_DETAILS: transaction_details_table,
        }
        self.pydantic_create_map = {
            TableNameEnum.CATEGORY_BUDGET_OVERVIEW: CategoryBudgetOverviewCreate,
            TableNameEnum.TRANSACTION_DETAILS: TransactionDetailCreate,
        }
        self.pydantic_update_map = {
            TableNameEnum.CATEGORY_BUDGET_OVERVIEW: CategoryBudgetOverviewUpdate,
            TableNameEnum.TRANSACTION_DETAILS: TransactionDetailUpdate,
        }
        self.pydantic_response_map = {
            TableNameEnum.CATEGORY_BUDGET_OVERVIEW: CategoryBudgetOverview,
            TableNameEnum.TRANSACTION_DETAILS: TransactionDetail,
        }

    def _get_sqla_table(self, table_name: TableNameEnum) -> Table:
        sqla_table = self.table_map.get(table_name)
        if sqla_table is None: # Check for None explicitly
            raise ValueError(f"Unknown table: {table_name.value}")
        return sqla_table

    def get_pydantic_model(self, table_name: TableNameEnum, model_type: str) -> BaseModel:
        model_map = {
            "create": self.pydantic_create_map,
            "update": self.pydantic_update_map,
            "response": self.pydantic_response_map,
        }
        selected_map = model_map.get(model_type)
        if selected_map is None:
            raise ValueError(f"Invalid model type: {model_type}")
        
        model = selected_map.get(table_name)
        if model is None: # Check for None explicitly
            raise ValueError(f"No Pydantic {model_type} model for table: {table_name.value}")
        return model
    
    def _update_category_budget(self, category_name: str, amount_change: float):
        """
        Helper function to update total_spent and remaining_budget for a category.
        'amount_change' is positive for an expense, negative for an income or reversal.
        """
        category_budget_s = self._get_sqla_table(TableNameEnum.CATEGORY_BUDGET_OVERVIEW)
        
        # Fetch the current budget and spent amount
        stmt = category_budget_s.select().where(category_budget_s.c.category == category_name)
        category_row = self.db.execute(stmt).fetchone()

        if category_row:
            new_total_spent = category_row.total_spent_inr + amount_change
            remaining_budget = category_row.budget_inr - new_total_spent
            update_stmt = category_budget_s.update().where(category_budget_s.c.category == category_name).values(total_spent_inr=new_total_spent, remaining_budget_inr=remaining_budget)
            self.db.execute(update_stmt)
            self.db.commit()

    def create_all_tables(self):
        """Creates all defined tables in the metadata."""
        metadata.create_all(bind=engine)
        LOGGER.info("Tables checked/created.")

    def add_item(self, table_name: TableNameEnum, item_payload: Dict[str, Any]) -> Dict[str, Any]:
        sqla_table = self._get_sqla_table(table_name)
        PydanticCreateModel = self.get_pydantic_model(table_name, "create")
        LOGGER.info(f"Attempting to add item to table '{table_name.value}' with payload: {item_payload}")

        # Calculate remaining_budget for category_budget_overview
        if table_name == TableNameEnum.CATEGORY_BUDGET_OVERVIEW:
            LOGGER.debug(f"Calculating remaining budget for category: {item_payload.get('category')}")
            budget = item_payload.get("budget_inr", 0.0)
            spent = item_payload.get("total_spent_inr", 0.0)
            item_payload["remaining_budget_inr"] = budget - spent
            
        item_create = PydanticCreateModel(**item_payload)
        
        insert_stmt = sqla_table.insert().values(**item_create.model_dump())
        LOGGER.debug(f"Executing SQL (add_item): {insert_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = self.db.execute(insert_stmt)
        self.db.commit()
        inserted_id = result.inserted_primary_key[0]
        LOGGER.info(f"Successfully added item with ID {inserted_id} to table '{table_name.value}'.")

        # If a transaction was added, update category budget
        if table_name == TableNameEnum.TRANSACTION_DETAILS and item_create.type.lower() == 'expense':
            LOGGER.info(f"Updating category budget for '{item_create.category}' due to new expense of {item_create.amount_inr}.")
            self._update_category_budget(item_create.category, item_create.amount_inr)
        return {"id": inserted_id, **item_create.model_dump()}

    def get_item_by_id(self, table_name: TableNameEnum, item_id: int) -> Optional[Dict[str, Any]]:
        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to get item with ID {item_id} from table '{table_name.value}'.")
        select_stmt = sqla_table.select().where(sqla_table.c.id == item_id)
        LOGGER.debug(f"Executing SQL (get_item_by_id): {select_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = self.db.execute(select_stmt).fetchone()
        if result:
            LOGGER.info(f"Found item with ID {item_id} in table '{table_name.value}'.")
            return dict(result._mapping)
        LOGGER.warning(f"Item with ID {item_id} not found in table '{table_name.value}'.")
        return None

    def get_all_items(self, table_name: TableNameEnum) -> List[Dict[str, Any]]:
        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to get all items from table '{table_name.value}'.")
        select_stmt = sqla_table.select()
        LOGGER.debug(f"Executing SQL (get_all_items): {select_stmt.compile(compile_kwargs={'literal_binds': True})}")
        results = self.db.execute(select_stmt).fetchall()
        LOGGER.info(f"Retrieved {len(results)} items from table '{table_name.value}'.")
        return [dict(row._mapping) for row in results]

    def update_item(self, table_name: TableNameEnum, item_id: int, item_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        sqla_table = self._get_sqla_table(table_name)
        PydanticUpdateModel = self.get_pydantic_model(table_name, "update")
        
        old_item_dict = None
        LOGGER.info(f"Attempting to update item with ID {item_id} in table '{table_name.value}' with payload: {item_payload}")
        if table_name == TableNameEnum.TRANSACTION_DETAILS:
            old_item_dict = self.get_item_by_id(table_name, item_id)
            if not old_item_dict:
                return None # Item not found

        item_update = PydanticUpdateModel(**item_payload)
        update_data = item_update.model_dump(exclude_unset=True)

        if not update_data:
            LOGGER.info(f"No update data provided for item ID {item_id} in table '{table_name.value}'. Returning current item.")
            return self.get_item_by_id(table_name, item_id)

        # If budget or total_spent is updated for category_budget_overview, recalculate remaining_budget
        if table_name == TableNameEnum.CATEGORY_BUDGET_OVERVIEW and ('budget_inr' in update_data or 'total_spent_inr' in update_data):
            LOGGER.debug(f"Recalculating remaining budget for category during update of item ID {item_id}.")
            current_item = self.get_item_by_id(table_name, item_id)
            if not current_item:
                return None # Item not found
            
            budget = update_data.get('budget_inr', current_item.get('budget_inr'))
            spent = update_data.get('total_spent_inr', current_item.get('total_spent_inr'))
            update_data['remaining_budget_inr'] = budget - spent

        update_stmt = (
            sqla_table.update()
            .where(sqla_table.c.id == item_id)
            .values(**update_data)
            .returning(*sqla_table.c) # Return the updated row
        )
        LOGGER.debug(f"Executing SQL (update_item): {update_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = self.db.execute(update_stmt).fetchone()
        self.db.commit()
        LOGGER.info(f"Update operation for item ID {item_id} in table '{table_name.value}' completed. Row count: {self.db.execute(update_stmt).rowcount if result else 0}")

        if table_name == TableNameEnum.TRANSACTION_DETAILS and result:
            # Handle changes in transaction amount or category
            old_amount = old_item_dict.get('amount_inr', 0.0) if old_item_dict.get('type','').lower() == 'expense' else 0.0
            old_category = old_item_dict.get('category')
            
            new_item_dict = dict(result._mapping)
            new_amount = new_item_dict.get('amount_inr', 0.0) if new_item_dict.get('type','').lower() == 'expense' else 0.0
            new_category = new_item_dict.get('category')

            if old_category != new_category:
                LOGGER.info(f"Transaction category changed for item ID {item_id}. Old: '{old_category}', New: '{new_category}'. Updating budgets.")
                if old_category: # Revert old category spending
                    self._update_category_budget(old_category, -old_amount)
                self._update_category_budget(new_category, new_amount) # Apply to new category
            elif old_amount != new_amount: # Same category, amount changed
                LOGGER.info(f"Transaction amount changed for item ID {item_id} in category '{new_category}'. Old: {old_amount}, New: {new_amount}. Updating budget.")
                self._update_category_budget(new_category, new_amount - old_amount)
        
        if not result:
            LOGGER.warning(f"Item with ID {item_id} not found or no changes made during update in table '{table_name.value}'.")
            return None
        LOGGER.info(f"Successfully updated item with ID {item_id} in table '{table_name.value}'.")
        return dict(result._mapping)


    def delete_item(self, table_name: TableNameEnum, item_id: int) -> bool:
        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to delete item with ID {item_id} from table '{table_name.value}'.")
        delete_stmt = sqla_table.delete().where(sqla_table.c.id == item_id)
        item_to_delete_dict = None

        if table_name == TableNameEnum.TRANSACTION_DETAILS:
            item_to_delete_dict = self.get_item_by_id(table_name, item_id)
            if not item_to_delete_dict:
                LOGGER.warning(f"Item with ID {item_id} not found in table '{TableNameEnum.TRANSACTION_DETAILS.value}' for pre-delete budget adjustment.")

        LOGGER.debug(f"Executing SQL (delete_item): {delete_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = self.db.execute(delete_stmt)
        self.db.commit()
        LOGGER.info(f"Delete operation for item ID {item_id} in table '{table_name.value}' completed. Rows affected: {result.rowcount}")

        if table_name == TableNameEnum.TRANSACTION_DETAILS and item_to_delete_dict and result.rowcount > 0:
            if item_to_delete_dict.get('type','').lower() == 'expense':
                 self._update_category_budget(item_to_delete_dict['category'], -item_to_delete_dict['amount_inr'])

        return result.rowcount > 0

