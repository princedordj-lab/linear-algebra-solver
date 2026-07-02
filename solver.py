"""
solver.py — Linear Algebra Solver Core Logic

Implements 8 numerical methods for solving linear systems (Ax = b) or
computing matrix inverses, each returning a step-by-step breakdown
suitable for display in a web UI.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_list(x):
    """Recursively convert numpy arrays/scalars to plain python lists/values."""
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


def _mat_list(M):
    return np.array(M, dtype=float).tolist()


def _verify_solution(A, x, b, tol=1e-6):
    A = np.array(A, dtype=float)
    x = np.array(x, dtype=float)
    b = np.array(b, dtype=float)
    actual = A @ x
    match = bool(np.allclose(actual, b, atol=1e-4))
    return {
        "expected": _to_list(b),
        "actual": _to_list(actual),
        "match": match,
    }


def _verify_inverse(A, A_inv):
    A = np.array(A, dtype=float)
    A_inv = np.array(A_inv, dtype=float)
    n = A.shape[0]
    I = np.eye(n)
    actual = A @ A_inv
    match = bool(np.allclose(actual, I, atol=1e-4))
    return {
        "expected": _to_list(I),
        "actual": _to_list(actual),
        "match": match,
    }


# ---------------------------------------------------------------------------
# 1. Gaussian Elimination — Partial Pivoting
# ---------------------------------------------------------------------------

def solve_gaussian_partial(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]
    aug = np.hstack([A, b.reshape(-1, 1)])

    steps = []
    steps.append({
        "label": "Initial Augmented Matrix",
        "matrix": _mat_list(aug),
    })

    for k in range(n - 1):
        # partial pivot: find max abs value in column k, at or below row k
        pivot_row = np.argmax(np.abs(aug[k:, k])) + k
        if pivot_row != k:
            aug[[k, pivot_row]] = aug[[pivot_row, k]]
            steps.append({
                "label": f"Swap Row {k+1} with Row {pivot_row+1} (Partial Pivot)",
                "matrix": _mat_list(aug),
            })

        if abs(aug[k, k]) < 1e-12:
            continue

        for i in range(k + 1, n):
            factor = aug[i, k] / aug[k, k]
            aug[i, k:] -= factor * aug[k, k:]

        steps.append({
            "label": f"Elimination Step {k+1}",
            "matrix": _mat_list(aug),
        })

    steps.append({
        "label": "Upper Triangular Form",
        "matrix": _mat_list(aug),
    })

    # back substitution
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if abs(aug[i, i]) < 1e-12:
            x[i] = 0.0
            continue
        x[i] = (aug[i, -1] - aug[i, i + 1:n] @ x[i + 1:n]) / aug[i, i]

    steps.append({
        "label": "Back Substitution — Solution",
        "matrix": _mat_list(aug),
        "vector": _to_list(x),
    })

    return {
        "solution": _to_list(x),
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 2. Gaussian Elimination — Complete Pivoting
# ---------------------------------------------------------------------------

def solve_gaussian_complete(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]
    aug = np.hstack([A, b.reshape(-1, 1)])
    col_order = list(range(n))  # tracks original column identities for x

    steps = []
    steps.append({
        "label": "Initial Augmented Matrix",
        "matrix": _mat_list(aug),
        "extra": {"colOrder": [c + 1 for c in col_order]},
    })

    for k in range(n - 1):
        # complete pivot: find max abs value in submatrix aug[k:, k:n]
        sub = np.abs(aug[k:n, k:n])
        idx = np.unravel_index(np.argmax(sub), sub.shape)
        pivot_row, pivot_col = idx[0] + k, idx[1] + k

        if pivot_row != k:
            aug[[k, pivot_row]] = aug[[pivot_row, k]]
        if pivot_col != k:
            aug[:, [k, pivot_col]] = aug[:, [pivot_col, k]]
            col_order[k], col_order[pivot_col] = col_order[pivot_col], col_order[k]

        if pivot_row != k or pivot_col != k:
            steps.append({
                "label": f"Swap Row {pivot_row+1}->{k+1}, Col {pivot_col+1}->{k+1} (Complete Pivot)",
                "matrix": _mat_list(aug),
                "extra": {"colOrder": [c + 1 for c in col_order]},
            })

        if abs(aug[k, k]) < 1e-12:
            continue

        for i in range(k + 1, n):
            factor = aug[i, k] / aug[k, k]
            aug[i, k:] -= factor * aug[k, k:]

        steps.append({
            "label": f"Elimination Step {k+1}",
            "matrix": _mat_list(aug),
            "extra": {"colOrder": [c + 1 for c in col_order]},
        })

    steps.append({
        "label": "Upper Triangular Form",
        "matrix": _mat_list(aug),
        "extra": {"colOrder": [c + 1 for c in col_order]},
    })

    # back substitution (produces solution in permuted variable order)
    y = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if abs(aug[i, i]) < 1e-12:
            y[i] = 0.0
            continue
        y[i] = (aug[i, -1] - aug[i, i + 1:n] @ y[i + 1:n]) / aug[i, i]

    # reorder y back to original variable order using col_order
    x = np.zeros(n)
    for permuted_idx, original_idx in enumerate(col_order):
        x[original_idx] = y[permuted_idx]

    steps.append({
        "label": "Back Substitution + Reordering — Solution",
        "matrix": _mat_list(aug),
        "vector": _to_list(x),
        "extra": {"colOrder": [c + 1 for c in col_order]},
    })

    return {
        "solution": _to_list(x),
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 3. Gauss-Jordan Elimination
# ---------------------------------------------------------------------------

def solve_gauss_jordan(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]
    aug = np.hstack([A, b.reshape(-1, 1)])

    steps = []
    steps.append({
        "label": "Initial Augmented Matrix",
        "matrix": _mat_list(aug),
    })

    for k in range(n):
        # partial pivot for stability
        pivot_row = np.argmax(np.abs(aug[k:, k])) + k
        if pivot_row != k:
            aug[[k, pivot_row]] = aug[[pivot_row, k]]
            steps.append({
                "label": f"Swap Row {k+1} with Row {pivot_row+1}",
                "matrix": _mat_list(aug),
            })

        if abs(aug[k, k]) < 1e-12:
            continue

        aug[k, :] = aug[k, :] / aug[k, k]
        steps.append({
            "label": f"Normalize Row {k+1} (Pivot -> 1)",
            "matrix": _mat_list(aug),
        })

        for i in range(n):
            if i != k and abs(aug[i, k]) > 1e-15:
                factor = aug[i, k]
                aug[i, :] -= factor * aug[k, :]

        steps.append({
            "label": f"Eliminate Column {k+1} (Above & Below)",
            "matrix": _mat_list(aug),
        })

    x = aug[:, -1]

    steps.append({
        "label": "Reduced Row Echelon Form (RREF) — Solution",
        "matrix": _mat_list(aug),
        "vector": _to_list(x),
    })

    return {
        "solution": _to_list(x),
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 4. Matrix Inverse via Gauss-Jordan
# ---------------------------------------------------------------------------

def solve_matrix_inverse(A, b=None):
    A = np.array(A, dtype=float)
    n = A.shape[0]
    I = np.eye(n)
    aug = np.hstack([A, I])

    steps = []
    steps.append({
        "label": "Augmented Matrix [A | I]",
        "matrix": _mat_list(aug),
    })

    singular = False
    for k in range(n):
        pivot_row = np.argmax(np.abs(aug[k:, k])) + k
        if pivot_row != k:
            aug[[k, pivot_row]] = aug[[pivot_row, k]]
            steps.append({
                "label": f"Swap Row {k+1} with Row {pivot_row+1}",
                "matrix": _mat_list(aug),
            })

        if abs(aug[k, k]) < 1e-12:
            singular = True
            continue

        aug[k, :] = aug[k, :] / aug[k, k]
        steps.append({
            "label": f"Normalize Row {k+1} (Pivot -> 1)",
            "matrix": _mat_list(aug),
        })

        for i in range(n):
            if i != k and abs(aug[i, k]) > 1e-15:
                factor = aug[i, k]
                aug[i, :] -= factor * aug[k, :]

        steps.append({
            "label": f"Eliminate Column {k+1}",
            "matrix": _mat_list(aug),
        })

    A_inv = aug[:, n:]

    steps.append({
        "label": "Result — [I | A⁻¹]",
        "matrix": _mat_list(aug),
    })

    verification = _verify_inverse(A, A_inv) if not singular else {
        "expected": _to_list(I),
        "actual": _to_list(A_inv),
        "match": False,
    }

    return {
        "solution": _mat_list(A_inv),
        "steps": steps,
        "verification": verification,
    }


# ---------------------------------------------------------------------------
# 5. Jacobi Iterative Method
# ---------------------------------------------------------------------------

def solve_jacobi(A, b, x0=None, tol=1e-6, max_iter=100):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]
    x = np.zeros(n) if x0 is None else np.array(x0, dtype=float)

    steps = []
    steps.append({
        "label": "Initial Guess",
        "x": _to_list(x),
        "residual": float(np.linalg.norm(A @ x - b)),
        "delta": None,
    })

    converged = False
    iterations = 0

    for it in range(1, max_iter + 1):
        x_new = np.zeros(n)
        components = []
        for i in range(n):
            s = 0.0
            for j in range(n):
                if j != i:
                    s += A[i, j] * x[j]
            if abs(A[i, i]) < 1e-12:
                x_new[i] = 0.0
            else:
                x_new[i] = (b[i] - s) / A[i, i]
            components.append({
                "row": i + 1,
                "sum_others": float(s),
                "value": float(x_new[i]),
            })

        delta = float(np.linalg.norm(x_new - x))
        residual = float(np.linalg.norm(A @ x_new - b))

        steps.append({
            "label": f"Iteration {it}",
            "x": _to_list(x_new),
            "residual": residual,
            "delta": delta,
            "extra": {"components": components},
        })

        x = x_new
        iterations = it

        if delta < tol:
            converged = True
            break

    return {
        "solution": _to_list(x),
        "iterations": iterations,
        "converged": converged,
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 6. Gauss-Seidel Iterative Method
# ---------------------------------------------------------------------------

def solve_gauss_seidel(A, b, x0=None, tol=1e-6, max_iter=100):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]
    x = np.zeros(n) if x0 is None else np.array(x0, dtype=float)

    steps = []
    steps.append({
        "label": "Initial Guess",
        "x": _to_list(x),
        "residual": float(np.linalg.norm(A @ x - b)),
        "delta": None,
    })

    converged = False
    iterations = 0

    for it in range(1, max_iter + 1):
        x_old = x.copy()
        components = []
        for i in range(n):
            lower_sum = 0.0
            for j in range(i):
                lower_sum += A[i, j] * x[j]  # already updated this iteration
            upper_sum = 0.0
            for j in range(i + 1, n):
                upper_sum += A[i, j] * x[j]  # still from previous iteration

            if abs(A[i, i]) < 1e-12:
                new_val = 0.0
            else:
                new_val = (b[i] - lower_sum - upper_sum) / A[i, i]

            components.append({
                "row": i + 1,
                "lower_sum": float(lower_sum),
                "upper_sum": float(upper_sum),
                "value": float(new_val),
            })

            x[i] = new_val  # in-place update — used immediately in later rows

        delta = float(np.linalg.norm(x - x_old))
        residual = float(np.linalg.norm(A @ x - b))

        steps.append({
            "label": f"Iteration {it}",
            "x": _to_list(x),
            "residual": residual,
            "delta": delta,
            "extra": {"components": components},
        })

        iterations = it

        if delta < tol:
            converged = True
            break

    return {
        "solution": _to_list(x),
        "iterations": iterations,
        "converged": converged,
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 7. LU Decomposition — Doolittle (L has 1s on diagonal)
# ---------------------------------------------------------------------------

def solve_lu_doolittle(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]

    L = np.eye(n)
    U = np.zeros((n, n))

    steps = []
    steps.append({
        "label": "Initial L (identity diagonal) and U (zeros)",
        "matrix": _mat_list(np.hstack([L, U])),
    })

    for i in range(n):
        # U row i
        for j in range(i, n):
            U[i, j] = A[i, j] - L[i, :i] @ U[:i, j]
        # L column i (below diagonal)
        for j in range(i + 1, n):
            if abs(U[i, i]) < 1e-12:
                L[j, i] = 0.0
            else:
                L[j, i] = (A[j, i] - L[j, :i] @ U[:i, i]) / U[i, i]

        steps.append({
            "label": f"Fill Row {i+1} of U, Column {i+1} of L",
            "matrix": _mat_list(np.hstack([L, U])),
        })

    steps.append({
        "label": "Completed L and U Matrices",
        "matrix": _mat_list(np.hstack([L, U])),
        "extra": {"L": _mat_list(L), "U": _mat_list(U)},
    })

    # forward substitution: Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - L[i, :i] @ y[:i]

    steps.append({
        "label": "Forward Substitution (Ly = b)",
        "matrix": _mat_list(np.hstack([L, U])),
        "vector": _to_list(y),
    })

    # back substitution: Ux = y
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if abs(U[i, i]) < 1e-12:
            x[i] = 0.0
        else:
            x[i] = (y[i] - U[i, i + 1:] @ x[i + 1:]) / U[i, i]

    steps.append({
        "label": "Back Substitution (Ux = y) — Solution",
        "matrix": _mat_list(np.hstack([L, U])),
        "vector": _to_list(x),
    })

    return {
        "solution": _to_list(x),
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# 8. LU Decomposition — Crout (U has 1s on diagonal)
# ---------------------------------------------------------------------------

def solve_lu_crout(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]

    L = np.zeros((n, n))
    U = np.eye(n)

    steps = []
    steps.append({
        "label": "Initial L (zeros) and U (identity diagonal)",
        "matrix": _mat_list(np.hstack([L, U])),
    })

    for j in range(n):
        # L column j (at and below diagonal)
        for i in range(j, n):
            L[i, j] = A[i, j] - L[i, :j] @ U[:j, j]
        # U row j (right of diagonal) — with division
        for i in range(j + 1, n):
            if abs(L[j, j]) < 1e-12:
                U[j, i] = 0.0
            else:
                U[j, i] = (A[j, i] - L[j, :j] @ U[:j, i]) / L[j, j]

        steps.append({
            "label": f"Fill Column {j+1} of L, Row {j+1} of U",
            "matrix": _mat_list(np.hstack([L, U])),
        })

    steps.append({
        "label": "Completed L and U Matrices",
        "matrix": _mat_list(np.hstack([L, U])),
        "extra": {"L": _mat_list(L), "U": _mat_list(U)},
    })

    # forward substitution: Ly = b (with division, since L diagonal != 1)
    y = np.zeros(n)
    for i in range(n):
        if abs(L[i, i]) < 1e-12:
            y[i] = 0.0
        else:
            y[i] = (b[i] - L[i, :i] @ y[:i]) / L[i, i]

    steps.append({
        "label": "Forward Substitution (Ly = b, with division)",
        "matrix": _mat_list(np.hstack([L, U])),
        "vector": _to_list(y),
    })

    # back substitution: Ux = y (no division, since U diagonal == 1)
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = y[i] - U[i, i + 1:] @ x[i + 1:]

    steps.append({
        "label": "Back Substitution (Ux = y, no division) — Solution",
        "matrix": _mat_list(np.hstack([L, U])),
        "vector": _to_list(x),
    })

    return {
        "solution": _to_list(x),
        "steps": steps,
        "verification": _verify_solution(A, x, b),
    }


# ---------------------------------------------------------------------------
# Matrix Properties: Determinant, Eigenvalues, Rank
# ---------------------------------------------------------------------------

def compute_properties(A):
    """Compute determinant, eigenvalues, and rank of a square matrix."""
    A = np.array(A, dtype=float)
    n = A.shape[0]

    if A.shape[0] != A.shape[1]:
        raise ValueError("Properties require a square matrix")

    det = float(np.linalg.det(A))
    eigvals_complex = np.linalg.eigvals(A)
    eigvals = eigvals_complex.real.tolist()
    rank = int(np.linalg.matrix_rank(A, tol=1e-9))

    steps = [
        {"label": "Matrix Input", "matrix": _mat_list(A)},
        {"label": f"Determinant: det(A) = {det:.6g}", "extra": {"determinant": det}},
        {"label": f"Rank: rank(A) = {rank} (of {n})", "extra": {"rank": rank, "size": n}},
        {"label": f"Eigenvalues: λ = [{', '.join(f'{v:.6g}' for v in eigvals)}]", "extra": {"eigenvalues": eigvals}},
    ]

    return {
        "solution": {
            "determinant": det,
            "rank": rank,
            "size": n,
            "eigenvalues": eigvals,
        },
        "steps": steps,
    }


# ---------------------------------------------------------------------------
# Method Registry
# ---------------------------------------------------------------------------

MATRIX_METHODS = {
    "gaussian_partial":  solve_gaussian_partial,
    "gaussian_complete": solve_gaussian_complete,
    "gauss_jordan":      solve_gauss_jordan,
    "matrix_inverse":    solve_matrix_inverse,
    "jacobi":            solve_jacobi,
    "gauss_seidel":      solve_gauss_seidel,
    "lu_doolittle":      solve_lu_doolittle,
    "lu_crout":          solve_lu_crout,
    "matrix_properties": compute_properties,
}

ITERATIVE_METHODS = {"jacobi", "gauss_seidel"}
NO_B_METHODS = {"matrix_inverse"}
