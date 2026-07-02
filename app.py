"""
app.py — Flask server for the Linear Algebra Solver web app.
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import secrets

from solver import MATRIX_METHODS, ITERATIVE_METHODS, NO_B_METHODS
from models import get_db, init_db, User, get_user_data, set_user_data
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user as flask_logout_user, login_user as flask_login_user, current_user as flask_current_user

app = Flask(__name__)
app.secret_key = "linsolve-secret-key-change-in-production"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


with app.app_context():
    init_db()

NO_B_METHODS = NO_B_METHODS | {"matrix_properties"}


# Auth helpers
def current_user():
    uid = session.get("user_id")
    return User.get_by_id(uid) if uid else None


def login_user(user_id):
    session["user_id"] = user_id
    session.permanent = True


def logout_user():
    session.pop("user_id", None)


# Auth API routes
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = User.get_by_email(email) or User.get_by_username(email)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    login_user(user.id)
    return jsonify({"user": {"id": user.id, "email": user.email, "username": user.username}})


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not email or not username or not password:
        return jsonify({"error": "All fields are required"}), 400
    if User.get_by_email(email) or User.get_by_username(username):
        return jsonify({"error": "Email or username already exists"}), 409
    user = User.create(email=email, username=username, password=password)
    login_user(user.id)
    return jsonify({"user": {"id": user.id, "email": user.email, "username": user.username}})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    logout_user()
    return jsonify({"ok": True})


@app.route("/api/auth/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"user": None})
    return jsonify({"user": {"id": user.id, "email": user.email, "username": user.username}})


@app.route("/api/auth/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    user = User.get_by_email(email)
    if not user:
        return jsonify({"ok": True})
    token = secrets.token_urlsafe(32)
    expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET reset_token = ?, reset_expires = ? WHERE id = ?", (token, expires, user.id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "token": token})


@app.route("/api/auth/reset-password", methods=["POST"])
def api_reset_password():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("token", "")
    password = data.get("password", "")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE reset_token = ?", (token,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Invalid token"}), 400
    expires = datetime.fromisoformat(row["reset_expires"])
    if datetime.utcnow() > expires:
        conn.close()
        return jsonify({"error": "Token expired"}), 400
    password_hash = generate_password_hash(password)
    c.execute("UPDATE users SET password_hash = ?, reset_token = NULL, reset_expires = NULL WHERE id = ?", (password_hash, row["id"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/auth/profile", methods=["PUT"])
def api_update_profile():
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", (username, email, user.id))
    conn.commit()
    conn.close()
    updated = User.get_by_id(user.id)
    return jsonify({"user": {"id": updated.id, "email": updated.email, "username": updated.username}})


@app.route("/api/auth/password", methods=["PUT"])
def api_change_password():
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.get_json(force=True, silent=True) or {}
    current_password = data.get("current_password", "")
    new_password = data.get("password", "")
    if not current_password or not new_password:
        return jsonify({"error": "Current and new password are required"}), 400
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 400
    password_hash = generate_password_hash(new_password)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user.id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# Public pages
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth")
def auth_page():
    return render_template("auth.html")


@app.route("/settings")
def settings_page():
    return render_template("settings.html")


# Solver API
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
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


# Feature pages
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