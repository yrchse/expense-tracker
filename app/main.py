
from fastapi import FastAPI

from app.auth import router as auth_router
from app.routers.expenses import router as expenses_router
from app.routers.budgets import router as budget_router
from app.database import create_tables

app = FastAPI(
    title="Expense Tracker API",
    description="Multi-user expense management backend",
    version="1.0.0"
)


# Initialize database tables
create_tables()


# Connect different API routers
app.include_router(auth_router)
app.include_router(expenses_router)
app.include_router(budget_router)


@app.get("/")
def home():
    return {
        "message": "Expense Tracker API is running"
    }
