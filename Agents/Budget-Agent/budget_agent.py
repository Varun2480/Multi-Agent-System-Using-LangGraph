import os
import ast
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from fastapi import FastAPI
from pydantic import BaseModel

from settings import LOGGER
from db_context import SessionLocal
from budget_agent_usecase import BudgetAgentUsecase
from schemas import (AgentResponse, QueryRequest, TableNameEnum, 
                      CategoryBudgetOverviewCreate, 
                      CategoryBudgetOverviewUpdate, 
                      CategoryBudgetOverview, 
                      TransactionDetailCreate, 
                      TransactionDetailUpdate, 
                      TransactionDetail)


load_dotenv()


# --- Environment Variable Checks ---
google_api_key_loaded = os.getenv("GOOGLE_API_KEY") is not None

LOGGER.info(f"Google API Key Loaded: {google_api_key_loaded}")

app = FastAPI(title="Budget Agent API")

def add_category_budget(payload: CategoryBudgetOverviewCreate) -> CategoryBudgetOverview:
    """
    Adds a category budget to the database.
    :param payload: A Pydantic model containing the category budget data.
    """
    with SessionLocal() as db:
        LOGGER.info(f"Adding category budget with payload: {payload}")
        try:
            usecase = BudgetAgentUsecase(db)
            added_category = usecase.handle_add_item(
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
    with SessionLocal() as db:
        LOGGER.info(f"Adding transaction with payload: {payload}")
        try:
            usecase = BudgetAgentUsecase(db)
            added_transaction = usecase.handle_add_item(
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
    with SessionLocal() as db:
        LOGGER.info("Getting all category budgets")
        try:
            usecase = BudgetAgentUsecase(db)
            all_categories = usecase.handle_get_all_items(TableNameEnum.CATEGORY_BUDGET_OVERVIEW)
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
    with SessionLocal() as db:
        LOGGER.info("Getting all transactions")
        try:
            usecase = BudgetAgentUsecase(db)
            all_transactions = usecase.handle_get_all_items(TableNameEnum.TRANSACTION_DETAILS)
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
    with SessionLocal() as db:
        LOGGER.info(f"Updating transaction ID {item_id} with data: {update_data}")
        try:
            usecase = BudgetAgentUsecase(db)
            payload = {"id": item_id, "update_data": update_data.model_dump(exclude_unset=True)}
            updated_transaction = usecase.handle_update_item(TableNameEnum.TRANSACTION_DETAILS, payload)
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
    with SessionLocal() as db:
        LOGGER.info(f"Updating category budget ID {item_id} with data: {update_data}")
        try:
            usecase = BudgetAgentUsecase(db)
            payload = {"id": item_id, "update_data": update_data.model_dump(exclude_unset=True)}
            updated_category = usecase.handle_update_item(TableNameEnum.CATEGORY_BUDGET_OVERVIEW, payload)
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
    with SessionLocal() as db:
        LOGGER.info(f"Deleting transaction ID {item_id}")
        try:
            usecase = BudgetAgentUsecase(db)
            payload = {"id": item_id}
            delete_response = usecase.handle_delete_item(TableNameEnum.TRANSACTION_DETAILS, payload)
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
    with SessionLocal() as db:
        LOGGER.info(f"Deleting category budget ID {item_id}")
        try:
            usecase = BudgetAgentUsecase(db)
            payload = {"id": item_id}
            delete_response = usecase.handle_delete_item(TableNameEnum.CATEGORY_BUDGET_OVERVIEW, payload)
            LOGGER.info(delete_response)
            return delete_response
        except Exception as e:
            LOGGER.error(f"Error deleting category budget: {e}", exc_info=True)
            raise


def deep_json_eval(data):
    if isinstance(data, dict):
        return {k: deep_json_eval(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_json_eval(item) for item in data]
    elif isinstance(data, str):
        try:
            parsed = json.loads(data)
            return deep_json_eval(parsed)
        except (json.JSONDecodeError, TypeError):
            return data
    else:
        return data


@app.post("/invoke_agent", response_model=AgentResponse)
def invoke_agent(request: QueryRequest):
    model = init_chat_model("gemini-1.5-flash", 
                            model_provider="google_genai",
                            temperature=0)

    file_path = 'prompt.txt'  # Specify the path to your text file

    try:
        with open(file_path, 'r') as file:
            prompt_content = file.read()
        LOGGER.info("Prompt imported successfully:")
        LOGGER.info(f"Prompt is {prompt_content}")
    except FileNotFoundError:
        LOGGER.error(f"Error: The file '{file_path}' was not found.")
        raise Exception(f"Prompt file not found: {file_path}")
    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")
        raise Exception(f"Error reading prompt file: {e}")


    budget_agent = create_react_agent(
        model=model,
        tools=[add_category_budget, 
            add_transaction, 
            get_all_category_budgets, 
            get_all_transactions, 
            update_transaction, 
            update_category_budget, 
            delete_transaction, 
            delete_category_budget],
        prompt=str(prompt_content),
        name="budget_agent",
    )

    response = budget_agent.invoke(
        {"messages": [{"role": "user", 
                    "content": request.query}]}
    )
    import pdb; pdb.set_trace()
    response = response['messages'][-1].content

    if isinstance(response, str):
        response = response.replace("json", "")
        response = response.replace("\n", "")
        response = response.replace("```", "")
        
        # Step 1: Safely evaluate the outer dictionary
        evaluated_response = ast.literal_eval(response)

    
    # Step 2: Recursively parse nested JSON strings
    final_json_response = deep_json_eval(evaluated_response)

    return AgentResponse(response=final_json_response)


# {
#   "query": "I want to view the trasactions history. List all the transactions"
# }


