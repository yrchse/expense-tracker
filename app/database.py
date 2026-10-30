import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_FILE = DATA_DIR / "expenses.db"


def get_connection():
    connection = sqlite3.connect(DB_FILE)
    return connection

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

def check_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(tables)
    connection.close()

def check_columns():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(expenses)")
    columns = cursor.fetchall()

    for column in columns:
        print(column)

    connection.close()

def insert_expense():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (name, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, ("Lunch", 150, "Food", "2026-10-30"))

    connection.commit()
    connection.close()
    print("Expense inserted!")


def view_expenses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    for expense in expenses:
        print(expense)

    connection.close()


def update_expense():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?
        WHERE id = ?
    """, (200, 1))

    connection.commit()
    connection.close()
    print("Expense updated!")


def delete_expense():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?", (1,)
    )

    connection.commit()
    connection.close()
    print("Expense deleted!")

if __name__ == "__main__":
    create_table()

    insert_expense()
    view_expenses()

    update_expense()
    view_expenses()

    delete_expense()
    view_expenses()