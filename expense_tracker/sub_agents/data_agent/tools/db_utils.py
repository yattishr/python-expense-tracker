import sqlite3

def get_expenses_for_user(user_id, months=2, db_path='expenses.db'):
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
        print(f"Executing query for user_id: {user_id} with months: {months}")
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        expenses = [
            {"date": row[0], "category": row[1], "amount": row[2]}
            for row in rows
        ]
        print(f"Retrieved {len(expenses)} expenses for user_id: {user_id}")
        return expenses
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [] # Or raise a more specific exception
    finally:
        if conn:
            conn.close()