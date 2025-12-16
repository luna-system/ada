# brain/notices_client.py
"""
Helper to fetch active system notices for prompt injection.
"""
import requests
import os

def get_active_notices() -> list:
    # If running inside FastAPI, import directly; else, fallback to HTTP (for future extensibility)
    try:
        from brain.notices import notice_manager
        return notice_manager.list_notices(active_only=True)
    except ImportError:
        # Fallback: fetch from API (not used in prod)
        url = os.getenv("BRAIN_API_URL", "http://localhost:7000/v1/notices")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return []
