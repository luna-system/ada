"""
Minimal schemas for Ada v4.0 clean kernel.
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool
    service: str
    python: str
    config: Dict[str, Any]


# Dummy ChatRequest for imports (not actually used)
class ChatRequest(BaseModel):
    """Chat request (not used in clean kernel)."""
    message: str
    conversation_id: Optional[str] = None
