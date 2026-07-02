# Linear Algebra Solver

A web application for solving linear systems **Ax = b** using eight numerical methods, with step-by-step solution display. Built with **Flask**, **NumPy**, and **Tailwind CSS**.

![dark theme](https://img.shields.io/badge/theme-dark-blue)
![light theme](https://img.shields.io/badge/theme-light-gray)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **8 numerical methods** — Direct, iterative, and LU decomposition methods
- **Step-by-step display** — navigate through each computational step
- **Dark / light theme** — toggle with one click, persisted in browser storage
- **Responsive layout** — two-column on desktop, stacked on mobile
- **Verification** — every solution is checked against Ax ≈ b
- **Matrix input** — dynamic n×n grid that resizes automatically
- **Vercel-ready** — deploy in one click

---

## Methods

| # | Method | Type | Description |
|---|--------|------|-------------|
| 1 | Gaussian — Partial Pivoting | Direct | Row swaps for largest pivot in each column |
| 2 | Gaussian — Complete Pivoting | Direct | Row + column swaps with column order tracking |
| 3 | Gauss-Jordan Elimination | Direct | Reduces to Reduced Row Echelon Form (RREF) |
| 4 | Matrix Inverse (Gauss-Jordan) | Direct | Augments [A\|I], reduces to [I\|A⁻¹] |
| 5 | Jacobi Iterative | Iterative | Component-wise using previous iteration values |
| 6 | Gauss-Seidel Iterative | Iterative | In-place updates using latest computed values |
| 7 | LU Decomposition (Doolittle) | Direct | L has 1s on diagonal, forward/back substitution |
| 8 | LU Decomposition (Crout) | Direct | U has 1s on diagonal, forward/back substitution |

---

## Project Structure

```
py/
├── api/
│   └── index.py          # Vercel serverless entry point
├── templates/
│   └── index.html         # Tailwind-styled UI (dark/light theme)
├── app.py                 # Flask server — GET / and POST /solve
├── solver.py              # 8 solver functions with step-by-step output
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel deployment configuration
└── README.md              # This file
```

---

## Local Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Install

```bash
# Clone or navigate to the project directory
cd py

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

The server runs in debug mode by default, so changes to the code trigger an automatic reload.

---

## Usage

1. Select a method from the dropdown
2. Set the matrix size **n** (1–10)
3. Enter matrix **A** values in the grid
4. Enter vector **b** values (hidden for Matrix Inverse)
5. For Jacobi / Gauss-Seidel, set tolerance and max iterations
6. Click **Solve**
7. Use **Prev / Next** to step through the computation
8. Check the **Solution** and **Verification** sections at the bottom
9. Click **↻** to reset all inputs and results
10. Toggle **☽ / ☀** in the header for dark / light mode

---

## API Reference

### `POST /solve`

Accepts JSON and returns the solver result with step-by-step data.

**Request body:**

```json
{
  "method": "gaussian_partial",
  "n": 3,
  "A": [[2, -1, 1], [3, 3, 9], [3, 3, 5]],
  "b": [2, -1, 4],
  "tol": 0.000001,
  "max_iter": 100
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `method` | string | yes | One of the 8 method keys (see below) |
| `n` | int | yes | Matrix size |
| `A` | 2D array | yes | n×n coefficient matrix |
| `b` | array | no | Omitted for `matrix_inverse` |
| `tol` | float | no | Used by Jacobi / Gauss-Seidel (default 1e-6) |
| `max_iter` | int | no | Used by Jacobi / Gauss-Seidel (default 100) |

**Method keys:** `gaussian_partial`, `gaussian_complete`, `gauss_jordan`, `matrix_inverse`, `jacobi`, `gauss_seidel`, `lu_doolittle`, `lu_crout`

**Response:**

```json
{
  "solution": [2.2222, 1.1944, -1.25],
  "steps": [
    {
      "label": "Initial Augmented Matrix",
      "matrix": [[...], ...],
      "vector": [...],
      "extra": {...}
    }
  ],
  "verification": {
    "expected": [2, -1, 4],
    "actual": [2.0, -1.0, 4.0],
    "match": true
  }
}
```

---

## Deploy on Vercel

### Option 1 — Vercel Dashboard (recommended)

1. Push the project to a **GitHub**, **GitLab**, or **Bitbucket** repository
2. Go to [vercel.com](https://vercel.com) and click **Add New > Project**
3. Import your repository
4. Vercel auto-detects the settings. Click **Deploy**

### Option 2 — Vercel CLI

```bash
npm install -g vercel
vercel login
cd py
vercel --prod
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, Flask 3.x |
| Numerical | NumPy 2.x |
| Frontend | Tailwind CSS (CDN) |
| Typography | Inter, JetBrains Mono (Google Fonts) |
| Hosting | Vercel (serverless Python) |

---

## License

MIT