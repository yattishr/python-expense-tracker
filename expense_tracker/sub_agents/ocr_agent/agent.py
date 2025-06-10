"""OCR_Agent Prompt: Performs OCR on a receipt image/PDF and returns structured JSON of receipt fields."""

from google.adk import Agent
from .tools.ocr_tool import ocr_tool

MODEL = "gemini-2.0-flash"

ocr_agent = Agent(
    name="ocr_agent",
    model=MODEL,
    description="Performs OCR on a receipt image/PDF and returns structured JSON of receipt fields.",
    instruction="""
    Given only the file path to a receipt image or PDF, call the ocr_tool to extract
    merchant, items, totals, dates, etc., then return *only* the resulting JSON.
    """,
    output_key="receipt_json",
    tools=[
        ocr_tool
    ],
)
