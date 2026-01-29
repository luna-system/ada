"""
A2A Protocol Models

Agent-to-Agent communication message types and schemas.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """A2A message types."""
    TASK_ASSIGNMENT = "task_assignment"
    PROGRESS_UPDATE = "progress_update"
    PEER_REQUEST = "peer_request"
    DECOMPOSITION_REQUEST = "decomposition_request"
    TASK_RESULT = "task_result"
    ERROR = "error"


class A2AMessage(BaseModel):
    """Base A2A message structure."""
    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.now)
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]


class TaskAssignment(BaseModel):
    """Task assignment from orchestrator to worker."""
    task_id: str
    description: str
    context: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


class ProgressUpdate(BaseModel):
    """Progress update from worker to orchestrator."""
    task_id: str
    status: str  # "in_progress", "blocked", "completed", "failed"
    progress: float = 0.0
    artifacts: Optional[List[str]] = None
    thoughts: Optional[str] = None
    needs_help: bool = False


class TaskResult(BaseModel):
    """Final task result."""
    task_id: str
    status: str
    results: Any
    artifacts: Optional[List[str]] = None


class PeerRequest(BaseModel):
    """Peer-to-peer request between workers."""
    from_agent: str
    to_agent: str
    request_type: str  # "code_review", "context_share", "dependency_check"
    payload: Dict[str, Any]


class DecompositionRequest(BaseModel):
    """Request to decompose a complex task."""
    task_id: str
    reason: str
    suggested_subtasks: Optional[List[str]] = None
