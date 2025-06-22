# --- Pydantic Models ---

import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, field_serializer
from enum import Enum as PyEnum # Renamed to avoid conflict with Pydantic's Enum if any

# CategoryBudgetOverview Models
class CategoryBudgetOverviewBase(BaseModel):
    category: str
    budget_inr: float
    total_spent_inr: float = 0.0
    remaining_budget_inr: Optional[float] = None # Will be calculated or set

class CategoryBudgetOverviewCreate(CategoryBudgetOverviewBase):
    pass

class CategoryBudgetOverviewUpdate(BaseModel):
    category: Optional[str] = None
    budget_inr: Optional[float] = None
    total_spent_inr: Optional[float] = None
    remaining_budget_inr: Optional[float] = None

class CategoryBudgetOverview(CategoryBudgetOverviewBase):
    id: int

    class Config:
        from_attributes = True

# TransactionDetail Models
class TransactionDetailBase(BaseModel):
    transaction_date: datetime.date
    category: str
    description: Optional[str] = None
    amount_inr: float
    type: str # e.g. "expense", "income"
    location: Optional[str] = None

    @field_serializer('transaction_date')
    def serialize_transaction_date(self, dt: datetime.date) -> int:
        return int(datetime.datetime(dt.year, dt.month, dt.day).timestamp())

class TransactionDetailCreate(TransactionDetailBase):
    pass

class TransactionDetailUpdate(BaseModel):
    transaction_date: Optional[datetime.date] = None
    category: Optional[str] = None
    description: Optional[str] = None
    amount_inr: Optional[float] = None
    type: Optional[str] = None
    location: Optional[str] = None

    @field_serializer('transaction_date')
    def serialize_transaction_date(self, dt: datetime.date) -> int:
        return int(datetime.datetime(dt.year, dt.month, dt.day).timestamp())

class TransactionDetail(TransactionDetailBase):
    id: int

    class Config:
        from_attributes = True

# --- Enum for Table Names and Operations ---
class TableNameEnum(str, PyEnum):
    CATEGORY_BUDGET_OVERVIEW = "category_budget_overview"
    TRANSACTION_DETAILS = "transaction_details"

class QueryOperationEnum(str, PyEnum):
    CREATE_TABLES = "create_tables"
    ADD = "add"
    GET_ONE = "get_one"
    GET_ALL = "get_all"
    UPDATE = "update"
    DELETE = "delete"

# --- Request Model for the Single Endpoint ---
class APIRequest(BaseModel):
    table: Optional[TableNameEnum] = None # Optional only for CREATE_TABLES
    query_type: QueryOperationEnum
    payload: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    final_response: Dict[str, Any]