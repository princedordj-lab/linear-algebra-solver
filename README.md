# LinSolve — Linear Algebra Solver

A full-featured web application for solving linear systems **Ax = b** using eight numerical methods, with step-by-step solution display, matrix analysis tools, and user authentication. Built with **Flask**, **NumPy**, and **Tailwind CSS**.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-green)
![Tailwind](https://img.shields.io/badge/tailwind-css-38bdf8)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **8 numerical methods** — Direct, iterative, and LU decomposition
- **Step-by-step display** — Navigate through each computation step, export as TXT / DOCX / PDF
- **Matrix properties** — Determinant, rank, eigenvalues
- **Side-by-side comparison** — Run all 8 methods on the same matrix
- **Shareable solver links** — Base64-encoded matrix data in the URL
- **Problem presets** — Vandermonde, Hilbert, diagonal-dominant, and more
- **Solve history** — Persisted per user (saved to SQLite)
- **Matrix visualization** — Color-coded heatmap + convergence plots
- **User authentication** — Register / login with session-based auth
- **Dark / light theme** — Toggle persisted in browser storage
- **Fully responsive** — Mobile-first layouts throughout (back buttons, collapsible sidebars, responsive canvases)

---

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Landing / Dashboard | `/` | Landing hero for guests, tool grid for authenticated users |
| Solver | `/solver` | 8 methods with step-by-step display and export |
| Properties | `/properties` | Determinant, rank, eigenvalue computation |
| Compare | `/compare` | All 8 methods side-by-side on the same matrix |
| Share | `/share` | Generate base64-encoded shareable solver links |
| Presets | `/presets` | Built-in matrix problem presets |
| History | `/history` | Saved solve history (per user) |
| Paste | `/paste` | Quick matrix paste from text input |
| Visualize | `/visualize` | Color-coded heatmap of matrix values |
| Convergence | `/convergence` | Residual drop plot for Jacobi / Gauss-Seidel |
| Settings | `/settings` | Account settings (requires login) |
| Auth | `/auth` | Login / registration |

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
│   └── index.py           # Vercel serverless entry point
├── public/
│   └── logo.svg           # Favicon / brand logo
├── templates/
│   ├── index.html         # Landing page + auth dashboard
│   ├── auth.html          # Login / registration
│   ├── settings.html      # Account settings
│   ├── solver.html        # Core solver UI
│   ├── properties.html    # Matrix properties
│   ├── compare.html       # Method comparison
│   ├── share.html         # Shareable link generator
│   ├── presets.html       # Problem presets
│   ├── history.html       # Solve history
│   ├── paste.html         # Quick paste
│   ├── visualize.html     # Heatmap visualization
│   └── convergence.html   # Convergence plot
├── app.py                 # Flask server — all routes
├── solver.py              # 8 solver functions
├── models.py              # SQLite auth models & helpers
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
cd py
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. The server runs in debug mode by default.

---

## Usage

### Guest flow
- Visit `/` — see the landing page with feature highlights and "Get Started" / "Sign In" buttons
- Click **Start Solving** — redirected to `/auth` for registration or login

### Authenticated flow
- Access all 11 tools from the dashboard grid on `/`
- **Solver** — Select a method, enter matrix A and vector b, step through the solution
- **Compare** — Run all 8 methods on the same matrix in one click
- **Properties** — Compute determinant, rank, and eigenvalues
- **Share** — Generate a link with your matrix data encoded in the URL
- **Presets** — Load common matrices (Hilbert, Vandermonde, etc.)
- **History** — Browse and reopen past solves
- **Visualize** — Generate a color-coded heatmap
- **Convergence** — Plot residual drop for iterative methods

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

**Method keys:** `gaussian_partial`, `gaussian_complete`, `gauss_jordan`, `matrix_inverse`, `jacobi`, `gauss_seidel`, `lu_doolittle`, `lu_crout`

**Response:**

```json
{
  "solution": [2.2222, 1.1944, -1.25],
  "steps": [ { "label": "...", "matrix": [...], "vector": [...] } ],
  "verification": { "expected": [...], "actual": [...], "match": true }
}
```

### `GET /api/auth/me`

Returns current user info for the dashboard auth state toggle.

### `GET /api/history`, `POST /api/history`, `DELETE /api/history`

CRUD for saved solve history (authenticated users only).

---

## Responsive Design

All pages are built mobile-first:

- **Body** uses `overflow: clip; min-height: 100vh` to enable inner scrolling on mobile
- **Back button** on every sub-page header
- **Sidebars** (solver, properties) collapse vertically on small screens (`max-lg:max-h-[50vh]`)
- **Matrix input cells** use responsive widths (`w-12 sm:w-14`)
- **Canvases** constrained by `max-width: 100%` with `aspect-ratio`
- **Settings** uses horizontal tab bar on mobile, sidebar on desktop

---

## Deploy on Vercel

### Vercel Dashboard (recommended)

1. Push to a GitHub / GitLab / Bitbucket repository
2. Go to [vercel.com](https://vercel.com) → **Add New > Project**
3. Import your repo — Vercel auto-detects settings
4. Click **Deploy**

### Vercel CLI

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
| Auth | Flask-Login, Werkzeug, SQLite |
| Numerical | NumPy 2.x |
| Frontend | Tailwind CSS (CDN) |
| Typography | Inter, JetBrains Mono (Google Fonts) |
| Hosting | Vercel (serverless Python) |

---

## License

MIT