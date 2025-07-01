# app/api/v1/router.py
from fastapi import APIRouter
from agents.budget_agent.infrastructure.webhooks.webhook import BUDGET_AGENT_WEBHOOK
from agents.stages_extractor_agent.infrastructure.webhooks.webhook import STAGES_EXTRACT_AGENT_WEBHOOK

api_router = APIRouter()

api_router.include_router(
    BUDGET_AGENT_WEBHOOK,
    prefix="/webhooks/budget-agent",
    tags=["Budget Agent"]
)

api_router.include_router(
    STAGES_EXTRACT_AGENT_WEBHOOK,
    prefix="/webhooks/stages-extract-agent",
    tags=["Stages Extract Agent"]
)
