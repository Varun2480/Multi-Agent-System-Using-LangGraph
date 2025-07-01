
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from agents.stages_extractor_agent.domain.schemas import StagesExtractInputDetails
from core.logger import LOGGER

load_dotenv()

# Global variables for model initialization to optimize cold starts
# These are initialized once per function instance
model = None

def get_model():
    """Initializes Vertex AI and the GenerativeModel.
    This function should be called once per instance to reduce cold start latency.
    """
    global model
    if model is None:
        model = ChatVertexAI(
            model_name="gemini-2.0-flash-001",
            temperature=0.3,
            max_output_tokens=2000,
            )
        LOGGER.info(f"Vertex AI Model Initialized")
    return model

def get_prompt():
        
        file_path = 'agents/stages_extractor_agent/infrastructure/prompts/stages_extract_tool_prompt.txt'

        try:
            with open(file_path, 'r') as file:
                prompt_content = file.read()
            LOGGER.info(f"Prompt imported successfully:\n{prompt_content}")
            return prompt_content
        except FileNotFoundError:
            LOGGER.error(f"Prompt file not found: {file_path}")
            raise Exception(f"Prompt file not found: {file_path}")
        except Exception as e:
            LOGGER.error(f"Error reading prompt file: {e}")
            raise Exception(f"Error reading prompt file: {e}")

def process_video(request: StagesExtractInputDetails) -> str:
    """HTTP Cloud Function that processes a video GCS URI to extract workflow stages
    and steps using Gemini 2.0 Flash.

    Args:
        request (flask.Request): The request object. Expects a JSON payload
                                 with 'video_gcs_uri'.
    Returns:
        The extracted workflow as JSON, or an error message.
    """
    
    video_mime_type = "video/mp4"
    STAGE_GENERATION_PROMPT = get_prompt()
    LLM = get_model()

    video_part = {
        "type": "media",
        "file_uri": request.video_gcs_uri,
        "mime_type": video_mime_type,}
    
    text_part = {
        "type": "text",
        "text": STAGE_GENERATION_PROMPT
        }
    
    message = HumanMessage(
        content=[video_part, text_part]
        )
    
    try:
        response = LLM.invoke([message])
        LOGGER.info(f"Successfully generated the stages from provided video.")
        return str(response.content)
    except Exception as e:
        LOGGER.error(f"An error occurred during content generation: {e}")
        return f"Error during video processing: {e}"