from typing import Any, Dict
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str

class StagesExtractorAgentResponse(BaseModel):
    response: Dict[str, Any] | str | list[Dict[str, Any]]

class StagesExtractInputDetails(BaseModel):
    video_gcs_uri: str
