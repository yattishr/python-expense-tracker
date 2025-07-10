# test_data_agent.py

import os
import sqlite3
from datetime import datetime, timedelta
import asyncio

# 1) Spin up a fresh SQLite file with fake expense data
print("Setting up test database...")
DB_PATH = "test_spend.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    category TEXT,
    amount REAL,
    date TEXT
)
""")
print("Created expenses table....")

now = datetime.utcnow()
for i in range(1, 4):
    date = (now - timedelta(days=30*i)).strftime("%Y-%m-%d")
    for cat, amt in [("Groceries", 100 + i * 20),
                     ("Dining",    50  + i * 15),
                     ("Travel",    75  + i * 10)]:
        cur.execute(
            "INSERT INTO expenses (user_id, category, amount, date) VALUES (?,?,?,?)",
            ("test-user", cat, amt, date)
        )
conn.commit()
conn.close()

print("Inserted test data into expenses table...")

# 2) Make sure your db_utils points at our test file.
#    Adjust this line to match how get_expenses_for_user reads the DB_URL
os.environ["EXPENSE_DB_URL"] = f"sqlite:///{DB_PATH}"

# 3) Import your tool
from tools.data_agent_tool import data_agent_tool  # <-- adjust path if needed

# 4) Drive the async function and print its output
async def run_data_agent():
    print("Running data_agent_tool...")
    # Note: data_agent_tool is a Tool instance; .func is the underlying async fn
    return await data_agent_tool.func(user_id="test-user", months=2, tool_context=None)

if __name__ == "__main__":
    report = asyncio.get_event_loop().run_until_complete(run_data_agent())
    print("=== Data Agent History Report ===")
    print(report)