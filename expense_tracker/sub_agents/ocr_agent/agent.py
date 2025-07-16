"""OCR_Agent Prompt: Performs OCR on a receipt image/PDF and returns structured JSON of receipt fields."""

from google.adk import Agent
from .tools.ocr_tool import ocr_tool
import os
from dotenv import load_dotenv
load_dotenv()

ocr_agent = Agent(
    name="ocr_agent",
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    description=(
        "Performs OCR on a receipt image/PDF passed as inlineData; "
        "returns structured JSON of receipt fields."
    ),
    instruction="""
        You will get exactly one message part of type inlineData (with base64 ‘data’ and ‘mimeType’).
        Call the tool `ocr_tool` passing that inline_data object.
        Return *only* the JSON string your tool returns.
    """,
    output_key="receipt_json",
    tools=[ocr_tool],
)
