from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from agents.budget_agent.domain.interface.interface_budget_repo import IBudgetRepo
from agents.budget_agent.domain.interface.interface_context_repo import IRepoContext
from agents.budget_agent.domain.schemas import TableNameEnum

class BudgetAggregate:

    @staticmethod
    def get_pydantic_model(budget_repo: IBudgetRepo, table_name: TableNameEnum, model_type: str) -> BaseModel:
        return budget_repo.get_pydantic_model(table_name=table_name, model_type=model_type)

    @staticmethod
    def add_item(budget_repo: IBudgetRepo, repo_context: IRepoContext, table_name: TableNameEnum, item_payload: Dict[str, Any]) -> Dict[str, Any]:
        return budget_repo.add_item(repo_context, table_name, item_payload)

    @staticmethod
    def get_item_by_id(budget_repo: IBudgetRepo, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> Optional[Dict[str, Any]]:
        return budget_repo.get_item_by_id(repo_context, table_name, item_id)
    
    @staticmethod
    def get_all_items(budget_repo: IBudgetRepo, repo_context: IRepoContext, table_name: TableNameEnum) -> List[Dict[str, Any]]:
        return budget_repo.get_all_items(repo_context, table_name)

    @staticmethod
    def update_item(budget_repo: IBudgetRepo, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int, item_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return budget_repo.update_item(repo_context, table_name, item_id, item_payload)
    
    @staticmethod
    def delete_item(budget_repo: IBudgetRepo, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> bool:
        return budget_repo.delete_item(repo_context, table_name, item_id)

    