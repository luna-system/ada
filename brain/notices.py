# brain/notices.py
"""
In-memory system notice manager for Ada backend.
Supports TTL, deduplication, and acknowledgement.
"""
import threading
import time
import uuid
from typing import List, Optional, Dict, Any
import os
import json

class Notice:
    def __init__(self, severity: str, component: str, code: str, message: str):
        self.id = str(uuid.uuid4())
        self.severity = severity  # e.g. 'warning', 'error', 'info'
        self.component = component  # e.g. 'backup', 'chroma', 'api'
        self.code = code  # e.g. 'backup.duplicate', 'chroma.heartbeat_failed'
        self.message = message
        self.created_at = int(time.time())
        self.acknowledged = False
        self.ack_by = None
        self.ack_at = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'severity': self.severity,
            'component': self.component,
            'code': self.code,
            'message': self.message,
            'created_at': self.created_at,
            'acknowledged': self.acknowledged,
            'ack_by': self.ack_by,
            'ack_at': self.ack_at,
        }

class NoticeManager:
    def __init__(self):
        self._notices: Dict[str, Notice] = {}
        self._lock = threading.Lock()
        # Optional persistence file shared between processes
        self._persist_file = os.getenv('NOTICE_PERSIST_FILE', '/data/brain_notices.json')
        # Try to load persisted notices if available
        try:
            if os.path.exists(self._persist_file):
                with open(self._persist_file, 'r') as fh:
                    data = json.load(fh)
                    for n in data:
                        note = Notice(n['severity'], n['component'], n['code'], n['message'], n.get('ttl', 3600))
                        note.id = n.get('id', note.id)
                        note.created_at = n.get('created_at', note.created_at)
                        note.acknowledged = n.get('acknowledged', False)
                        note.ack_by = n.get('ack_by')
                        note.ack_at = n.get('ack_at')
                        self._notices[note.id] = note
        except Exception:
            # Don't let persistence failures stop the manager
            pass

    def add_notice(self, severity: str, component: str, code: str, message: str) -> str:
        with self._lock:
            # Deduplicate by (component, code, message)
            for n in self._notices.values():
                if (n.component, n.code, n.message) == (component, code, message):
                    return n.id
            notice = Notice(severity, component, code, message)
            self._notices[notice.id] = notice
            self._persist()
            return notice.id

    def list_notices(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Return all notices (or only non-acknowledged if active_only=True)."""
        # Reload from file to pick up notices from other workers
        self._load_from_file()
        with self._lock:
            notices = list(self._notices.values())
            if active_only:
                notices = [n for n in notices if not n.acknowledged]
            return [n.to_dict() for n in notices]
    
    def _load_from_file(self):
        """Load notices from persistence file, updating existing notices with persisted state."""
        try:
            if os.path.exists(self._persist_file):
                with open(self._persist_file, 'r') as fh:
                    data = json.load(fh)
                    for n in data:
                        note_id = n.get('id')
                        if note_id in self._notices:
                            # Update existing notice with persisted state (e.g., acknowledgement)
                            self._notices[note_id].acknowledged = n.get('acknowledged', False)
                            self._notices[note_id].ack_by = n.get('ack_by')
                            self._notices[note_id].ack_at = n.get('ack_at')
                        else:
                            # Add new notice from file
                            note = Notice(n['severity'], n['component'], n['code'], n['message'])
                            note.id = note_id
                            note.created_at = n.get('created_at', note.created_at)
                            note.acknowledged = n.get('acknowledged', False)
                            note.ack_by = n.get('ack_by')
                            note.ack_at = n.get('ack_at')
                            self._notices[note.id] = note
        except Exception:
            pass

    def acknowledge(self, notice_id: str, ack_by: Optional[str] = None) -> bool:
        with self._lock:
            n = self._notices.get(notice_id)
            if n and not n.acknowledged:
                n.acknowledged = True
                n.ack_by = ack_by
                n.ack_at = int(time.time())
                self._persist()
                return True
            return False

    def clear_notice(self, notice_id: str) -> bool:
        with self._lock:
            if notice_id in self._notices:
                del self._notices[notice_id]
                self._persist()
                return True
            return False

    def _persist(self):
        try:
            data = [n.to_dict() for n in self._notices.values()]
            tmp = self._persist_file + '.tmp'
            with open(tmp, 'w') as fh:
                json.dump(data, fh)
            os.replace(tmp, self._persist_file)
        except Exception:
            # best effort
            pass

# Singleton instance
notice_manager = NoticeManager()
