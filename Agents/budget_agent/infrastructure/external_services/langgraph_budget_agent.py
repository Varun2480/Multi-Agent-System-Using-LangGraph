import ast
import json
from typing import Union
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from core.logger import LOGGER
from agents.budget_agent.domain.schemas import (BudgetAgentResponse, QueryRequest)
from agents.budget_agent.infrastructure.tools.budget_agent_tools import (add_category_budget,  
                                      add_transaction,
                                      get_all_category_budgets,
                                      get_all_transactions,
                                      update_category_budget,
                                      update_transaction,
                                      delete_category_budget,
                                      delete_transaction
                                      )
               

class LangGraphBudgetAgent:

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


    def invoke_agent(self, request: QueryRequest) -> BudgetAgentResponse:
        model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature=0)

        file_path = 'agents/budget_agent/prompt_2.txt'

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

        budget_agent = create_react_agent(
            model=model,
            tools=[
                add_category_budget, add_transaction, get_all_category_budgets,
                get_all_transactions, update_transaction, update_category_budget,
                delete_transaction, delete_category_budget
            ],
            prompt=prompt_content,
            name="budget_agent",
        )

        response = budget_agent.invoke({
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

        return BudgetAgentResponse(response=parsed_response)

    
LANGGRAPH_AGENT = LangGraphBudgetAgent()
