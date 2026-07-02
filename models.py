"""
models.py — Database models for LinSolve auth and user data.
"""

import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "linsolve.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            reset_token TEXT,
            reset_expires TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, key)
        );
    """)
    conn.commit()
    conn.close()


class User(UserMixin):
    def __init__(self, id, email, username, password_hash, reset_token=None, reset_expires=None, created_at=None):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.reset_token = reset_token
        self.reset_expires = reset_expires
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return User(**row) if row else None

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        return User(**row) if row else None

    @staticmethod
    def get_by_username(username):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        return User(**row) if row else None

    @staticmethod
    def create(email, username, password):
        password_hash = generate_password_hash(password)
        created_at = datetime.utcnow().isoformat()
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (email, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, username, password_hash, created_at),
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return User.get_by_id(user_id)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET reset_token = ?, reset_expires = ? WHERE id = ?",
            (self.reset_token, self.reset_expires, self.id),
        )
        conn.commit()
        conn.close()

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_expires = None
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET reset_token = NULL, reset_expires = NULL WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()


def get_user_data(user_id, key, default=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM user_data WHERE user_id = ? AND key = ?", (user_id, key))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default


def set_user_data(user_id, key, value):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_data (user_id, key, value, updated_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
        (user_id, key, value, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()