# agents/expense_ingestor_agent.py

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .categorizer_agent import categorizer_agent
from .reporter_agent import reporter_agent

MODEL = "gemini-2.0-flash"

expense_ingestor_agent = LlmAgent(
    name="expense_ingestor",
    model=MODEL,
    description=(
        "Ingests expense receipts, processes them, "
        "delegates categorization and reporting to sub-agents."
    ),
    instruction=prompt.EXPENSE_INGESTOR_PROMPT,
    output_key="expense_receipt",
    tools=[
        AgentTool(agent=categorizer_agent),
        AgentTool(agent=reporter_agent),
    ],
)

root_agent = expense_ingestor_agent