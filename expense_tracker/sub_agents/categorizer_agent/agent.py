"""Expense_Categorizer: Classifies each parsed receipt into a predefined set of spending categories for downstream analysis and budgeting."""

from google.adk import Agent
from . import prompt
# from .tools.firestore_tool import firestore_tool

MODEL = "gemini-2.5-pro-preview-05-06"

categorizer_agent = Agent(
    model=MODEL,
    name="categorizer_agent",
    description="Tags each receipt line‐item with a spending category.",
    instruction=prompt.CATEGORIZER_PROMPT,
    output_key="items",
    # tools=[
    #     firestore_tool
    # ],
)
