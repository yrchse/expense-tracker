
# Expense Tracker

A full-stack expense tracking application built with **React, FastAPI, and PostgreSQL**.

I built this project to practice REST APIs, authentication, database operations, automated testing, and full-stack deployment. Users can track expenses, manage monthly budgets, and view spending reports.

**Live Application:** https://expense-tracker-khaki-eight-17.vercel.app/

**Backend API:** https://expense-tracker-oube.onrender.com/docs

**GitHub Repository:** https://github.com/yrchse/expense-tracker

## Features

- User registration and login with JWT authentication
- Secure password hashing using Argon2
- Separate expenses and budgets for each user
- Add, view, update, and delete expenses
- Search, sorting, and pagination
- Monthly spending reports
- Category-wise expense summaries
- Monthly budget tracking and overspending alerts
- Export expenses to CSV
- Responsive React dashboard

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React, JavaScript, CSS, Vite |
| Backend | Python, FastAPI, Pydantic |
| Database | PostgreSQL |
| Database Hosting | Neon |
| Database Driver | Psycopg 3 |
| Authentication | JWT, Argon2 |
| Testing | Pytest, FastAPI TestClient |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| Version Control | Git, GitHub |

## System Architecture

```text
User's Browser
      |
      v
React Frontend (Vercel)
      |
      | HTTP Requests / JSON Responses
      v
FastAPI Backend (Render)
      |
      | SQL Queries using Psycopg
      v
PostgreSQL Database (Neon)
```

React handles the user interface.

FastAPI processes requests, validates data, and manages authentication.

PostgreSQL stores users, expenses, and budgets.

The frontend communicates with the backend through REST APIs. It never connects directly to the database.

## Project Structure

```text
expense-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       ├── expenses.py
│       └── budgets.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Dashboard.jsx
│   │   ├── App.css
│   │   └── Dashboard.css
│   ├── package.json
│   └── vite.config.js
├── tests/
│   └── test_expense_tracker.py
├── scripts/
│   └── seed_data.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/yrchse/expense-tracker.git
cd expense-tracker
```

### 2. Install Backend Dependencies

```bash
py -m pip install -r requirements.txt
```

On macOS/Linux, use `python3` instead of `py`.

### 3. Configure Environment Variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your_secret_key_at_least_32_characters
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Generate a secure secret key using:

```bash
py -c "import secrets; print(secrets.token_hex(32))"
```

Replace the example values with your own credentials.

Never upload `.env` or database passwords to GitHub.

### 4. Start the Backend

```bash
py -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

Swagger API Documentation:

http://127.0.0.1:8000/docs

The application creates the required PostgreSQL tables if they do not already exist.

### 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

http://localhost:5173

By default, the local frontend communicates with FastAPI at `http://127.0.0.1:8000`.

You can configure a different backend URL using `VITE_API_URL`.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register user |
| POST | `/login` | Login and receive JWT |
| GET | `/profile` | View logged-in user profile |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/expenses` | List, search, sort, and paginate expenses |
| POST | `/expenses` | Create expense |
| GET | `/expenses/{expense_id}` | Get expense |
| PUT | `/expenses/{expense_id}` | Update expense |
| DELETE | `/expenses/{expense_id}` | Delete expense |
| GET | `/expenses/summary/categories` | Category-wise totals |
| GET | `/expenses/reports/monthly` | Monthly spending report |
| GET | `/expenses/export/csv` | Download expenses as CSV |

### Budget

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/budget` | Create or update monthly budget |
| GET | `/budget` | View budget and remaining balance |

Protected endpoints require JWT authentication.

## Automated Testing

The backend includes **13 automated tests** covering:

- Registration and login
- Authentication protection
- Multi-user expense isolation
- Expense CRUD operations
- Budget isolation and calculations
- Search and pagination
- Monthly reports
- Category summaries and CSV export

Tests use a separate PostgreSQL database.

Create a test database named `expense_tracker_test` and add this variable to `.env`:

```env
TEST_DATABASE_URL=postgresql://USER:PASSWORD@HOST/expense_tracker_test?sslmode=require
```

**Important:** Never point `TEST_DATABASE_URL` to your main database. Automated tests clear records from the test tables.

Run the tests:

```bash
py -m pytest tests/ -v
```

**Last verified result: 13 passed.**

To check the frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Deployment

The application is deployed using three cloud services.

### Frontend — Vercel

Vercel hosts the React frontend.

Configuration:

```text
Framework: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

Environment variable:

```env
VITE_API_URL=https://expense-tracker-oube.onrender.com
```

Live frontend:

https://expense-tracker-khaki-eight-17.vercel.app/

### Backend — Render

Render hosts the FastAPI backend.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```env
DATABASE_URL=your_neon_postgresql_connection
SECRET_KEY=your_jwt_secret
FRONTEND_URL=https://expense-tracker-khaki-eight-17.vercel.app
```

Live API:

https://expense-tracker-oube.onrender.com/docs

### Database — Neon

Neon hosts the PostgreSQL database.

FastAPI connects to Neon using Psycopg and the `DATABASE_URL` environment variable.

The database stores:

- Users
- Expenses
- Budgets

The application uses free-tier hosting options, which have usage limits. Render's free service may take longer to respond after inactivity.

## What I Learned

Through this project, I gained practical experience in:

- Building REST APIs with FastAPI
- Developing a React frontend
- Implementing JWT authentication
- Secure password hashing
- Writing SQL queries
- Migrating from SQLite to PostgreSQL
- Connecting frontend, backend, and database
- Writing automated tests with Pytest
- Managing code using Git and GitHub
- Deploying applications using Vercel, Render, and Neon
- Configuring environment variables and CORS

## Future Improvements

- Add frontend automated testing
- Improve accessibility and error handling
- Add CI/CD checks using GitHub Actions

## Project Status

**Deployed**

- React frontend: Vercel
- FastAPI backend: Render
- PostgreSQL database: Neon
- Automated backend tests: 13 passed

Final end-to-end verification of the deployed website is recommended.
