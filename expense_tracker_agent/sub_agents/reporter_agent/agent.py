"""Expense_Reporter: Aggregates categorized receipts to produce detailed financial reports, including spend-by-category breakdowns and CSV exports."""

from google.adk import Agent
from . import prompt
import os
from dotenv import load_dotenv
load_dotenv()

reporter_agent = Agent(
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    name="reporter_agent",
    description="Sub agent for generating reports.",
    instruction=prompt.REPORTER_PROMPT,   
    output_key="report"
)