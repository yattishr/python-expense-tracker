# agent.py
"""Data_Agent: Aggregates and analyzes historical spending data for a user, returning category-level trends and monthly breakdowns for downstream insight and nudge generation."""

from google.adk import Agent
from .tools.data_agent_tool import data_agent_tool # Import the function directly
import os
from dotenv import load_dotenv
load_dotenv()

data_agent = Agent(
    name="data_agent",
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    description="Aggregates expense history for a user for use by downstream Insights Agent",    
    instruction="""When you are invoked, immediately call the function `data_agent_tool` with:
                    • user_id set to the conversation’s USER_ID (from the API call),
                    • months left at its default of 2.
                Return *only* the JSON output of that tool (i.e. { "history": […] }).
                Do not emit any other text or ask follow-up questions.""",
    tools=[data_agent_tool],
    output_key="history",
)
