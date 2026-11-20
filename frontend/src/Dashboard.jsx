
import { useEffect, useState } from 'react'
import './Dashboard.css'

const API = 'http://127.0.0.1:8000'

function currentMonth() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

function Dashboard({ token, refreshKey }) {
  const [month, setMonth] = useState(currentMonth())
  const [report, setReport] = useState(null)
  const [budget, setBudget] = useState(null)
  const [budgetInput, setBudgetInput] = useState('')
  const [categories, setCategories] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  async function apiGet(path) {
    const response = await fetch(`${API}${path}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.status === 404 && path === '/budget') {
      return null
    }

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }

    return response.json()
  }

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      setLoading(true)
      setMessage('')

      try {
        const [reportData, budgetData, categoryData] =
          await Promise.all([
            apiGet(`/expenses/reports/monthly?month=${month}`),
            apiGet('/budget'),
            apiGet('/expenses/summary/categories'),
          ])

        if (!cancelled) {
          setReport(reportData)
          setBudget(budgetData)
          setCategories(categoryData)
        }
      } catch (error) {
        if (!cancelled) {
          setMessage(error.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      cancelled = true
    }
    // Reload when the month, token, or expenses change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, month, refreshKey])

  async function saveBudget(event) {
    event.preventDefault()

    const amount = Number(budgetInput)

    if (!Number.isFinite(amount) || amount <= 0) {
      setMessage('Enter a valid budget greater than zero')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const response = await fetch(`${API}/budget`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ amount }),
      })

      if (!response.ok) {
        throw new Error('Could not save budget')
      }

      const updatedBudget = await apiGet('/budget')
      setBudget(updatedBudget)
      setBudgetInput('')
      setMessage('Budget saved successfully')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  const totalCategorySpending = categories.reduce(
    (total, category) => total + category.total,
    0
  )

  const money = (value) =>
    `₹${Number(value || 0).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`

  return (
    <section className="dashboard">
      <h2>Spending Dashboard</h2>

      <label>
        Report month:{' '}
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />
      </label>

      {loading && <p>Loading dashboard...</p>}
      {message && <p role="status">{message}</p>}

      <div className="dashboard-cards">
        <article className="dashboard-card">
          <h3>Selected Month Spending</h3>
          <strong>{money(report?.total_spent)}</strong>
          <p>{report?.total_expenses ?? 0} expenses</p>
        </article>

        <article className="dashboard-card">
          <h3>Current Monthly Budget</h3>
          <strong>
            {budget ? money(budget.monthly_budget) : 'Not set'}
          </strong>
        </article>

        <article className="dashboard-card">
          <h3>Current Month Remaining</h3>
          <strong>
            {budget ? money(budget.remaining) : 'Not available'}
          </strong>

          {budget?.exceeded && (
            <p className="budget-warning">Budget exceeded!</p>
          )}

          {budget && !budget.exceeded && (
            <p className="budget-success">Within budget</p>
          )}
        </article>
      </div>

      <p className="dashboard-note">
        Budget and remaining always refer to the current month,
        regardless of the selected report month.
      </p>

      <div className="dashboard-panel">
        <h3>Set / Update Monthly Budget</h3>

        <form onSubmit={saveBudget}>
          <input
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Enter budget amount"
            value={budgetInput}
            onChange={(e) => setBudgetInput(e.target.value)}
            required
          />
          <button disabled={loading}>Save Budget</button>
        </form>
      </div>

      <div className="dashboard-panel">
        <h3>Category Spending (All Time)</h3>

        {categories.length === 0 && (
          <p>No category data available.</p>
        )}

        {categories.map((category) => {
          const percentage =
            totalCategorySpending > 0
              ? (category.total / totalCategorySpending) * 100
              : 0

          return (
            <div className="category-row" key={category.category}>
              <div className="category-label">
                <span>{category.category}</span>
                <span>{money(category.total)}</span>
              </div>

              <div
                className="category-track"
                role="progressbar"
                aria-label={`${category.category} share of spending`}
                aria-valuenow={Math.round(percentage)}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="category-fill"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default Dashboard
