
from datetime import date, timedelta

from app.multiuser_database import get_connection

# 5 customers with 10 sample expenses each
sample_expenses = {
    "rahul": [
        ("Lunch", 150, "Food"),
        ("Petrol", 500, "Transport"),
        ("Groceries", 1200, "Shopping"),
        ("Movie", 250, "Entertainment"),
        ("Breakfast", 80, "Food"),
        ("Internet", 699, "Bills"),
        ("Bus Ticket", 120, "Transport"),
        ("Medicine", 350, "Health"),
        ("Dinner", 300, "Food"),
        ("Shoes", 1800, "Shopping"),
    ],
    "priya": [
        ("Coffee", 100, "Food"),
        ("Dress", 1500, "Shopping"),
        ("Taxi", 250, "Transport"),
        ("Lunch", 200, "Food"),
        ("Books", 600, "Education"),
        ("Groceries", 950, "Shopping"),
        ("Movie", 300, "Entertainment"),
        ("Mobile Recharge", 299, "Bills"),
        ("Snacks", 120, "Food"),
        ("Medicine", 180, "Health"),
    ],
    "arjun": [
        ("Breakfast", 90, "Food"),
        ("Petrol", 800, "Transport"),
        ("Gym", 1200, "Fitness"),
        ("Lunch", 180, "Food"),
        ("Internet", 799, "Bills"),
        ("Groceries", 1100, "Shopping"),
        ("Movie", 250, "Entertainment"),
        ("Bus Pass", 600, "Transport"),
        ("Dinner", 280, "Food"),
        ("Notebook", 150, "Education"),
    ],
    "sneha": [
        ("Coffee", 150, "Food"),
        ("Shopping", 2000, "Shopping"),
        ("Taxi", 350, "Transport"),
        ("Lunch", 220, "Food"),
        ("Books", 800, "Education"),
        ("Electricity", 1500, "Bills"),
        ("Groceries", 1300, "Shopping"),
        ("Movie", 350, "Entertainment"),
        ("Dinner", 400, "Food"),
        ("Medicine", 250, "Health"),
    ],
    "kiran": [
        ("Breakfast", 70, "Food"),
        ("Petrol", 400, "Transport"),
        ("Lunch", 160, "Food"),
        ("Groceries", 850, "Shopping"),
        ("Internet", 599, "Bills"),
        ("Movie", 200, "Entertainment"),
        ("Snacks", 100, "Food"),
        ("Bus Ticket", 90, "Transport"),
        ("Dinner", 250, "Food"),
        ("Clothes", 1200, "Shopping"),
    ],
}


def seed_expenses():
    connection = get_connection()

    try:
        inserted_count = 0

        for username, expenses in sample_expenses.items():

            # Find the actual user ID
            user = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if user is None:
                print(f"Skipping {username}: user not registered")
                continue

            user_id = user["id"]

            # Avoid duplicating data if script runs again
            existing = connection.execute(
                "SELECT COUNT(*) FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]

            if existing > 0:
                print(f"Skipping {username}: already has expenses")
                continue

            for index, (name, amount, category) in enumerate(expenses):

                expense_date = (
                    date.today() - timedelta(days=index)
                ).isoformat()

                connection.execute(
                    """
                    INSERT INTO expenses
                    (user_id, name, amount, category, date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, name, amount, category, expense_date)
                )

                inserted_count += 1

            print(f"Added 10 expenses for {username}")

        connection.commit()
        print(f"\nTotal new expenses inserted: {inserted_count}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_expenses()
