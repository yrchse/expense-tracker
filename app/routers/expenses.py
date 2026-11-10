import csv
import io
import re

from datetime import date
from fastapi import Query
from fastapi.responses import StreamingResponse

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.auth import get_current_user
from app.schemas import ExpenseCreate, ExpenseResponse


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# 1. GET ALL EXPENSES

@router.get("", response_model=list[ExpenseResponse])
def get_expenses(
    current_user: dict = Depends(get_current_user),
    search: str | None = None,
    sort_by: str = Query("id", pattern="^(id|name|amount|date)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    connection = get_connection()

    try:
        sql = "SELECT * FROM expenses WHERE user_id = ?"
        parameters = [current_user["id"]]

        if search:
            sql += " AND (name LIKE ? OR category LIKE ?)"
            keyword = f"%{search}%"
            parameters.extend([keyword, keyword])

        # Safe because sort_by and order are restricted above
        sql += f" ORDER BY {sort_by} {order.upper()}"
        sql += " LIMIT ? OFFSET ?"

        parameters.extend([limit, skip])

        rows = connection.execute(
            sql, parameters
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# 2. GET ONE EXPENSE
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        expense = connection.execute(
            """
            SELECT * FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, current_user["id"])
        ).fetchone()

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        return dict(expense)

    finally:
        connection.close()


# 3. CREATE EXPENSE
@router.post(
    "",
    status_code=201,
    response_model=ExpenseResponse
)
def add_expense(
    expense: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO expenses
            (user_id, name, amount, category, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                current_user["id"],
                expense.name,
                expense.amount,
                expense.category,
                expense.date.isoformat()
            )
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "user_id": current_user["id"],
            **expense.model_dump()
        }

    finally:
        connection.close()


# 4. UPDATE EXPENSE
@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE expenses
            SET name = ?, amount = ?, category = ?, date = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                expense.name,
                expense.amount,
                expense.category,
                expense.date.isoformat(),
                expense_id,
                current_user["id"]
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        connection.commit()

        return {
            "id": expense_id,
            "user_id": current_user["id"],
            **expense.model_dump()
        }

    finally:
        connection.close()


# 5. DELETE EXPENSE
@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, current_user["id"])
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        connection.commit()

        return {
            "message": "Expense deleted successfully"
        }

    finally:
        connection.close()

@router.get("/summary/categories")
def category_summary(
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT category, ROUND(SUM(amount), 2) AS total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY category
            """,
            (current_user["id"],)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()

@router.get("/reports/monthly")
def monthly_report(
    month: str = Query(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*) AS total_expenses,
                   COALESCE(SUM(amount), 0) AS total_spent
            FROM expenses
            WHERE user_id = ?
            AND substr(date, 1, 7) = ?
            """,
            (current_user["id"], month)
        ).fetchone()

        return {
            "month": month,
            "total_expenses": result["total_expenses"],
            "total_spent": round(result["total_spent"], 2)
        }

    finally:
        connection.close()

@router.get("/export/csv")
def export_expenses(
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT name, amount, category, date
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC
            """,
            (current_user["id"],)
        ).fetchall()
    finally:
        connection.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Name", "Amount", "Category", "Date"])

    for row in rows:
        writer.writerow([
            row["name"],
            row["amount"],
            row["category"],
            row["date"]
        ])

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="expenses.csv"'
        }
    )