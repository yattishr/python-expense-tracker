"""Expense_Categorizer: Classifies each parsed receipt into a predefined set of spending categories for downstream analysis and budgeting."""

from google.adk import Agent
from . import prompt
import os
from dotenv import load_dotenv
load_dotenv()

categorizer_agent = Agent(
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    name="categorizer_agent",
    description="Tags each receipt line‐item with a spending category.",
    instruction=prompt.CATEGORIZER_PROMPT,
    output_key="categorizer_items",
    # tools=[
    #     firestore_tool
    # ],
)
