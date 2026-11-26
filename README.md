Expense Tracker
A full-stack expense tracking application built with React, FastAPI, and PostgreSQL.

I built this project to practice REST APIs, authentication, database operations, automated testing, and full-stack deployment. Users can track expenses, manage monthly budgets, and view spending reports.

Live application: https://expense-tracker-khaki-eight-17.vercel.app/
Backend API documentation: https://expense-tracker-oube.onrender.com/docs
Source code: https://github.com/yrchse/expense-tracker
Features
- User registration and login with JWT authentication
- Password hashing with Argon2
- Separate expenses and budgets for each user
- Add, view, edit, and delete expenses
- Search, sorting, and pagination
- Monthly spending reports and category-wise summaries
- Monthly budget tracking, remaining balance, and overspending checks
- Export expenses to CSV
- Responsive React dashboard
Tech Stack
Part	Technology
Frontend	React, JavaScript, CSS, Vite
Backend	Python, FastAPI, Pydantic
Database	PostgreSQL, hosted on Neon
Database driver	Psycopg 3
Authentication	JWT, Argon2
Testing	pytest, FastAPI TestClient
Deployment	Vercel (frontend), Render (backend), Neon (database)
Version control	Git, GitHub


How It Works
User's browser
      |
      v
React frontend (Vercel)
      | HTTP requests / JSON responses
      v
FastAPI backend (Render)
      | SQL queries through Psycopg
      v
PostgreSQL database (Neon)
The React frontend sends requests to FastAPI. FastAPI validates requests, checks JWT authentication, and reads or writes data in PostgreSQL. The frontend does not connect directly to the database.
Project Structure
expense-tracker/
├── app/
│   ├── main.py              # FastAPI application and CORS
│   ├── auth.py              # Registration, login, JWT authentication
│   ├── database.py          # PostgreSQL connection and table creation
│   ├── schemas.py           # Request and response models
│   └── routers/
│       ├── expenses.py      # Expense CRUD, search, reports, CSV
│       └── budgets.py       # Monthly budgets
├── frontend/                # React and Vite application
├── tests/                   # Backend automated tests
├── scripts/                 # Development utilities
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable example
└── README.md
Run Locally
You need Python, Node.js, npm, and access to a PostgreSQL database (for example, a Neon database).

1. Clone the project
git clone https://github.com/yrchse/expense-tracker.git
cd expense-tracker
2. Install backend dependencies
py -m pip install -r requirements.txt
On macOS/Linux, use python3 instead of py.

3. Configure environment variables

Create a .env file in the project root:
SECRET_KEY=replace_with_a_random_secret_of_at_least_32_characters
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
Generate a secret with:
py -c "import secrets; print(secrets.token_hex(32))"
Replace the placeholders with your own values. Never commit .env, database passwords, or secret keys to GitHub.

4. Start FastAPI
py -m uvicorn app.main:app --reload
Open http://127.0.0.1:8000/docs to use the API documentation. The backend initializes its database tables when it starts.

5. Start React (in another terminal)
cd frontend
npm install
npm run dev
Open http://localhost:5173.

For local development, React uses http://127.0.0.1:8000 as its default backend URL. You can override it with a VITE_API_URL environment variable.
Testing
The backend has 13 automated tests covering authentication, user isolation, expenses, budgets, search, pagination, monthly reports, and CSV export.

Tests use a separate PostgreSQL database and clear its records before each test. Create a dedicated Neon database named expense_tracker_test and set this additional value in your local .env:
TEST_DATABASE_URL=postgresql://USER:PASSWORD@HOST/expense_tracker_test?sslmode=require
Warning: Never set TEST_DATABASE_URL to your main application database. The test setup deletes data from the test tables.

Run from the project root:
py -m pytest tests/ -v
Latest confirmed result: 13 tests passed.

To check the frontend build:
cd frontend
npm run lint
npm run build
Deployment
The app uses three hosted services:
- Vercel: Builds and hosts the React frontend from the frontend directory. Its VITE_API_URL environment variable points to the Render backend.
- Render: Runs the FastAPI application using the repository root. Its DATABASE_URL and SECRET_KEY environment variables are configured securely in Render.
- Neon: Hosts the PostgreSQL database used by FastAPI.
The Render backend also uses FRONTEND_URL to allow browser requests from the deployed Vercel website through CORS.

Deployment-related environment variables:
Platform	Key	Purpose
Vercel	VITE_API_URL	Public Render API URL
Render	DATABASE_URL	Private Neon database connection string
Render	SECRET_KEY	JWT signing secret
Render	FRONTEND_URL	Public Vercel website URL for CORS


The app is deployed using the services' free-tier options, which have usage and availability limits. A free Render service may take extra time to respond after inactivity.
What I Learned
This project helped me understand how a frontend communicates with a backend through HTTP requests, how FastAPI uses JWT to protect user data, and how PostgreSQL stores application records. I also practiced migrating from SQLite to PostgreSQL, writing automated tests, using Git/GitHub, and deploying separate frontend and backend services.
Future Improvements
- Add automated frontend tests
- Improve accessibility and error messages
- Add CI checks for testing and builds
Project Status
Deployed: React on Vercel, FastAPI on Render, and PostgreSQL on Neon. Backend automated tests: 13 passed. Final end-to-end verification of the deployed website remains a recommended check.