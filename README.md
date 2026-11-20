**Expense Tracker**

A simple full-stack expense tracking application built using Python, FastAPI, React and SQLite.

I built this project to practice backend development, REST APIs, authentication, database operations and connecting a frontend to a backend.

The application allows users to manage their expenses, set monthly budgets and understand their spending.

**Features**

- User registration and login using JWT authentication
- Secure password hashing with Argon2
- Separate expense data for each user
- Add, view, update and delete expenses
- Search, sort and browse expenses using pagination
- Monthly spending reports
- Category-wise spending charts
- Set and update monthly budgets
- Check remaining budget and spending limits
- Export expenses to CSV
- Responsive React interface

**Technologies Used**

Backend: Python, FastAPI, SQLite, Pydantic

Frontend: React, JavaScript, CSS, Vite

Authentication: JWT and Argon2 password hashing

Testing: pytest

Version control: Git and GitHub

**Project Structure**

```text
expense-tracker/
├── app/             FastAPI backend
├── frontend/        React frontend
├── tests/           Backend tests
├── scripts/         Sample data script
├── data/            Local SQLite database
├── requirements.txt
└── README.md
```

**Running the Project Locally**

Make sure Python, Node.js and npm are installed.

1. Clone the repository and open the project directory.

```bash
git clone https://github.com/yrchse/expense-tracker.git
cd expense-tracker
```

2. Install the Python dependencies.

```bash
py -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root. Generate a random secret key with:

```bash
py -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `.env`:

```text
SECRET_KEY=your_generated_secret_key
```

4. Start the backend.

```bash
py -m uvicorn app.main:app --reload
```

The FastAPI documentation will be available at http://127.0.0.1:8000/docs.

5. Open another terminal and start React.

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

Register a new account and log in to start using the application.

**Testing**

Run the backend tests from the project root:

```bash
py -m pytest tests/ -v
```

The current backend test suite contains 13 automated tests covering authentication, user isolation, expenses, budgets and reporting.

To check the frontend:

```bash
cd frontend
npm run lint
npm run build
```

**What I Learned**

This project helped me understand how a full-stack application works.

I learned how to create APIs using FastAPI, store data in SQLite, secure endpoints using JWT, validate user input and connect React to Python APIs.

I also practiced automated testing, Git and organizing a project into separate modules.

**Future Improvements**

- Deploy the application online
- Move to PostgreSQL for production database hosting
- Add automated frontend tests
- Improve error handling and accessibility

**Project Status**

The core application is working locally. Deployment is the next planned step.