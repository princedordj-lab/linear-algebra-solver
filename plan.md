# LinSolve — Linear Algebra Solver Web App

## Overview

A Flask web app that solves linear systems **Ax = b** using 8 numerical methods, with step-by-step solution display, user authentication, and a full suite of matrix analysis tools. Styled with Tailwind CSS via CDN.

---

## File Structure

```
py/
├── app.py             (~280 lines) — Flask server, all routes
├── solver.py          (~400 lines) — 8 solver functions
├── models.py          (~142 lines) — SQLite auth models & DB helpers
├── requirements.txt    — Python dependencies
├── vercel.json         — Vercel deployment config
├── plan.md             — This file
├── linsolve.db         — SQLite database (auto-created)
├── api/
│   └── index.py        — Vercel serverless entry point
├── public/
│   └── logo.svg        — App favicon
├── templates/
│   ├── index.html        (~474 lines) — Landing page + auth dashboard
│   ├── auth.html         (~110 lines) — Login / register
│   ├── settings.html     (~210 lines) — User settings (mobile-responsive)
│   ├── solver.html       (~205 lines) — Core solver (8 methods, steps)
│   ├── properties.html   (~139 lines) — Matrix properties (det, rank, eig)
│   ├── compare.html      (~ 63 lines) — Side-by-side method comparison
│   ├── share.html        (~ 76 lines) — Generate shareable solver links
│   ├── presets.html      (~ 55 lines) — Common matrix problem presets
│   ├── history.html      (~ 50 lines) — Previous solve history
│   ├── paste.html        (~ 54 lines) — Paste/share matrix data
│   ├── visualize.html    (~ 48 lines) — Matrix heatmap visualization
│   └── convergence.html  (~ 49 lines) — Iterative method convergence plot
```

---

## Feature Pages

| Page          | Route          | Description                                         |
|---------------|----------------|-----------------------------------------------------|
| Landing/Dash  | `/`            | Non-auth: hero + features. Auth: tool dashboard     |
| Auth          | `/auth`        | Login / register with validation                    |
| Solver        | `/solver`      | 8 methods, step-by-step display, export TXT/DOCX/PDF|
| Properties    | `/properties`  | Determinant, rank, eigenvalues                      |
| Compare       | `/compare`     | Run all 8 methods side-by-side on same matrix       |
| Share         | `/share`       | Generate base64-encoded shareable URL               |
| Presets       | `/presets`     | Pre-built matrix problems (Vandermonde, Hilbert…)   |
| History       | `/history`     | Persisted solve history per user                    |
| Paste         | `/paste`       | Quick matrix paste from text                        |
| Visualize     | `/visualize`   | Color-coded heatmap of matrix values                |
| Convergence   | `/convergence` | Residual drop plot for Jacobi & Gauss-Seidel        |
| Settings      | `/settings`    | Account settings (protected route)                  |

---

## Methods

| # | Method                     | Type      | Solves  | Key Features                                      |
|---|----------------------------|-----------|---------|---------------------------------------------------|
| 1 | Gaussian — Partial Pivoting | Direct    | Ax = b  | Row swaps for largest pivot in column              |
| 2 | Gaussian — Complete Pivoting| Direct    | Ax = b  | Row + column swaps, colOrder tracking              |
| 3 | Gauss-Jordan Elimination   | Direct    | Ax = b  | Pivot→1, eliminate above AND below, RREF           |
| 4 | Matrix Inverse (Gauss-Jordan)| Direct   | A⁻¹     | Augment [A\|I], reduce to [I\|A⁻¹]                 |
| 5 | Jacobi Iterative           | Iterative | Ax = b  | Component-wise using previous iteration values      |
| 6 | Gauss-Seidel Iterative     | Iterative | Ax = b  | In-place updates using latest values                |
| 7 | LU Decomposition (Doolittle)| Direct    | Ax = b  | L has 1s on diagonal, forward/back substitution     |
| 8 | LU Decomposition (Crout)   | Direct    | Ax = b  | U has 1s on diagonal, forward/back substitution     |

---

## `solver.py` — Core Logic

### Method Map

```python
MATRIX_METHODS = {
    "gaussian_partial":  solve_gaussian_partial,
    "gaussian_complete": solve_gaussian_complete,
    "gauss_jordan":      solve_gauss_jordan,
    "matrix_inverse":    solve_matrix_inverse,
    "jacobi":            solve_jacobi,
    "gauss_seidel":      solve_gauss_seidel,
    "lu_doolittle":      solve_lu_doolittle,
    "lu_crout":          solve_lu_crout,
}
```

### Function Signatures

**Direct methods (1–4, 7–8):**
```python
def solve_<method>(A: np.ndarray, b: np.ndarray or None) -> dict:
    return {
        "solution": list,       # solution vector or inverse matrix
        "steps": [              # ordered list of steps
            {
                "label": str,
                "matrix": list,
                "vector": list,
                "extra": dict,
            }
        ],
        "verification": { "expected": list, "actual": list, "match": bool }
    }
```

**Iterative methods (5–6):**
```python
def solve_<method>(A: np.ndarray, b: np.ndarray, x0=None, tol=1e-6, max_iter=100) -> dict:
    return {
        "solution": list,
        "iterations": int,
        "converged": bool,
        "steps": [
            {
                "label": str,
                "x": list,
                "residual": float,
                "delta": float,
                "extra": dict,
            }
        ],
        "verification": { ... }
    }
```

---

## `app.py` — Flask Server

### Routes

| Route          | Method | Purpose                                          |
|----------------|--------|--------------------------------------------------|
| `/`            | GET    | Serve index.html (landing / dashboard)           |
| `/auth`        | GET    | Serve auth.html                                  |
| `/auth`        | POST   | Login or register                                |
| `/logout`      | GET    | Logout + redirect to `/`                         |
| `/solver`      | GET    | Serve solver.html                                |
| `/properties`  | GET    | Serve properties.html                            |
| `/compare`     | GET    | Serve compare.html                               |
| `/share`       | GET    | Serve share.html                                 |
| `/presets`     | GET    | Serve presets.html                               |
| `/history`     | GET    | Serve history.html                               |
| `/paste`       | GET    | Serve paste.html                                 |
| `/visualize`   | GET    | Serve visualize.html                             |
| `/convergence` | GET    | Serve convergence.html                           |
| `/settings`    | GET    | Serve settings.html (protected)                  |
| `/solve`       | POST   | Accept JSON, run solver, return result JSON      |
| `/api/auth/me` | GET    | Return current user JSON (for dashboard toggle)  |
| `/api/history` | GET    | Return saved solve history for current user      |
| `/api/history` | POST   | Save a solve result to history                   |
| `/api/history` | DELETE | Clear all history for current user               |
| `/api/settings`| POST   | Update user settings                             |

### Auth System

- **SQLite** database (`linsolve.db`) with `users` and `user_data` tables
- **Session-based** auth via `flask_login`
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Dashboard toggle in `index.html` uses `/api/auth/me` endpoint (no redirect)

### API: POST /solve

**Request:**
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

**Response:**
```json
{
  "solution": [2.2222, 1.1944, -1.25],
  "steps": [ { "label": "...", "matrix": [...], "vector": [...] } ],
  "verification": { "expected": [...], "actual": [...], "match": true }
}
```

---

## Responsive Design

All pages are mobile-responsive with the following patterns:

| Pattern | Implementation |
|---------|---------------|
| Body scroll | `overflow: clip; min-height: 100vh` (not `overflow: hidden`) |
| Back button | Arrow + "Back" in header on every sub-page |
| Sidebar layout | `flex-col lg:flex-row` — sidebar stacks vertically on mobile with `max-lg:max-h-[50vh]` |
| Matrix inputs | Responsive cell sizing: `w-12 sm:w-14` |
| Canvases | `max-width: 100%` with `aspect-ratio` preservation |
| Touch targets | `py-2`+ for buttons, `py-2.5` for header auth buttons |
| Settings tabs | Horizontal tab bar on mobile, sidebar on `md+` |

---

## Design Decisions

| Decision                      | Rationale                                              |
|-------------------------------|--------------------------------------------------------|
| Tailwind via CDN              | Zero build step, fast prototyping                      |
| Dynamic input grids via JS    | Adapts to any n, no server round-trips for UI changes  |
| Unified step dict format      | Consistent rendering regardless of method              |
| Landing + dashboard same page | JS auth check toggles visibility, avoids redirect      |
| SQLite for auth               | Zero-config, portable, no external DB server           |
| `overflow: clip`              | Allows inner scroll panels on mobile vs `overflow: hidden` |

---

## Dependencies

- Python 3.x
- Flask ≥ 3.0
- Flask-Login ≥ 0.6
- NumPy ≥ 2.0
- Werkzeug ≥ 3.0
- Tailwind CSS (CDN, no install)

---

## Implementation Order

1. `solver.py` — All 8 solver functions
2. `app.py` — Flask server with `/` and `/solve` routes
3. `templates/solver.html` — First UI (full solver with steps)
4. `models.py` + auth routes — User system
5. `templates/index.html` — Landing page + auth dashboard
6. Remaining feature pages — properties, compare, share, presets, history, paste, visualize, convergence
7. `templates/settings.html` — Account settings
8. Mobile responsive pass — Back buttons, overflow fix, sidebar collapse, responsive inputs/canvases
9. `README.md` + `plan.md` — Documentation