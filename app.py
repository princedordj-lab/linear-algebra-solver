"""
app.py — Flask server for the Linear Algebra Solver web app.
"""

from flask import Flask, render_template, request, jsonify

from solver import MATRIX_METHODS, ITERATIVE_METHODS, NO_B_METHODS

NO_B_METHODS = NO_B_METHODS | {"matrix_properties"}

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


@app.route("/solver")
def solver_page():
    return render_template("solver.html")


@app.route("/presets")
def presets_page():
    return render_template("presets.html")


@app.route("/compare")
def compare_page():
    return render_template("compare.html")


@app.route("/visualize")
def visualize_page():
    return render_template("visualize.html")


@app.route("/history")
def history_page():
    return render_template("history.html")


@app.route("/convergence")
def convergence_page():
    return render_template("convergence.html")


@app.route("/paste")
def paste_page():
    return render_template("paste.html")


@app.route("/share")
def share_page():
    return render_template("share.html")


@app.route("/properties")
def properties_page():
    return render_template("properties.html")


if __name__ == "__main__":
    app.run(debug=True)
