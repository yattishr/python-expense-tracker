# agent.py
"""Ingestion_Agent: Takes receipt JSON and stores it in the database."""

from google.adk import Agent
from .tools.ingestion_tool import ingestion_tool # Import the new tool
import os
from dotenv import load_dotenv
load_dotenv()

ingestion_agent = Agent(
    name="ingestion_agent",
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    description=(
        "Processes the JSON output from OCR and stores the expense in the database."
    ),
    instruction="""
        You will receive a JSON string in the conversation history under the key 'categorizer_items'.
        Immediately call the tool `ingestion_tool` with the following arguments:
        - `categorizer_items`: The JSON string found in the conversation history.
        - `user_id`: The conversation’s USER_ID (from the API call).
        Return *only* the status JSON from the tool call.
    """,
    tools=[ingestion_tool],
    output_key="ingestion_status",
)