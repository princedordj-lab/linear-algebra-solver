# Linear Algebra Solver Web App — Implementation Plan

## Overview

A Flask web app that solves linear systems using 8 numerical methods, with step-by-step solution display.
Styled with Tailwind CSS via CDN.

---

## File Structure

```
py/
├── solver.py          (~400 lines)  — 8 solver functions
├── app.py             (~80 lines)   — Flask server, POST /solve
├── templates/
│   └── index.html     (~250 lines)  — Tailwind-styled UI
└── static/           (empty — Tailwind via CDN, no local CSS)
└── plan.md            — this file

```

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
                "label": str,   # e.g. "After Elimination Step 1"
                "matrix": list, # 2D array (augmented matrix, L, U, etc.)
                "vector": list, # optional — current solution estimate
                "extra": dict,  # optional — method-specific (colOrder, etc.)
            }
        ],
        "verification": {       # always computed for validation
            "expected": list,   # b or I
            "actual": list,     # A@x or A@A⁻¹
            "match": bool,
        }
    }
```

**Iterative methods (5–6):**
```python
def solve_<method>(A: np.ndarray, b: np.ndarray, x0=None, tol=1e-6, max_iter=100) -> dict:
    return {
        "solution": list,
        "iterations": int,      # number of iterations taken
        "converged": bool,
        "steps": [
            {
                "label": str,   # e.g. "Iteration 1"
                "x": list,      # current solution vector
                "residual": float,  # ||Ax - b||
                "delta": float,     # ||x_new - x_old||
                "extra": dict,  # per-component details
            }
        ],
        "verification": { ... }
    }
```

### Step Display per Method

| Method              | Steps shown                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| Gaussian Partial    | Initial augmented, row swaps, elimination steps, upper triangular, solution |
| Gaussian Complete   | Initial augmented, row/col swaps + colOrder, elimination, reordered solution|
| Gauss-Jordan        | Initial augmented, pivot→1, column elimination, RREF, solution              |
| Matrix Inverse      | [A\|I], pivot swaps, steps to identity, A⁻¹, A·A⁻¹ check                    |
| Jacobi              | Per-iteration: x vector, component deltas, residual norm                    |
| Gauss-Seidel        | Per-iteration + per-row: x updates, lower/upper sums, residual              |
| Doolittle           | Progressive L/U fill, Ly=b forward sub, Ux=y back sub                       |
| Crout               | Progressive L/U fill (L column first), Ly=b with division, Ux=y no division |

---

## `app.py` — Flask Server

### Routes

| Route    | Method | Purpose                         |
|----------|--------|---------------------------------|
| `/`      | GET    | Serve index.html                |
| `/solve` | POST   | Accept JSON, run solver, return result JSON |

### Request (POST /solve)

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

- `b` omitted for Matrix Inverse (method 4)
- `tol` and `max_iter` only used for Jacobi/Gauss-Seidel (methods 5–6)

### Response

Returns the solver function's output dict as JSON, with all numpy arrays converted to lists.

---

## `templates/index.html` — Tailwind UI

### Layout

**Desktop:** Two-column (input left, results right). **Mobile:** Stacked vertically.

### Sections

1. **Header** — "Linear Algebra Solver"
2. **Method Selector** — Dropdown, 3 optgroups:
   - Direct Methods (1–4)
   - Iterative Methods (5–6)
   - LU Decomposition (7–8)
3. **Input Panel:**
   - `n` — number input (triggers grid rebuild on change)
   - Matrix `A` — `n × n` grid of `<input>` elements, generated by JS
   - Vector `B` — `n` inputs in a row (hidden when method = Matrix Inverse)
   - Tolerance + Max Iterations — shown only for Jacobi / Gauss-Seidel
   - Solve button
4. **Results Panel** — hidden until solve:
   - Step navigation (prev/next buttons, step counter)
   - Active step display: label, matrices as HTML tables, vectors
   - Final solution highlighted
   - Verification row (Ax ≈ b, or A·A⁻¹ ≈ I)

### Dynamic JavaScript

| Function             | Trigger         | Action                                         |
|----------------------|-----------------|------------------------------------------------|
| `buildGrids()`       | `n` change       | Regenerate A grid and B row inputs              |
| `updateForm()`       | method change    | Show/hide B, tolerance, max_iter fields         |
| `submitSolve()`      | Solve button     | POST fetch to `/solve`, render response          |
| `renderSteps()`      | response received| Build step display with navigation              |
| `navigateStep(dir)`  | prev/next click  | Show previous/next step                         |

### Tailwind Integration

- CDN script: `<script src="https://cdn.tailwindcss.com"></script>`
- All styling via utility classes — no custom CSS file
- Matrix inputs styled as a grid matching mathematical notation
- Steps displayed in monospace cards with clear labeling

---

## Design Decisions

| Decision                      | Rationale                                              |
|-------------------------------|--------------------------------------------------------|
| Tailwind via CDN              | Zero build step, fast prototyping                      |
| No custom CSS file            | All styling inline via Tailwind utilities              |
| Dynamic input grids via JS    | Adapts to any n, no server round-trips for UI changes  |
| Unified step dict format      | Consistent rendering regardless of method              |
| Matrix Inverse hides B        | A⁻¹ computation doesn't need RHS vector                |
| x0 defaults to zeros          | No input field needed; reasonable default              |
| LU methods include solve      | Decompose + forward/back sub = full Ax=b solution      |
| Verification always computed  | Users can confirm correctness regardless of method     |

---

## Implementation Order

1. `solver.py` — All 8 solver functions
2. `app.py` — Flask server with `/` and `/solve` routes
3. `templates/index.html` — Full UI with Tailwind
4. Integration test — Run Flask, test each method via browser

---

## Dependencies

- Python 3.x
- Flask (`pip install flask`)
- NumPy (`pip install numpy`)
- Tailwind CSS (CDN, no install)