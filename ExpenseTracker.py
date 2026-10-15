
import json

def save_expenses():
    with open("expenses.json", "w") as file:
        json.dump(expenses, file)

def load_expenses():
    global expenses
    try:
        with open("expenses.json", "r") as file:
            expenses = json.load(file)
    except FileNotFoundError:
        expenses = []

def add_expense():
    name = input("Enter the expense name: ")
    amount = float(input("Enter the expense amount: "))

    expense = {"name": name, "amount": amount}
    expenses.append(expense)
    save_expenses()
    print("Expense added successfully")

def view_expenses():
    if not expenses:
        print("No expenses found")
        return
    
    for expense in expenses:
        print(f'"Name": {expense["name"]},"Amount": {expense["amount"]}')
    

def show_total():
    total = 0 
    for expense in expenses:
        total += (expense['amount'])
    print(total)


load_expenses()
while True:
    print("\n--Expense Tracker")
    print("1.Add Expense")
    print("2.View Expense")
    print("3.Show Total")
    print("4.Exit")

    choice =input("Enter your choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        show_total()

    elif choice == "4":
        print("exited")
        break

    else:
        print("Invalid")
