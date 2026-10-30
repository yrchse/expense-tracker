
import json
from pathlib import Path

# Project data folder
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EXPENSES_FILE = DATA_DIR / "expenses.json"
BUDGET_FILE = DATA_DIR / "budget.json"


def save_expenses(expenses):
    DATA_DIR.mkdir(exist_ok=True)

    with open(EXPENSES_FILE, "w") as file:
        json.dump(expenses, file, indent=4)


def load_expenses():
    DATA_DIR.mkdir(exist_ok=True)

    try:
        with open(EXPENSES_FILE, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        save_expenses([])
        return []


def save_budget(budget):
    DATA_DIR.mkdir(exist_ok=True)

    with open(BUDGET_FILE, "w") as file:
        json.dump(budget, file, indent=4)


def load_budget():
    DATA_DIR.mkdir(exist_ok=True)

    try:
        with open(BUDGET_FILE, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        default_budget = 50000
        save_budget(default_budget)
        return default_budget
