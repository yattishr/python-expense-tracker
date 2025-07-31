# tools/ingestion_tool.py
from datetime import datetime
import json
import logging
from google.adk.tools import ToolContext
from typing import List, Optional
from typing import Dict, Any
from ...data_agent.tools.db_utils import insert_expense_for_user
from ...models import CategorizedItems, Item

logger = logging.getLogger(__name__)

async def ingestion_tool(categorized_items: CategorizedItems, user_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Parses categorized JSON items and inserts them into the database.
    
    Args:
        categorized_items (CategorizedItems): Pydantic model containing the categorized line items.
        user_id (str): The ID of the user.
        tool_context (ToolContext): The context for the tool execution.

    Returns:
        A dictionary indicating the status of the insertion.
    """

    resolved_user_id = "streamlit-user-1" 
    logger.info("Starting ingestion for user: %s", resolved_user_id)

    items: List[Item] = categorized_items.items

    if not items:
        logger.warning("No items found in categorized JSON")
        return {"status": "failure", "message": "No items to ingest"}
    
    insertion_success = True
    for item in items:
        # Now we can access item properties directly from the validated object
        success = insert_expense_for_user(
            user_id=resolved_user_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            category=item.category.value,
            amount=item.line_total
        )
        if not success:
            insertion_success = False
    
    if insertion_success:
        logger.info("Successfully ingested all categorized expenses for user: %s", resolved_user_id)
        return {"status": "success", "message": "All categorized items ingested successfully"}
    else:
        logger.error("Failed to insert some expenses into the database")
        return {"status": "failure", "message": "Some expenses failed to ingest"}
