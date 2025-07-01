import json
from typing import Union
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from core.logger import LOGGER
from agents.stages_extractor_agent.domain.schemas import (QueryRequest, StagesExtractorAgentResponse)
from agents.stages_extractor_agent.infrastructure.tools.stages_extract_agent_tools import process_video
               

class LangGraphStagesExtractorAgent:

    def _deep_json_eval(self, data):
        if isinstance(data, dict):
            return {k: self._deep_json_eval(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deep_json_eval(item) for item in data]
        elif isinstance(data, str):
            try:
                parsed = json.loads(data)
                return self._deep_json_eval(parsed)
            except (json.JSONDecodeError, TypeError):
                return data
        else:
            return data

    def invoke_agent(self, request: QueryRequest) -> StagesExtractorAgentResponse:
        model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature=0)

        file_path = 'agents/stages_extractor_agent/infrastructure/prompts/agent_prompt.txt'


        try:
            with open(file_path, 'r') as file:
                prompt_content = file.read()
            LOGGER.info(f"Prompt imported successfully:\n{prompt_content}")
        except FileNotFoundError:
            LOGGER.error(f"Prompt file not found: {file_path}")
            raise Exception(f"Prompt file not found: {file_path}")
        except Exception as e:
            LOGGER.error(f"Error reading prompt file: {e}")
            raise Exception(f"Error reading prompt file: {e}")

        stages_extract_agent = create_react_agent(
            model=model,
            tools=[process_video],
            prompt=prompt_content,
            name="stages_extract_agent",
        )

        response = stages_extract_agent.invoke({
            "messages": [{"role": "user", "content": request.query}]
        })

        raw_response = response['messages'][-1].content

        # Clean up formatting artifacts
        cleaned_response = raw_response.replace("json", "").replace("\n", "").replace("```", "").strip()

        # Try to parse as JSON or Python literal
        parsed_response: Union[str, dict]
        try:
            # evaluated_response = ast.literal_eval(cleaned_response)
            # parsed_response = self._deep_json_eval(evaluated_response)
            parsed_response = self._deep_json_eval(cleaned_response)
        except (ValueError, SyntaxError):
            parsed_response = cleaned_response  # Return as plain string

        return StagesExtractorAgentResponse(response=parsed_response)

    
LANGGRAPH_STAGES_EXTRACT_AGENT = LangGraphStagesExtractorAgent()
