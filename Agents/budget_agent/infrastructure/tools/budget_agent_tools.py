from typing import Dict, Any, List

from core.logger import LOGGER
from agents.budget_agent.domain.schemas import (TableNameEnum, 
                      CategoryBudgetOverviewCreate, 
                      CategoryBudgetOverviewUpdate, 
                      CategoryBudgetOverview, 
                      TransactionDetailCreate, 
                      TransactionDetailUpdate, 
                      TransactionDetail)
from agents.budget_agent.infrastructure.webhooks import BUDGET_USECASE


def add_category_budget(payload: CategoryBudgetOverviewCreate) -> CategoryBudgetOverview:
    """
    Adds a category budget to the database.
    :param payload: A Pydantic model containing the category budget data.
    """
    LOGGER.info(f"Adding category budget with payload: {payload}")
    try:

        added_category = BUDGET_USECASE.handle_add_item(
            TableNameEnum.CATEGORY_BUDGET_OVERVIEW, payload.model_dump()
        )
        LOGGER.info(f"Added category: {added_category}")
        return added_category.model_dump()
    except Exception as e:
        LOGGER.error(f"Error adding category: {e}", exc_info=True)
        raise


def add_transaction(payload: TransactionDetailCreate) -> TransactionDetail:
    """
    Adds a transaction to the database.
    :param payload: A Pydantic model containing the transaction data.
    """

    LOGGER.info(f"Adding transaction with payload: {payload}")
    try:
        added_transaction = BUDGET_USECASE.handle_add_item(
            TableNameEnum.TRANSACTION_DETAILS, payload.model_dump()
        )
        LOGGER.info(f"Added transaction: {added_transaction}")
        return added_transaction.model_dump()
    except Exception as e:
        LOGGER.error(f"Error adding transaction: {e}", exc_info=True)
        raise


def get_all_category_budgets() -> List[CategoryBudgetOverview]:
    """
    Gets all category budgets from the database.
    """

    LOGGER.info("Getting all category budgets")
    try:
        all_categories = BUDGET_USECASE.handle_get_all_items(TableNameEnum.CATEGORY_BUDGET_OVERVIEW)
        LOGGER.info(f"Found {len(all_categories)} category budgets.")
        all_categories = [category.model_dump() for category in all_categories]
        return all_categories
    except Exception as e:
        LOGGER.error(f"Error getting all categories: {e}", exc_info=True)
        raise


def get_all_transactions() -> List[TransactionDetail]:
    """
    Gets all transactions from the database.
    """

    LOGGER.info("Getting all transactions")
    try:
        all_transactions = BUDGET_USECASE.handle_get_all_items(TableNameEnum.TRANSACTION_DETAILS)
        LOGGER.info(f"Found {len(all_transactions)} transactions.")
        all_transactions = [transaction.model_dump() for transaction in all_transactions]
        return all_transactions
    except Exception as e:
        LOGGER.error(f"Error getting all transactions: {e}", exc_info=True)
        raise
        
def update_transaction(item_id: int, update_data: TransactionDetailUpdate) -> TransactionDetail:
    """
    Updates a transaction in the database.
    :param item_id: The ID of the transaction to update.
    :param update_data: A Pydantic model with the fields to update.
    """

    LOGGER.info(f"Updating transaction ID {item_id} with data: {update_data}")
    try:
        payload: Dict[str, Any] = {"id": item_id, "update_data": update_data.model_dump(exclude_unset=True)}
        updated_transaction = BUDGET_USECASE.handle_update_item(TableNameEnum.TRANSACTION_DETAILS, payload)
        LOGGER.info(f"Updated transaction: {updated_transaction}")
        return updated_transaction.model_dump()
    except Exception as e:
        LOGGER.error(f"Error updating transaction: {e}", exc_info=True)
        raise

def update_category_budget(item_id: int, update_data: CategoryBudgetOverviewUpdate) -> CategoryBudgetOverview:
    """
    Updates a category budget in the database.
    :param item_id: The ID of the category budget to update.
    :param update_data: A Pydantic model with the fields to update.
    """

    LOGGER.info(f"Updating category budget ID {item_id} with data: {update_data}")
    try:
        payload: Dict[str, Any] = {"id": item_id, "update_data": update_data.model_dump(exclude_unset=True)}
        updated_category = BUDGET_USECASE.handle_update_item(TableNameEnum.CATEGORY_BUDGET_OVERVIEW, payload)
        LOGGER.info(f"Updated category: {updated_category}")
        return updated_category.model_dump()
    except Exception as e:
        LOGGER.error(f"Error updating category: {e}", exc_info=True)
        raise

def delete_transaction(item_id: int) -> Dict[str, Any]:
    """
    Deletes a transaction from the database.
    :param item_id: The ID of the transaction to delete.
    """
    LOGGER.info(f"Deleting transaction ID {item_id}")
    try:
        payload = {"id": item_id}
        delete_response = BUDGET_USECASE.handle_delete_item(TableNameEnum.TRANSACTION_DETAILS, payload)
        LOGGER.info(delete_response)
        return delete_response
    except Exception as e:
        LOGGER.error(f"Error deleting transaction: {e}", exc_info=True)
        raise

def delete_category_budget(item_id: int) -> Dict[str, Any]:
    """
    Deletes a category budget from the database.
    :param item_id: The ID of the category budget to delete.
    """

    LOGGER.info(f"Deleting category budget ID {item_id}")
    try:
        payload = {"id": item_id}
        delete_response = BUDGET_USECASE.handle_delete_item(TableNameEnum.CATEGORY_BUDGET_OVERVIEW, payload)
        LOGGER.info(delete_response)
        return delete_response
    except Exception as e:
        LOGGER.error(f"Error deleting category budget: {e}", exc_info=True)
        raise

