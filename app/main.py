
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.routers.expenses import router as expenses_router
from app.routers.budgets import router as budget_router
from app.database import create_tables


app = FastAPI(
    title="Expense Tracker API",
    description="Multi-user expense management backend",
    version="1.0.0"
)

# Allowed frontend websites
frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
