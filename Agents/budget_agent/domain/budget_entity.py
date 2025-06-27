from sqlalchemy import MetaData, Table
from sqlalchemy import Column, Integer, String, MetaData, Table, Float, Date


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
