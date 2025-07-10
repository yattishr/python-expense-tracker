# tools/data_agent_tool.py
import logging
from google.adk.tools import ToolContext
from .db_utils import get_expenses_for_user
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

async def data_agent_tool(user_id: str, months: int = 2, tool_context: ToolContext = None) -> dict:
    """
    Returns spend per category for current and previous months for the user.

    Args:
        user_id: The ID of the user whose expense history is to be retrieved.
        months: The number of months of expense history to include (default is 2).

    Returns:
        A dictionary containing the aggregated spend history.
    """
    resolved_user_id = user_id

    # implementing the below for TESTING purposes
    # resolved_user_id = "streamlit-user-1"

    if not resolved_user_id and tool_context and tool_context.user_state and "user_id" in tool_context.user_state:
        resolved_user_id = tool_context.user_state["user_id"]

    if not resolved_user_id:
        logger.error("Error: User ID not found in tool argument or ToolContext.")
        return {"error": "User ID is required but was not provided."}

    expenses = get_expenses_for_user(resolved_user_id, months)
    per_month = defaultdict(lambda: defaultdict(float))
    for exp in expenses:
        dt = datetime.strptime(exp["date"], "%Y-%m-%d")
        ym = dt.strftime("%Y-%m")
        per_month[ym][exp["category"]] += float(exp["amount"])

    all_months = sorted(per_month.keys(), reverse=True)
    history = [
        {"month": m, "categories": dict(per_month[m])}
        for m in all_months[:months+1]
    ]
    
    logger.info("Successfully processed history for user: %s", resolved_user_id)
    logger.debug("Sending expense history back to the agent:", history)
    return {"history": history, "status": "success"}
