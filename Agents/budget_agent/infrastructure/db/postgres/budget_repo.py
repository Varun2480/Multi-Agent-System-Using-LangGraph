
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy import Table
from core.logger import LOGGER

from agents.budget_agent.domain.budget_entity import category_budget_table, transaction_details_table
from agents.budget_agent.domain.schemas import (TableNameEnum, 
                            TransactionDetail, 
                            TransactionDetailCreate, 
                            TransactionDetailUpdate, 
                            CategoryBudgetOverviewCreate, 
                            CategoryBudgetOverviewUpdate, 
                            CategoryBudgetOverview) 
from agents.budget_agent.domain.interface.interface_context_repo import IRepoContext


# --- Database CRUD Class ---
class BudgetRepo:
    def __init__(self):
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
    
    def _update_category_budget(self, repo_context: IRepoContext, category_name: str, amount_change: float):
        """
        Helper function to update total_spent and remaining_budget for a category.
        'amount_change' is positive for an expense, negative for an income or reversal.
        """

        category_budget_s = self._get_sqla_table(TableNameEnum.CATEGORY_BUDGET_OVERVIEW)
        
        # Fetch the current budget and spent amount
        stmt = category_budget_s.select().where(category_budget_s.c.category == category_name)
        category_row = repo_context.session.execute(stmt).fetchone()

        if category_row:
            new_total_spent = category_row.total_spent_inr + amount_change
            remaining_budget = category_row.budget_inr - new_total_spent
            update_stmt = category_budget_s.update().where(category_budget_s.c.category == category_name).values(total_spent_inr=new_total_spent, remaining_budget_inr=remaining_budget)
            repo_context.session.execute(update_stmt)
            repo_context.session.commit()
        LOGGER.info(f"Updated the budget for the category {category_name}")

    def add_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_payload: Dict[str, Any]) -> Dict[str, Any]:
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
        result = repo_context.session.execute(insert_stmt)
        repo_context.session.commit()

        inserted_id = result.inserted_primary_key[0]
        LOGGER.info(f"Successfully added item with ID {inserted_id} to table '{table_name.value}'.")

        # If a transaction was added, update category budget
        if table_name == TableNameEnum.TRANSACTION_DETAILS and item_create.type.lower() == 'expense':
            LOGGER.info(f"Updating category budget for '{item_create.category}' due to new expense of {item_create.amount_inr}.")
            self._update_category_budget(repo_context, item_create.category, item_create.amount_inr)
        return {"id": inserted_id, **item_create.model_dump()}

    def get_item_by_id(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> Optional[Dict[str, Any]]:

        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to get item with ID {item_id} from table '{table_name.value}'.")
        select_stmt = sqla_table.select().where(sqla_table.c.id == item_id)
        LOGGER.debug(f"Executing SQL (get_item_by_id): {select_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = repo_context.session.execute(select_stmt).fetchone()
        if result:
            LOGGER.info(f"Found item with ID {item_id} in table '{table_name.value}'.")
            return dict(result._mapping)
        LOGGER.warning(f"Item with ID {item_id} not found in table '{table_name.value}'.")
        return None

    def get_all_items(self, repo_context: IRepoContext, table_name: TableNameEnum) -> List[Dict[str, Any]]:

        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to get all items from table '{table_name.value}'.")
        select_stmt = sqla_table.select()
        LOGGER.debug(f"Executing SQL (get_all_items): {select_stmt.compile(compile_kwargs={'literal_binds': True})}")
        results = repo_context.session.execute(select_stmt).fetchall()
        LOGGER.info(f"Retrieved {len(results)} items from table '{table_name.value}'.")
        return [dict(row._mapping) for row in results]
        
    def update_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int, item_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        sqla_table = self._get_sqla_table(table_name)
        PydanticUpdateModel = self.get_pydantic_model(table_name, "update")

        old_item_dict = self._fetch_old_item_if_needed(repo_context, table_name, item_id)
        if table_name == TableNameEnum.TRANSACTION_DETAILS and not old_item_dict:
            return None

        update_data = self._prepare_update_data(PydanticUpdateModel, item_payload)
        if not update_data:
            return self.get_item_by_id(repo_context, table_name, item_id)

        if table_name == TableNameEnum.CATEGORY_BUDGET_OVERVIEW:
            update_data = self._recalculate_remaining_budget(repo_context, item_id, update_data)

        update_stmt = (
        sqla_table.update()
        .where(sqla_table.c.id == item_id)
        .values(**update_data)
        .returning(*sqla_table.c)
        )
        LOGGER.debug(f"Executing SQL (update_item): {update_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = repo_context.session.execute(update_stmt).fetchone()
        repo_context.session.commit()

        if table_name == TableNameEnum.TRANSACTION_DETAILS and result:
            self._handle_transaction_budget_update(repo_context, item_id, old_item_dict, dict(result._mapping))

        if not result:
            return None

        return dict(result._mapping)

    # 🔹 Sub-functions

    def _fetch_old_item_if_needed(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> Optional[Dict[str, Any]]:
        if table_name == TableNameEnum.TRANSACTION_DETAILS:
            return self.get_item_by_id(repo_context, table_name, item_id)
        return None

    def _prepare_update_data(self, PydanticUpdateModel, item_payload: Dict[str, Any]) -> Dict[str, Any]:
        item_update = PydanticUpdateModel(**item_payload)
        return item_update.model_dump(exclude_unset=True)

    def _recalculate_remaining_budget(self, repo_context: IRepoContext, item_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        current_item = self.get_item_by_id(repo_context, TableNameEnum.CATEGORY_BUDGET_OVERVIEW, item_id)
        if not current_item:
            return update_data

        budget = update_data.get('budget_inr', current_item.get('budget_inr'))
        spent = update_data.get('total_spent_inr', current_item.get('total_spent_inr'))
        update_data['remaining_budget_inr'] = budget - spent
        return update_data

    def _handle_transaction_budget_update(self, repo_context: IRepoContext, item_id: int, old_item_dict: Dict[str, Any], new_item_dict: Dict[str, Any]):
        old_amount = old_item_dict.get('amount_inr', 0.0) if old_item_dict.get('type', '').lower() == 'expense' else 0.0
        old_category = old_item_dict.get('category')
        new_amount = new_item_dict.get('amount_inr', 0.0) if new_item_dict.get('type', '').lower() == 'expense' else 0.0
        new_category = new_item_dict.get('category')

        if old_category != new_category:
            if old_category:
                self._update_category_budget(repo_context, old_category, -old_amount)
            self._update_category_budget(repo_context, new_category, new_amount)
        elif old_amount != new_amount:
            self._update_category_budget(repo_context, new_category, new_amount - old_amount)

    def delete_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> bool:

        sqla_table = self._get_sqla_table(table_name)
        LOGGER.info(f"Attempting to delete item with ID {item_id} from table '{table_name.value}'.")
        delete_stmt = sqla_table.delete().where(sqla_table.c.id == item_id)
        item_to_delete_dict = None

        if table_name == TableNameEnum.TRANSACTION_DETAILS:
            item_to_delete_dict = self.get_item_by_id(repo_context, table_name, item_id)
            if not item_to_delete_dict:
                LOGGER.warning(f"Item with ID {item_id} not found in table '{TableNameEnum.TRANSACTION_DETAILS.value}' for pre-delete budget adjustment.")

        LOGGER.debug(f"Executing SQL (delete_item): {delete_stmt.compile(compile_kwargs={'literal_binds': True})}")
        result = repo_context.session.execute(delete_stmt)
        repo_context.session.commit()
        LOGGER.info(f"Delete operation for item ID {item_id} in table '{table_name.value}' completed. Rows affected: {result.rowcount}")

        if table_name == TableNameEnum.TRANSACTION_DETAILS and item_to_delete_dict and result.rowcount > 0:
            if item_to_delete_dict.get('type','').lower() == 'expense':
                self._update_category_budget(repo_context, item_to_delete_dict['category'], -item_to_delete_dict['amount_inr'])

        return result.rowcount > 0
