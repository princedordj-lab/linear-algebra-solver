"""
Vercel serverless entry point — wraps the Flask app as a WSGI callable.
"""
import sys
import os

# Add the project root to sys.path so imports (solver, templates) resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel Python runtime looks for a `handler` or `app` callable
handler = app