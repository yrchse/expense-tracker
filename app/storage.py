
from app.database import get_connection




# Save expenses to SQLite
def save_expenses(expenses):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM expenses")

    for expense in expenses:
        cursor.execute("""
            INSERT INTO expenses (name, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (
            expense["name"],
            expense["amount"],
            expense["category"],
            expense["date"]
        ))

    connection.commit()
    connection.close()


# Load expenses from SQLite
def load_expenses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, amount, category, date
        FROM expenses
    """)

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "name": row[0],
            "amount": row[1],
            "category": row[2],
            "date": row[3]
        }
        for row in rows
    ]


# Save budget to SQLite
def save_budget(budget):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO budget (id, amount)
        VALUES (1, ?)
    """, (budget,))

    connection.commit()
    connection.close()


# Load budget from SQLite
def load_budget():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT amount FROM budget WHERE id = 1")
    result = cursor.fetchone()

    if result is None:
        default_budget = 50000
        save_budget(default_budget)
        connection.close()
        return default_budget

    connection.close()
    return result[0]