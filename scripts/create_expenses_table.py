import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expenses.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL
)
""")

conn.commit()
conn.close()

print("Table 'expenses' created (if it did not exist).")