
import os
from datetime import date
from uuid import uuid4
from urllib.parse import urlsplit, unquote

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app import database
from app.main import app


load_dotenv()


# SET UP SEPARATE POSTGRESQL TEST DATABASE
@pytest.fixture
def client(monkeypatch):
    main_url = os.getenv("DATABASE_URL")
    test_url = os.getenv("TEST_DATABASE_URL")

    if not main_url or not test_url:
        pytest.fail(
            "DATABASE_URL and TEST_DATABASE_URL must be set in .env"
        )

    main_db_name = unquote(urlsplit(main_url).path.lstrip("/"))
    test_db_name = unquote(urlsplit(test_url).path.lstrip("/"))

    # Protect the main application database
    if (
        main_db_name == test_db_name
        or test_db_name != "expense_tracker_test"
    ):
        pytest.fail(
            "Tests must use the separate expense_tracker_test database"
        )

    # Temporarily switch to the test database
    monkeypatch.setenv("DATABASE_URL", test_url)

    database.create_tables()

    # Reset test data before each test
    connection = database.get_connection()

    try:
        connection.execute("""
            TRUNCATE TABLE expenses, budgets, users
            RESTART IDENTITY CASCADE
        """)
        connection.commit()
    finally:
        connection.close()

    with TestClient(app) as test_client:
        yield test_client


# REGISTER AND LOGIN A RANDOM TEST USER
def register_and_login(client):
    username = f"testuser_{uuid4().hex[:12]}"
    password = "TestPassword123!"

    register = client.post(
        "/register",
        json={
            "username": username,
            "password": password
        }
    )

    assert register.status_code == 201

    login = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "username": username,
        "headers": {
            "Authorization": f"Bearer {token}"
        }
    }


# CREATE A TEST EXPENSE
def create_expense(client, user, name="Lunch"):
    response = client.post(
        "/expenses",
        headers=user["headers"],
        json={
            "name": name,
            "amount": 150,
            "category": "Food",
            "date": date.today().isoformat()
        }
    )

    assert response.status_code == 201

    return response.json()["id"]


# TEST 1: REGISTRATION AND LOGIN
def test_customer_login(client):
    user = register_and_login(client)

    response = client.get(
        "/profile",
        headers=user["headers"]
    )

    assert response.status_code == 200
    assert response.json()["username"] == user["username"]


# TEST 2: LOGIN REQUIRED
def test_expenses_require_login(client):
    response = client.get("/expenses")

    assert response.status_code == 401


# TEST 3: USER EXPENSE ISOLATION
def test_expense_isolation(client):
    user1 = register_and_login(client)
    user2 = register_and_login(client)

    create_expense(client, user1, "User One Lunch")
    create_expense(client, user2, "User Two Coffee")

    expenses1 = client.get(
        "/expenses",
        headers=user1["headers"]
    ).json()

    expenses2 = client.get(
        "/expenses",
        headers=user2["headers"]
    ).json()

    assert len(expenses1) == 1
    assert len(expenses2) == 1

    assert expenses1[0]["name"] == "User One Lunch"
    assert expenses2[0]["name"] == "User Two Coffee"


# TEST 4: CANNOT VIEW ANOTHER USER'S EXPENSE
def test_cross_user_get_denied(client):
    user1 = register_and_login(client)
    user2 = register_and_login(client)

    expense_id = create_expense(client, user2)

    response = client.get(
        f"/expenses/{expense_id}",
        headers=user1["headers"]
    )

    assert response.status_code == 404


# TEST 5: CANNOT UPDATE ANOTHER USER'S EXPENSE
def test_cross_user_update_denied(client):
    user1 = register_and_login(client)
    user2 = register_and_login(client)

    expense_id = create_expense(client, user2)

    response = client.put(
        f"/expenses/{expense_id}",
        headers=user1["headers"],
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
        headers=user2["headers"]
    )

    assert original.status_code == 200
    assert original.json()["name"] == "Lunch"


# TEST 6: CANNOT DELETE ANOTHER USER'S EXPENSE
def test_cross_user_delete_denied(client):
    user1 = register_and_login(client)
    user2 = register_and_login(client)

    expense_id = create_expense(client, user2)

    response = client.delete(
        f"/expenses/{expense_id}",
        headers=user1["headers"]
    )

    assert response.status_code == 404

    original = client.get(
        f"/expenses/{expense_id}",
        headers=user2["headers"]
    )

    assert original.status_code == 200


# TEST 7: UPDATE AND DELETE OWN EXPENSE
def test_own_expense_crud(client):
    user = register_and_login(client)

    expense_id = create_expense(client, user)

    updated = client.put(
        f"/expenses/{expense_id}",
        headers=user["headers"],
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
        headers=user["headers"]
    )

    assert deleted.status_code == 200

    check = client.get(
        f"/expenses/{expense_id}",
        headers=user["headers"]
    )

    assert check.status_code == 404


# TEST 8: SEPARATE BUDGETS FOR EACH USER
def test_budget_isolation(client):
    user1 = register_and_login(client)
    user2 = register_and_login(client)

    response1 = client.put(
        "/budget",
        headers=user1["headers"],
        json={"amount": 10000}
    )

    response2 = client.put(
        "/budget",
        headers=user2["headers"],
        json={"amount": 15000}
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    budget1 = client.get(
        "/budget",
        headers=user1["headers"]
    ).json()

    budget2 = client.get(
        "/budget",
        headers=user2["headers"]
    ).json()

    assert budget1["monthly_budget"] == 10000
    assert budget2["monthly_budget"] == 15000


# TEST 9: MONTHLY BUDGET CALCULATION
def test_monthly_budget_calculation(client):
    user = register_and_login(client)

    response = client.put(
        "/budget",
        headers=user["headers"],
        json={"amount": 1000}
    )

    assert response.status_code == 200

    create_expense(client, user)

    response = client.get(
        "/budget",
        headers=user["headers"]
    )

    assert response.status_code == 200
    assert response.json()["spent"] == 150
    assert response.json()["remaining"] == 850
    assert response.json()["exceeded"] is False


# TEST 10: SEARCH EXPENSES
def test_search_expenses(client):
    user = register_and_login(client)

    create_expense(client, user, "Lunch")
    create_expense(client, user, "Coffee")

    response = client.get(
        "/expenses?search=Lunch",
        headers=user["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Lunch"


# TEST 11: PAGINATION
def test_pagination(client):
    user = register_and_login(client)

    for i in range(5):
        create_expense(client, user, f"Expense {i}")

    response = client.get(
        "/expenses?skip=0&limit=2",
        headers=user["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# TEST 12: MONTHLY REPORT
def test_monthly_report(client):
    user = register_and_login(client)

    create_expense(client, user)

    month = date.today().strftime("%Y-%m")

    response = client.get(
        f"/expenses/reports/monthly?month={month}",
        headers=user["headers"]
    )

    assert response.status_code == 200
    assert response.json()["total_expenses"] == 1
    assert response.json()["total_spent"] == 150


# TEST 13: CATEGORY SUMMARY AND CSV EXPORT
def test_summary_and_csv(client):
    user = register_and_login(client)

    create_expense(client, user)

    summary = client.get(
        "/expenses/summary/categories",
        headers=user["headers"]
    )

    assert summary.status_code == 200
    assert summary.json()[0]["category"] == "Food"
    assert summary.json()[0]["total"] == 150

    csv_response = client.get(
        "/expenses/export/csv",
        headers=user["headers"]
    )

    assert csv_response.status_code == 200
    assert "Lunch" in csv_response.text
