"""Expense_Tracker: End-to-end expense receipt ingestion and management, encompassing OCR parsing, category assignment, financial reporting, and concise summary generation."""

from google.adk.agents import SequentialAgent # This line is correct now

from .sub_agents.categorizer_agent import categorizer_agent
from .sub_agents.reporter_agent import reporter_agent
from .sub_agents.summarizer_agent import summarizer_agent
from .sub_agents.ocr_agent.agent import ocr_agent
from .sub_agents.data_agent.agent import data_agent
from .sub_agents.ingestion_agent.agent import ingestion_agent

# 1 Create the sequential orchestrator
expense_pipeline_agent = SequentialAgent(
    name="ExpensePipelineAgent",
    sub_agents=[
        ocr_agent,            # Step 1: parse the image        
        categorizer_agent,    # Step 2: assign categories
        ingestion_agent,      # Step 3: store the categorized data in the database
        data_agent,           # Step 4: fetch historical data for the user
        reporter_agent,       # Step 5: generate detailed reports
        summarizer_agent,     # Step 6: produce a human‐friendly summary
    ],
    description="Executes OCR → Categorize → Ingestion Agent → Data Agent → Report → Summarize in one seamless pipeline."
)

root_agent = expense_pipeline_agent