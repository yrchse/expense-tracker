
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a separate SQLite database for every test
    test_db = tmp_path / "test_expense_tracker.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.create_tables()

    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client, username):
    password = "TestPassword123!"

    register = client.post("/register", json={
        "username": username,
        "password": password
    })

    assert register.status_code == 201

    login = client.post("/login", data={
        "username": username,
        "password": password
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_expense(client, headers, name="Lunch"):
    response = client.post(
        "/expenses",
        headers=headers,
        json={
            "name": name,
            "amount": 150,
            "category": "Food",
            "date": date.today().isoformat()
        }
    )

    assert response.status_code == 201

    return response.json()["id"]


# TEST 1: Customer registration and login
def test_customer_login(client):
    headers = register_and_login(client, "rahul")

    response = client.get("/profile", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "rahul"


# TEST 2: Unauthenticated users are denied
def test_expenses_require_login(client):
    response = client.get("/expenses")

    assert response.status_code == 401


# TEST 3: Customers see only their expenses
def test_expense_isolation(client):
    rahul = register_and_login(client, "rahul")
    priya = register_and_login(client, "priya")

    create_expense(client, rahul, "Rahul Lunch")
    create_expense(client, priya, "Priya Coffee")

    rahul_expenses = client.get(
        "/expenses", headers=rahul
    ).json()

    priya_expenses = client.get(
        "/expenses", headers=priya
    ).json()

    assert len(rahul_expenses) == 1
    assert len(priya_expenses) == 1

    assert rahul_expenses[0]["name"] == "Rahul Lunch"
    assert priya_expenses[0]["name"] == "Priya Coffee"


# TEST 4: Customer cannot view another user's expense
def test_cross_user_get_denied(client):
    rahul = register_and_login(client, "rahul")
    priya = register_and_login(client, "priya")

    expense_id = create_expense(client, priya)

    response = client.get(
        f"/expenses/{expense_id}",
        headers=rahul
    )

    assert response.status_code == 404


# TEST 5: Customer cannot update another user's expense
def test_cross_user_update_denied(client):
    rahul = register_and_login(client, "rahul")
    priya = register_and_login(client, "priya")

    expense_id = create_expense(client, priya)

    response = client.put(
        f"/expenses/{expense_id}",
        headers=rahul,
        json={
            "name": "Changed Expense",
            "amount": 999,
            "category": "Other",
            "date": date.today().isoformat()
        }
    )

    assert response.status_code == 404

    original = client.get(
        f"/expenses/{expense_id}",
        headers=priya
    )

    assert original.json()["name"] == "Lunch"


# TEST 6: Customer cannot delete another user's expense
def test_cross_user_delete_denied(client):
    rahul = register_and_login(client, "rahul")
    priya = register_and_login(client, "priya")

    expense_id = create_expense(client, priya)

    response = client.delete(
        f"/expenses/{expense_id}",
        headers=rahul
    )

    assert response.status_code == 404

    original = client.get(
        f"/expenses/{expense_id}",
        headers=priya
    )

    assert original.status_code == 200


# TEST 7: Customer can update and delete own expense
def test_own_expense_crud(client):
    rahul = register_and_login(client, "rahul")
    expense_id = create_expense(client, rahul)

    updated = client.put(
        f"/expenses/{expense_id}",
        headers=rahul,
        json={
            "name": "Dinner",
            "amount": 250,
            "category": "Food",
            "date": date.today().isoformat()
        }
    )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Dinner"

    deleted = client.delete(
        f"/expenses/{expense_id}",
        headers=rahul
    )

    assert deleted.status_code == 200

    check = client.get(
        f"/expenses/{expense_id}",
        headers=rahul
    )

    assert check.status_code == 404


# TEST 8: Each customer has a separate budget
def test_budget_isolation(client):
    rahul = register_and_login(client, "rahul")
    priya = register_and_login(client, "priya")

    r = client.put(
        "/budget",
        headers=rahul,
        json={"amount": 10000}
    )

    p = client.put(
        "/budget",
        headers=priya,
        json={"amount": 15000}
    )

    assert r.status_code == 200
    assert p.status_code == 200

    rahul_budget = client.get(
        "/budget", headers=rahul
    ).json()

    priya_budget = client.get(
        "/budget", headers=priya
    ).json()

    assert rahul_budget["monthly_budget"] == 10000
    assert priya_budget["monthly_budget"] == 15000


# TEST 9: Monthly budget calculation
def test_monthly_budget_calculation(client):
    rahul = register_and_login(client, "rahul")

    client.put(
        "/budget",
        headers=rahul,
        json={"amount": 1000}
    )

    create_expense(client, rahul)

    response = client.get("/budget", headers=rahul)

    assert response.status_code == 200
    assert response.json()["spent"] == 150
    assert response.json()["remaining"] == 850
    assert response.json()["exceeded"] is False

# TEST 10: Search
def test_search_expenses(client):
    rahul = register_and_login(client, "rahul")

    create_expense(client, rahul, "Lunch")
    create_expense(client, rahul, "Coffee")

    response = client.get(
        "/expenses?search=Lunch",
        headers=rahul
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Lunch"


# TEST 11: Pagination
def test_pagination(client):
    rahul = register_and_login(client, "rahul")

    for i in range(5):
        create_expense(client, rahul, f"Expense {i}")

    response = client.get(
        "/expenses?skip=0&limit=2",
        headers=rahul
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# TEST 12: Monthly report
def test_monthly_report(client):
    rahul = register_and_login(client, "rahul")
    create_expense(client, rahul)

    month = date.today().strftime("%Y-%m")

    response = client.get(
        f"/expenses/reports/monthly?month={month}",
        headers=rahul
    )

    assert response.status_code == 200
    assert response.json()["total_expenses"] == 1
    assert response.json()["total_spent"] == 150


# TEST 13: Category summary and CSV
def test_summary_and_csv(client):
    rahul = register_and_login(client, "rahul")
    create_expense(client, rahul)

    summary = client.get(
        "/expenses/summary/categories",
        headers=rahul
    )

    assert summary.status_code == 200
    assert summary.json()[0]["category"] == "Food"
    assert summary.json()[0]["total"] == 150

    csv_response = client.get(
        "/expenses/export/csv",
        headers=rahul
    )

    assert csv_response.status_code == 200
    assert "Lunch" in csv_response.text
