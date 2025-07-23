"""Expense_Summarizer: Generates concise, human-readable summaries of processed expenses, highlighting totals, top categories, and key observations."""

from google.adk import Agent
from . import prompt
import os
from dotenv import load_dotenv
load_dotenv()

summarizer_agent = Agent(
    name="summarizer_agent",
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    description="Summarizes expense/receipt data into a brief human-readable summary.",
    instruction=prompt.SUMMARIZER_PROMPT,
    output_key="summary"
)
