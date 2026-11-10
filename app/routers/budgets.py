
from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.auth import get_current_user
from app.schemas import BudgetCreate


router = APIRouter(
    prefix="/budget",
    tags=["Budget"]
)


# SET OR UPDATE BUDGET
@router.put("")
def set_budget(
    budget: BudgetCreate,
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO budgets (user_id, amount)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET amount = excluded.amount
            """,
            (current_user["id"], budget.amount)
        )

        connection.commit()

        return {
            "message": "Budget saved successfully",
            "monthly_budget": budget.amount
        }

    finally:
        connection.close()


# CHECK MONTHLY BUDGET
@router.get("")
def check_budget(
    current_user: dict = Depends(get_current_user)
):
    connection = get_connection()

    try:
        budget = connection.execute(
            """
            SELECT amount
            FROM budgets
            WHERE user_id = ?
            """,
            (current_user["id"],)
        ).fetchone()

        if budget is None:
            raise HTTPException(
                status_code=404,
                detail="Budget not set"
            )

        current_month = date.today().strftime("%Y-%m")

        result = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ?
            AND substr(date, 1, 7) = ?
            """,
            (current_user["id"], current_month)
        ).fetchone()

        spent = result[0]
        budget_amount = budget["amount"]

        return {
            "monthly_budget": budget_amount,
            "spent": spent,
            "remaining": round(budget_amount - spent, 2),
            "exceeded": spent > budget_amount
        }

    finally:
        connection.close()
