from datetime import date
from app.storage import load_budget, save_budget
from app.storage import load_expenses

budget = load_budget()


def set_budget():
    global budget

    try:
        amount = float(input("Enter your budget: ₹"))
    except ValueError:
        print("Enter a valid number")
        return

    if amount <= 0:
        print("Budget must be greater than zero")
        return

    budget = amount
    save_budget(budget)

    print(f"Budget set to ₹{budget:.2f}")


def check_budget():
    expenses = load_expenses()
    current_month = date.today().strftime("%Y-%m")

    total = sum(
        expense["amount"]
        for expense in expenses
        if expense.get("date", "").startswith(current_month)
    )

    print(f"Monthly budget: ₹{budget:.2f}")
    print(f"Current month expenses: ₹{total:.2f}")

    if total > budget:
        print("Warning: You exceeded your budget!")
    else:
        print(f"Remaining budget: ₹{budget - total:.2f}")