"""Data_Agent: Aggregates and analyzes historical spending data for a user, returning category-level trends and monthly breakdowns for downstream insight and nudge generation."""

from google.adk import Agent
from .tools.data_agent_tool import data_agent_tool
from google.adk.tools import FunctionTool

MODEL = "gemini-2.0-flash"

data_agent = Agent(
    name="data_agent",
    model=MODEL,
    description="Aggregates expense history for a user for use by downstream Insights Agent",
    instruction="Call the data_agent_tool to retrieve spend history for a user.",
    tools=[FunctionTool(func=data_agent_tool)]
)
