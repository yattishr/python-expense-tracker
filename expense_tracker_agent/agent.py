"""Expense_Tracker: End-to-end expense receipt ingestion and management, encompassing OCR parsing, category assignment, financial reporting, and concise summary generation."""

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
import os
from dotenv import load_dotenv
from .sub_agents.categorizer_agent import categorizer_agent
from .sub_agents.reporter_agent import reporter_agent
from .sub_agents.summarizer_agent import summarizer_agent
from .sub_agents.ocr_agent.agent import ocr_agent
from .sub_agents.data_agent.agent import data_agent
from . import prompt

load_dotenv()

PIPELINE_INSTRUCTION = """
You are ExpensePipelineAgent.  You must orchestrate five sub-agents **in exactly this order**:
 
  1. ocr_agent  
  2. data_agent  
  3. categorizer_agent  
  4. reporter_agent  
  5. summarizer_agent  

**At each step**, emit exactly:
transfer_to_agent({"agent_name": "<next_agent_name>"})
Do **not** produce any free-text reply until you have completed step 5.  After summarizer_agent runs, return its JSON under the key `"final_report"`, then stop.
"""

# 1 Create the sequential orchestrator
expense_pipeline_agent = LlmAgent(
    name="ExpensePipelineAgent",
    model=os.environ.get("GOOGLE_GENAI_MODEL"),
    description=(
        """Ingests expense receipts, performs OCR and data extraction, 
        aggregates and analyzes historical spending for the user, 
        and delegates categorization, reporting, and summarization to specialized sub-agents."""
    ),
    planner=PlanReActPlanner(),
    sub_agents=[
        ocr_agent,            # Step 1: parse the image
        data_agent,           # Step 2: fetch historical data for the user
        categorizer_agent,    # Step 3: assign categories
        reporter_agent,       # Step 4: generate detailed reports
        summarizer_agent,     # Step 5: produce a human‐friendly summary
    ],
    # instruction=prompt.EXPENSE_COORDINATOR_PROMPT,
    instruction=PIPELINE_INSTRUCTION,
    output_key="final_report",
)

root_agent = expense_pipeline_agent