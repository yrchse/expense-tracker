import json
from app.database import get_connection, create_table

# Read expenses from JSON
with open("data/expenses.json", "r") as file:
    expenses = json.load(file)

# Create table and connect
create_table()
connection = get_connection()
cursor = connection.cursor()

# Check if database is empty
cursor.execute("SELECT COUNT(*) FROM expenses")
count = cursor.fetchone()[0]

if count == 0:
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
    print(f"Successfully migrated {len(expenses)} expenses!")
else:
    print("Database already has records. Migration skipped.")

connection.close()