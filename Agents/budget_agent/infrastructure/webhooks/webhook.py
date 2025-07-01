from dotenv import load_dotenv
from fastapi import APIRouter

from agents.budget_agent.domain.schemas import (BudgetAgentResponse, QueryRequest)
from agents.budget_agent.infrastructure.external_services.langgraph_budget_agent import LANGGRAPH_BUDGET_AGENT

load_dotenv()

BUDGET_AGENT_WEBHOOK = APIRouter()


@BUDGET_AGENT_WEBHOOK.post("/invoke_budget_agent", response_model=BudgetAgentResponse)
def invoke_agent(request: QueryRequest):
    response = LANGGRAPH_BUDGET_AGENT.invoke_agent(request)
    return response

# {
#   "query": "I want to view the trasactions history. List all the transactions"
# }
