"""Expense_Tracker: End-to-end expense receipt ingestion and management, encompassing OCR parsing, category assignment, financial reporting, and concise summary generation."""

from google.adk.agents import LlmAgent # This line is correct now
from google.adk.tools.agent_tool import AgentTool # This line is correct now

from . import prompt

from .sub_agents.categorizer_agent import categorizer_agent
from .sub_agents.reporter_agent import reporter_agent
from .sub_agents.summarizer_agent import summarizer_agent

from .tools.ocr_tool import ocr_tool

MODEL = "gemini-2.0-flash"

expense_coordinator = LlmAgent(
    name="expense_coordinator",
    model=MODEL,
    description=(
        "Handles end-to-end expense receipt processing: upload, parse, "
        "categorize, and report. "
        "Delegates category, report, and summary work to categorizer_agent, "
        "reporter_agent, and summarizer_agent sub-agents respectively."
    ),
    instruction=prompt.EXPENSE_COORDINATOR_PROMPT,
    output_key="expense_result",
    tools=[
        ocr_tool,
        AgentTool(agent=categorizer_agent),
        AgentTool(agent=reporter_agent),
    ],
    # sub_agents=[
    #     categorizer_agent,
    #     reporter_agent,
    #     summarizer_agent,
    # ],
)

root_agent = expense_coordinator
