# tools/data_agent_tool.py

from google.adk.tools import ToolContext
from db_utils import get_expenses_for_user
from collections import defaultdict
from datetime import datetime
from google.adk.tools import Tool, FunctionTool

async def data_agent_tool(user_id: str, months: int = 2, tool_context: ToolContext = None):
    """
    Aggregates spend per category for current and previous periods for a given user.
    Returns history for use by the Insights Agent.
    """
    expenses = get_expenses_for_user(user_id, months)
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
    return {"history": history}

data_agent_tool = Tool(
    func=data_agent_tool,
    name="data_agent_tool",
    description="Returns spend per category for current and previous months for the user.",
    args_schema={
        "user_id": {"type": "string", "description": "User ID"},
        "months": {"type": "integer", "description": "Number of months to include"}
    }
)
