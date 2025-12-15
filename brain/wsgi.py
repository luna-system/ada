"""
WSGI entry point for Ada brain service.

This module is the standard entry point for production deployments.
Gunicorn/Uvicorn will import and run the `app` object from here.
"""
import sys
import os

# Ensure the brain module is importable
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == '__main__':
    app.run()
