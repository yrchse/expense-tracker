
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from app.database import get_connection
from app.schemas import UserCreate


# Router handles authentication endpoints
router = APIRouter(tags=["Authentication"])

# Password hashing
password_hash = PasswordHash.recommended()

# Load secret key from .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY must contain at least 32 characters")

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# CREATE JWT TOKEN
def create_access_token(user_id: int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expiration
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# VERIFY LOGGED-IN CUSTOMER
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    connection = get_connection()

    try:
        user = connection.execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return dict(user)

    finally:
        connection.close()


# REGISTER CUSTOMER
@router.post("/register", status_code=201)
def register_user(user: UserCreate):
    hashed_password = password_hash.hash(user.password)

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (user.username, hashed_password)
        )

        connection.commit()

        return {
            "message": "Customer registered successfully",
            "user_id": cursor.lastrowid,
            "username": user.username
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    finally:
        connection.close()


# CUSTOMER LOGIN
@router.post("/login")
def login_user(form: OAuth2PasswordRequestForm = Depends()):
    connection = get_connection()

    try:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (form.username,)
        ).fetchone()

        if user is None or not password_hash.verify(
            form.password,
            user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        token = create_access_token(user["id"])

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        connection.close()


# PROTECTED PROFILE
@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["id"],
        "username": current_user["username"]
    }
