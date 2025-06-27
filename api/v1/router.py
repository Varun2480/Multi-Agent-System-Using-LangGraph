# app/api/v1/router.py
from fastapi import APIRouter
from agents.budget_agent.infrastructure.webhooks.webhook import BUDGET_AGENT_WEBHOOK

api_router = APIRouter()

api_router.include_router(
    BUDGET_AGENT_WEBHOOK,
    prefix="/webhooks/budget-agent",
    tags=["Budget Agent"]
)
