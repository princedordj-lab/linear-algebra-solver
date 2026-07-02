"""
app.py — Flask server for the Linear Algebra Solver web app.
"""

from flask import Flask, render_template, request, jsonify

from solver import MATRIX_METHODS, ITERATIVE_METHODS, NO_B_METHODS

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True, silent=True) or {}

    method = data.get("method")
    A = data.get("A")
    b = data.get("b")
    tol = data.get("tol", 1e-6)
    max_iter = data.get("max_iter", 100)

    if method not in MATRIX_METHODS:
        return jsonify({"error": f"Unknown method: {method}"}), 400

    if A is None:
        return jsonify({"error": "Matrix A is required"}), 400

    try:
        tol = float(tol)
    except (TypeError, ValueError):
        tol = 1e-6

    try:
        max_iter = int(max_iter)
    except (TypeError, ValueError):
        max_iter = 100

    solver_fn = MATRIX_METHODS[method]

    try:
        if method in NO_B_METHODS:
            result = solver_fn(A)
        elif method in ITERATIVE_METHODS:
            if b is None:
                return jsonify({"error": "Vector b is required for this method"}), 400
            result = solver_fn(A, b, x0=None, tol=tol, max_iter=max_iter)
        else:
            if b is None:
                return jsonify({"error": "Vector b is required for this method"}), 400
            result = solver_fn(A, b)
    except Exception as exc:  # noqa: BLE001 - surface solver errors to client
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
