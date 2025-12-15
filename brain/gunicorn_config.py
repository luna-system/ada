# Gunicorn configuration for Ada brain service (with FastAPI/Uvicorn)
# Usage: gunicorn -c gunicorn_config.py wsgi:app

import os
import multiprocessing

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:7000")
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")  # FastAPI requires ASGI
worker_connections = 1000
timeout = int(os.getenv("GUNICORN_TIMEOUT", "300"))  # 5 min for LLM calls
keepalive = 5

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ada-brain"

# Server hooks for graceful shutdown
def on_starting(server):
    """Called before the master process is initialized."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    print("[BRAIN] Server is ready. Spawning workers")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("[BRAIN] Server shutting down")
