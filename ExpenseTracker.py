from datetime import date,datetime
import json
import csv
import matplotlib.pyplot as plt

def save_budget():
    with open("budget.json", "w") as file:
        json.dump(budget, file)

def load_budget():
    global budget
    try:
        with open("budget.json", "r") as file:
            budget = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        budget = 5000
        save_budget()


def save_expenses():
    with open("expenses.json", "w") as file:
        json.dump(expenses, file)

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

def delete_expense():
    view_expenses()

    if not expenses:
        return
    
    try:
        number = int(input("Enter the expense number to delete: "))
    except ValueError:
        print("Enter a Valid number")
        return

    if number < 1 or number > len(expenses):
        print("Invalid expense number")
        return
    else:
        removed = expenses.pop(number - 1)
        save_expenses()
        print(f'Deleted: {removed["name"]}')


def edit_expense():
    view_expenses()

    if not expenses:
        return

    try:
        number = int(input("Enter expense number to edit: "))
    except ValueError:
        print("Please enter a valid number")
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

    save_expenses()
    print("Expense updated successfully!")


def search_expenses():
    keyword = input("Search by name or category: ").strip().lower()

    if not keyword:
        print("Please enter a search term")
        return

    results = [
        expense for expense in expenses
        if keyword in expense["name"].lower()
        or keyword in expense.get("category", "Other").lower()
    ]

    if not results:
        print("No matching expenses found")
        return

    print("\n-- Search Results --")
    for expense in results:
        print(
            f'{expense["name"]} - ₹{expense["amount"]:.2f} '
            f'- {expense.get("category", "Other")} '
            f'- {expense.get("date", "Date unavailable")}'
        )

def set_budget():
    global budget

    try:
        amount = float(input("Enter your budget: ₹"))
    except ValueError:
        print("Please enter a valid number")
        return

    if amount <= 0:
        print("Budget must be greater than zero")
        return

    budget = amount
    save_budget()
    print(f"Budget set to ₹{budget:.2f}")


def check_budget():
    total = sum(expense["amount"] for expense in expenses)

    print(f"Monthly budget: ₹{budget:.2f}")
    print(f"Total expenses: ₹{total:.2f}")

    if total > budget:
        print("Warning: You exceeded your budget!")
    else:
        remaining = budget - total
        print(f"Remaining budget: ₹{remaining:.2f}")

    
def monthly_report():
    month = input("Enter month (YYYY-MM): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Use YYYY-MM, e.g. 2026-10")
        return

    monthly_expenses = [
        expense for expense in expenses
        if expense.get("date", "").startswith(month)
    ]

    if not monthly_expenses:
        print("No expenses for this month")
        return

    total = sum(expense["amount"] for expense in monthly_expenses)
    categories = {}

    print(f"\n-- Report for {month} --")

    for expense in monthly_expenses:
        print(f'{expense["name"]} - ₹{expense["amount"]:.2f}')

        category = expense.get("category", "Other")
        categories[category] = categories.get(category, 0) + expense["amount"]

    print(f"\nTotal spending: ₹{total:.2f}")
    print("\n-- Category Totals --")

    for category, amount in categories.items():
        print(f"{category}: ₹{amount:.2f}")

    

def load_expenses():
    global expenses
    try:
        with open("expenses.json", "r") as file:
            expenses = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        expenses = []
        save_expenses()

def add_expense():
    name = input("Enter the expense name: ").strip()

    if not name:
        print("Expense name cannot be empty")
        return

    try:
        amount = float(input("Enter the expense amount: "))
    except ValueError:
        print("Please enter a valid number")
        return

    if amount <= 0:
        print("Amount must be greater than zero")
        return

    category = input("Enter category (Food/Travel/Shopping/Other): ").strip().title()

    if not category:
        print("Category cannot be empty")
        return

    expense_date = date.today().isoformat()
    
    expense = {"name": name,
                "amount": amount,
                "category": category,
                "date": expense_date
            }
    expenses.append(expense)
    save_expenses()
    print("Expense added successfully")

def view_expenses():
    if not expenses:
        print("No expenses found")
        return
    
    for i,expense in enumerate(expenses,start=1):
        print(
    f'{i}. {expense["name"]} - ₹{expense["amount"]:.2f} '
    f'- {expense.get("category", "Other")} '
    f'- {expense.get("date", "Date unavailable")}'
)
    

def show_total():
    total = 0 
    for expense in expenses:
        total += (expense['amount'])
    print(total)

def sort_expenses():

    print("1. Sort by amount")
    print("2. Sort by date")

    choice = input("Choose sorting option: ")

    if choice == "1":
        sorted_expenses = sorted(
            expenses, key=lambda x: x["amount"]
        )
    elif choice == "2":
        sorted_expenses = sorted(
            expenses, key=lambda x: x.get("date", "")
        )
    else:
        print("Invalid choice")
        return

    for expense in sorted_expenses:
        print(
            f'{expense["name"]} - ₹{expense["amount"]:.2f} '
            f'- {expense.get("date", "Date unavailable")}'
        )

load_expenses()
load_budget()

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

    print("Expenses exported to expenses.csv successfully!")

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

while True:
    print("\n--Expense Tracker")
    print("1.Add Expense")
    print("2.View Expense")
    print("3.Show Total")
    print("4.Delete expense")
    print("5.Edit expense")
    print("6.Category Summary")
    print("7.Set Budget")
    print("8.Check Budget")
    print("9.Monthly Report") 
    print("10.Search Expenses")
    print("11.Exit")
    print("12.Sort Expenses")
    print("13.Export Expenses to CSV")
    print("14.Show Spending Chart")


    choice =input("Enter your choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        show_total()

    elif choice == "4":
        delete_expense()

    elif choice == "5":
        edit_expense()

    elif choice == "6":
        category_summary()

    elif choice == "7":
        set_budget()
    
    elif choice == "8":
        check_budget()

    elif choice == "9":
        monthly_report()
    
    elif choice == "10":
        search_expenses()

    elif choice == "12":
        sort_expenses()

    elif choice == "13":
        export_csv()
        
    elif choice == "14":
        show_chart()

    elif choice == "11":
        print("Exited")
        break

