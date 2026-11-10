from datetime import date
from pydantic import BaseModel, Field


# Customer registration
class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


# Creating or updating expenses
class ExpenseCreate(BaseModel):
    name: str = Field(min_length=2)
    amount: float = Field(gt=0)
    category: str = Field(min_length=2)
    date: date


# Expense API response
class ExpenseResponse(ExpenseCreate):
    id: int
    user_id: int


# Customer budget
class BudgetCreate(BaseModel):
    amount: float = Field(gt=0)