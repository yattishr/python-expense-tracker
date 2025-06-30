import sqlite3

def get_expenses_for_user(user_id, months=2, db_path='expenses.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
    SELECT date, category, amount
    FROM expenses
    WHERE user_id = ?
    ORDER BY date DESC
    """

    cursor.execute(query, (user_id,))    
    rows = cursor.fetchall()
    conn.close()
    expenses = [
        {"date": row[0], "category": row[1], "amount": row[2]}
        for row in rows
    ]
    return expenses