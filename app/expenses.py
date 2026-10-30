
from datetime import date, datetime
import csv
import matplotlib.pyplot as plt

from app.storage import load_expenses, save_expenses

expenses = load_expenses()


def add_expense():
    name = input("Enter expense name: ").strip()

    if not name:
        print("Expense name cannot be empty")
        return

    try:
        amount = float(input("Enter expense amount: "))
        if amount <= 0:
            print("Amount must be greater than zero")
            return
    except ValueError:
        print("Enter a valid amount")
        return

    category = input("Enter category: ").strip().title()

    if not category:
        print("Category cannot be empty")
        return

    expense = {
        "name": name,
        "amount": amount,
        "category": category,
        "date": date.today().isoformat()
    }

    expenses.append(expense)
    save_expenses(expenses)
    print("Expense added successfully")


def view_expenses():
    if not expenses:
        print("No expenses found")
        return

    for i, expense in enumerate(expenses, start=1):
        print(
            f'{i}. {expense["name"]} - ₹{expense["amount"]:.2f} '
            f'- {expense.get("category", "Other")} '
            f'- {expense.get("date", "Date unavailable")}'
        )


def show_total():
    total = sum(expense["amount"] for expense in expenses)
    print(f"Total expenses: ₹{total:.2f}")


def delete_expense():
    view_expenses()

    if not expenses:
        return

    try:
        number = int(input("Enter expense number to delete: "))
    except ValueError:
        print("Enter a valid number")
        return

    if number < 1 or number > len(expenses):
        print("Invalid expense number")
        return

    removed = expenses.pop(number - 1)
    save_expenses(expenses)
    print(f'Deleted: {removed["name"]}')


def edit_expense():
    view_expenses()

    if not expenses:
        return

    try:
        number = int(input("Enter expense number to edit: "))
    except ValueError:
        print("Enter a valid number")
        return

    if number < 1 or number > len(expenses):
        print("Invalid expense number")
        return

    expense = expenses[number - 1]

    name = input(f'New name ({expense["name"]}): ').strip()
    amount = input(f'New amount ({expense["amount"]}): ').strip()
    category = input(
        f'New category ({expense.get("category", "Other")}): '
    ).strip()

    if name:
        expense["name"] = name

    if amount:
        try:
            new_amount = float(amount)
            if new_amount <= 0:
                print("Amount must be greater than zero")
                return
            expense["amount"] = new_amount
        except ValueError:
            print("Invalid amount")
            return

    if category:
        expense["category"] = category.title()

    save_expenses(expenses)
    print("Expense updated successfully!")


def category_summary():
    if not expenses:
        print("No expenses found")
        return

    totals = {}

    for expense in expenses:
        category = expense.get("category", "Other")
        totals[category] = totals.get(category, 0) + expense["amount"]

    print("\n-- Category Summary --")

    for category, amount in totals.items():
        print(f"{category}: ₹{amount:.2f}")


def search_expenses():
    keyword = input("Search by name or category: ").strip().lower()

    if not keyword:
        print("Enter a search term")
        return

    results = [
        expense for expense in expenses
        if keyword in expense["name"].lower()
        or keyword in expense.get("category", "Other").lower()
    ]

    if not results:
        print("No matching expenses found")
        return

    for expense in results:
        print(
            f'{expense["name"]} - ₹{expense["amount"]:.2f} '
            f'- {expense.get("category", "Other")}'
        )


def monthly_report():
    month = input("Enter month (YYYY-MM): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format")
        return

    monthly_expenses = [
        expense for expense in expenses
        if expense.get("date", "").startswith(month)
    ]

    if not monthly_expenses:
        print("No expenses for this month")
        return

    total = sum(e["amount"] for e in monthly_expenses)
    print(f"Total spending for {month}: ₹{total:.2f}")


def sort_expenses():
    print("1. Sort by amount")
    print("2. Sort by date")

    choice = input("Choose sorting option: ")

    if choice == "1":
        sorted_expenses = sorted(expenses, key=lambda x: x["amount"])
    elif choice == "2":
        sorted_expenses = sorted(
            expenses, key=lambda x: x.get("date", "")
        )
    else:
        print("Invalid choice")
        return

    for expense in sorted_expenses:
        print(expense)


def export_csv():
    with open("expenses.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Amount", "Category", "Date"])

        for expense in expenses:
            writer.writerow([
                expense["name"],
                expense["amount"],
                expense.get("category", "Other"),
                expense.get("date", "Unknown")
            ])

    print("Expenses exported successfully!")


def show_chart():
    if not expenses:
        print("No expenses to display")
        return

    categories = {}

    for expense in expenses:
        category = expense.get("category", "Other")
        categories[category] = (
            categories.get(category, 0) + expense["amount"]
        )

    plt.bar(categories.keys(), categories.values())
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.tight_layout()
    plt.show()
