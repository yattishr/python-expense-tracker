import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# Get the absolute path of the current script (db_utils.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the project root by going up four directories
# from .../tools/ -> .../data_agent/ -> .../sub_agents/ -> .../expense_tracker/ -> project root
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))

# Construct the absolute path to the database file
DB_PATH = os.path.join(project_root, 'expenses.db')

def get_expenses_for_user(user_id, months=2, db_path=DB_PATH):
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
        SELECT date, category, amount
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC
        """
        
        # Log the query execution        
        logger.info(f"Executing query for user_id: {user_id} with months: {months}")
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        expenses = [
            {"date": row[0], "category": row[1], "amount": row[2]}
            for row in rows
        ]
        logger.info(f"Retrieved {len(expenses)} expenses for user_id: {user_id}")        
        return expenses
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return [] # Or raise a more specific exception
    finally:
        if conn:
            conn.close()