"""Expense_Reporter: Aggregates categorized receipts to produce detailed financial reports, including spend-by-category breakdowns and CSV exports."""

from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro-preview-05-06"

reporter_agent = Agent(
    model=MODEL,
    name="reporter_agent",
    description="Sub agent for generating reports.",
    instruction=prompt.REPORTER_PROMPT,   
    output_key="report"
)