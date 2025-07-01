from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    print(f" env variable is {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")


llm = ChatVertexAI(

    model_name="gemini-2.0-flash-001",
    temperature=0.3,
    max_output_tokens=2000,
)

video_gs_uri = "gs://process-mining-bucket-1/How to Buy On Amazon (really easy).mp4"
video_mime_type = "video/mp4"
prompt = "summarize the video by providing 5 pointers."

video_part = {
            "type": "media",
            "file_uri": video_gs_uri,
            "mime_type": video_mime_type,
        }

# video_part = {
#             "type": "video_file",
#             "video_file": {
#                 "uri": video_gs_uri,
#                 "mime_type": video_mime_type
#                 }
#             }

text_part = {
    "type": "text",
    "text": prompt
}

message = HumanMessage(
    content=[video_part, text_part]
)

response = llm.invoke([message])

print(response.content)