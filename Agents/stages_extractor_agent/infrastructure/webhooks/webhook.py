from dotenv import load_dotenv
from fastapi import APIRouter

from agents.stages_extractor_agent.domain.schemas import (QueryRequest, StagesExtractorAgentResponse)
from agents.stages_extractor_agent.infrastructure.external_services.langgraph_stages_extractor_agent import LANGGRAPH_STAGES_EXTRACT_AGENT

load_dotenv()

STAGES_EXTRACT_AGENT_WEBHOOK = APIRouter()


@STAGES_EXTRACT_AGENT_WEBHOOK.post("/invoke_stages_extract_agent", response_model=StagesExtractorAgentResponse)
def invoke_agent(request: QueryRequest):
    response = LANGGRAPH_STAGES_EXTRACT_AGENT.invoke_agent(request)
    return response
