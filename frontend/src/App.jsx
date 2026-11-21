
import { useEffect, useState } from 'react'
import Dashboard from './Dashboard'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const LIMIT = 10

function emptyForm() {
  const today = new Date()
  const localDate = new Date(
    today.getTime() - today.getTimezoneOffset() * 60000
  ).toISOString().slice(0, 10)

  return {
    name: '',
    amount: '',
    category: '',
    date: localDate,
  }
}

function App() {
  // Authentication
  const [token, setToken] = useState(
    () => sessionStorage.getItem('access_token') || ''
  )
  const [authMode, setAuthMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  // Expense management
  const [expenses, setExpenses] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [deleteId, setDeleteId] = useState(null)

  // Search, sorting and pagination
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('id')
  const [order, setOrder] = useState('asc')
  const [skip, setSkip] = useState(0)

  // Refresh dashboard after database changes
  const [refreshKey, setRefreshKey] = useState(0)

  function logout() {
    sessionStorage.removeItem('access_token')
    setToken('')
    setExpenses([])
    setPassword('')
    setMessage('')
    setEditingId(null)
    setDeleteId(null)
    setForm(emptyForm())
    setSearch('')
    setSkip(0)
    setAuthMode('login')
  }

  function handleExpiredSession() {
    logout()
    setMessage('Session expired. Please login again.')
  }

  async function loadExpenses(
    authToken = token,
    offset = skip,
    keyword = search,
    sort = sortBy,
    direction = order
  ) {
    setLoading(true)

    const params = new URLSearchParams({
      search: keyword,
      sort_by: sort,
      order: direction,
      skip: String(offset),
      limit: String(LIMIT),
    })

    try {
      const response = await fetch(
        `${API}/expenses?${params}`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      )

      if (response.status === 401) {
        handleExpiredSession()
        return
      }

      if (!response.ok) {
        throw new Error('Failed to load expenses')
      }

      const data = await response.json()
      setExpenses(data)
      setSkip(offset)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
  const savedToken = sessionStorage.getItem('access_token')

  if (!savedToken) return

  let cancelled = false

  async function restoreSession() {
    try {
      const response = await fetch(
        `${API}/expenses?sort_by=id&order=asc&skip=0&limit=${LIMIT}`,
        {
          headers: {
            Authorization: `Bearer ${savedToken}`,
          },
        }
      )

      if (cancelled) return

      if (response.status === 401) {
        sessionStorage.removeItem('access_token')
        setToken('')
        setMessage('Session expired. Please login again.')
        return
      }

      if (!response.ok) {
        throw new Error('Failed to load expenses')
      }

      const data = await response.json()

      if (!cancelled) {
        setExpenses(data)
      }
    } catch {
      if (!cancelled) {
        setMessage('Cannot connect to FastAPI')
      }
    }
  }

  restoreSession()

  return () => {
    cancelled = true
  }
}, [])

  // LOGIN
  async function handleLogin(event) {
    event.preventDefault()
    logout()
    setLoading(true)

    const body = new URLSearchParams({
      username,
      password,
    })

    try {
      const response = await fetch(`${API}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      })

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.detail || 'Login failed')
        return
      }

      sessionStorage.setItem(
        'access_token',
        data.access_token
      )

      setToken(data.access_token)
      setMessage('Login successful')

      await loadExpenses(
        data.access_token, 0, '', 'id', 'asc'
      )
    } catch {
      setMessage('Cannot connect to FastAPI')
    } finally {
      setLoading(false)
    }
  }

  // REGISTRATION
  async function handleRegister(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const response = await fetch(`${API}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 409) {
          setMessage('Username already exists')
        } else {
          setMessage(
            typeof data.detail === 'string'
              ? data.detail
              : 'Username must have 3+ characters and password 8+ characters'
          )
        }
        return
      }

      setPassword('')
      setAuthMode('login')
      setMessage('Registration successful! Please login.')
    } catch {
      setMessage('Cannot connect to FastAPI')
    } finally {
      setLoading(false)
    }
  }

  // ADD OR EDIT
  async function handleSave(event) {
    event.preventDefault()
    setLoading(true)

    const expenseData = {
      name: form.name.trim(),
      amount: Number(form.amount),
      category: form.category.trim(),
      date: form.date,
    }

    if (
      expenseData.name.length < 2 ||
      expenseData.category.length < 2 ||
      !Number.isFinite(expenseData.amount) ||
      expenseData.amount <= 0
    ) {
      setMessage('Please enter valid expense details')
      setLoading(false)
      return
    }

    const url = editingId === null
      ? `${API}/expenses`
      : `${API}/expenses/${editingId}`

    try {
      const response = await fetch(url, {
        method: editingId === null ? 'POST' : 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(expenseData),
      })

      if (response.status === 401) {
        handleExpiredSession()
        return
      }

      if (!response.ok) {
        throw new Error('Could not save expense')
      }

      setMessage(
        editingId === null
          ? 'Expense added successfully'
          : 'Expense updated successfully'
      )

      setForm(emptyForm())
      setEditingId(null)

      await loadExpenses(token, 0)
      setRefreshKey((previous) => previous + 1)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  function handleEdit(expense) {
    setEditingId(expense.id)
    setForm({
      name: expense.name,
      amount: String(expense.amount),
      category: expense.category,
      date: expense.date,
    })

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // DELETE - CUSTOM REACT CONFIRMATION
  async function confirmDelete() {
    if (deleteId === null) return

    const id = deleteId
    setLoading(true)

    try {
      const response = await fetch(
        `${API}/expenses/${id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.status === 401) {
        handleExpiredSession()
        return
      }

      if (!response.ok) {
        throw new Error('Could not delete expense')
      }

      setDeleteId(null)
      setMessage('Expense deleted successfully')
      setEditingId(null)
      setForm(emptyForm())

      const nextSkip =
        expenses.length === 1 && skip > 0
          ? skip - LIMIT
          : skip

      await loadExpenses(token, nextSkip)
      setRefreshKey((previous) => previous + 1)
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  // CSV EXPORT
  async function downloadCSV() {
    setLoading(true)

    try {
      const response = await fetch(
        `${API}/expenses/export/csv`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.status === 401) {
        handleExpiredSession()
        return
      }

      if (!response.ok) {
        throw new Error('CSV download failed')
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      const link = document.createElement('a')
      link.href = url
      link.download = 'expenses.csv'
      document.body.appendChild(link)
      link.click()
      link.remove()

      setTimeout(() => URL.revokeObjectURL(url), 1000)
      setMessage('CSV downloaded successfully')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  // LOGIN / REGISTRATION SCREEN
  if (!token) {
    return (
      <main className="auth-page">
        <div className="auth-card">
          <h1>Expense Tracker</h1>
          <p>Manage your expenses in one place</p>

          <h2>
            {authMode === 'login'
              ? 'Login'
              : 'Create Account'}
          </h2>

          <form
            onSubmit={
              authMode === 'login'
                ? handleLogin
                : handleRegister
            }
          >
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              minLength={authMode === 'register' ? 3 : undefined}
              required
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={authMode === 'register' ? 8 : undefined}
              required
            />

            <button disabled={loading} type="submit">
              {loading
                ? 'Please wait...'
                : authMode === 'login'
                  ? 'Login'
                  : 'Register'}
            </button>
          </form>

          <p role="status">{message}</p>

          <button
            type="button"
            className="text-button"
            onClick={() => {
              setAuthMode(
                authMode === 'login' ? 'register' : 'login'
              )
              setMessage('')
              setPassword('')
            }}
          >
            {authMode === 'login'
              ? "Don't have an account? Register"
              : 'Already registered? Login'}
          </button>
        </div>
      </main>
    )
  }

  // MAIN APPLICATION
  return (
    <main className="container">
      <header className="main-header">
        <div>
          <h1>Expense Tracker</h1>
          <p>Personal finance dashboard</p>
        </div>

        <button
          className="secondary-button"
          onClick={logout}
        >
          Logout
        </button>
      </header>

      {message && (
        <p className="status-message" role="status">
          {message}
        </p>
      )}

      {/* EXISTING DASHBOARD */}
      <Dashboard token={token} refreshKey={refreshKey} />

      {/* ADD / EDIT EXPENSE */}
      <section className="content-panel">
        <h2>
          {editingId === null
            ? 'Add Expense'
            : 'Edit Expense'}
        </h2>

        <form onSubmit={handleSave} className="expense-form">
          <input
            placeholder="Expense name"
            minLength={2}
            value={form.name}
            onChange={(e) =>
              setForm({ ...form, name: e.target.value })
            }
            required
          />

          <input
            type="number"
            placeholder="Amount"
            min="0.01"
            step="0.01"
            value={form.amount}
            onChange={(e) =>
              setForm({ ...form, amount: e.target.value })
            }
            required
          />

          <input
            placeholder="Category"
            minLength={2}
            value={form.category}
            onChange={(e) =>
              setForm({ ...form, category: e.target.value })
            }
            required
          />

          <input
            type="date"
            value={form.date}
            onChange={(e) =>
              setForm({ ...form, date: e.target.value })
            }
            required
          />

          <button disabled={loading} type="submit">
            {editingId === null
              ? 'Add Expense'
              : 'Save Changes'}
          </button>

          {editingId !== null && (
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setEditingId(null)
                setForm(emptyForm())
              }}
            >
              Cancel
            </button>
          )}
        </form>
      </section>

      {/* EXPENSE MANAGEMENT */}
      <section className="content-panel">
        <div className="section-header">
          <h2>My Expenses</h2>
          <button
            onClick={downloadCSV}
            disabled={loading}
            className="export-button"
          >
            Download CSV
          </button>
        </div>

        <div className="filter-panel">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              loadExpenses(token, 0)
            }}
          >
            <input
              placeholder="Search name or category"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button disabled={loading} type="submit">
              Search
            </button>
          </form>

          <div className="filters">
            <select
              value={sortBy}
              onChange={(e) => {
                const value = e.target.value
                setSortBy(value)
                loadExpenses(token, 0, search, value, order)
              }}
            >
              <option value="id">ID</option>
              <option value="name">Name</option>
              <option value="amount">Amount</option>
              <option value="date">Date</option>
            </select>

            <select
              value={order}
              onChange={(e) => {
                const value = e.target.value
                setOrder(value)
                loadExpenses(token, 0, search, sortBy, value)
              }}
            >
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Amount</th>
                <th>Category</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{expense.name}</td>
                  <td>₹{expense.amount.toFixed(2)}</td>
                  <td>{expense.category}</td>
                  <td>{expense.date}</td>
                  <td className="action-cell">
                    <button
                      disabled={loading}
                      className="secondary-button"
                      onClick={() => handleEdit(expense)}
                    >
                      Edit
                    </button>

                    <button
                      disabled={loading}
                      className="danger-button"
                      onClick={() => setDeleteId(expense.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {expenses.length === 0 && !loading && (
          <p>No expenses found.</p>
        )}

        <div className="pagination">
          <button
            className="secondary-button"
            disabled={skip === 0 || loading}
            onClick={() => loadExpenses(token, skip - LIMIT)}
          >
            Previous
          </button>

          <span>Page {Math.floor(skip / LIMIT) + 1}</span>

          <button
            className="secondary-button"
            disabled={expenses.length < LIMIT || loading}
            onClick={() => loadExpenses(token, skip + LIMIT)}
          >
            Next
          </button>
        </div>

        {loading && <p>Loading...</p>}
      </section>

      {/* CUSTOM DELETE DIALOG */}
      {deleteId !== null && (
        <div className="modal-overlay">
          <div
            className="modal"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="delete-title"
            aria-describedby="delete-description"
          >
            <h2 id="delete-title">Delete Expense?</h2>
            <p id="delete-description">
              This action cannot be undone.
            </p>

            <div className="modal-actions">
              <button
                disabled={loading}
                className="secondary-button"
                onClick={() => setDeleteId(null)}
              >
                Cancel
              </button>

              <button
                disabled={loading}
                className="danger-button"
                onClick={confirmDelete}
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}

export default App
