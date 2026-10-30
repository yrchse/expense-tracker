
from app.expenses import (
    add_expense,
    view_expenses,
    show_total,
    delete_expense,
    edit_expense,
    category_summary,
    monthly_report,
    search_expenses,
    sort_expenses,
    export_csv,
    show_chart
)

from app.budget import set_budget, check_budget


def main():
    while True:
        print("\n--- EXPENSE TRACKER ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Total")
        print("4. Delete Expense")
        print("5. Edit Expense")
        print("6. Category Summary")
        print("7. Set Budget")
        print("8. Check Budget")
        print("9. Monthly Report")
        print("10. Search Expenses")
        print("11. Exit")
        print("12. Sort Expenses")
        print("13. Export Expenses to CSV")
        print("14. Show Spending Chart")

        choice = input("Enter your choice: ")

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
        elif choice == "11":
            print("Exited")
            break
        elif choice == "12":
            sort_expenses()
        elif choice == "13":
            export_csv()
        elif choice == "14":
            show_chart()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
