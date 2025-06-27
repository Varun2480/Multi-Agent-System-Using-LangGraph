from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel
from agents.budget_agent.domain.schemas import TableNameEnum
from agents.budget_agent.domain.interface.interface_context_repo import IRepoContext

class IBudgetRepo(Protocol):

    def get_pydantic_model(self, table_name: TableNameEnum, model_type: str) -> BaseModel:
        ...

    def add_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def get_item_by_id(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> Optional[Dict[str, Any]]:
        ...
    
    def get_all_items(self, repo_context: IRepoContext, table_name: TableNameEnum) -> List[Dict[str, Any]]:
        ...

    def update_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int, item_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ...
    
    def delete_item(self, repo_context: IRepoContext, table_name: TableNameEnum, item_id: int) -> bool:
        ...

    