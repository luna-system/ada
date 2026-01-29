from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    TASK_ASSIGNMENT = "task_assignment"
    PROGRESS_UPDATE = "progress_update"
    PEER_REQUEST = "peer_request"
    DECOMPOSITION_REQUEST = "decomposition_request"


class TaskAssignment(BaseModel):
    """Task delegation from orchestrator to worker"""

    task_id: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class ProgressUpdate(BaseModel):
    """Worker status reports to orchestrator"""

    task_id: str
    status: str  # in_progress | blocked | completed | failed
    progress: float = 0.0
    artifacts: List[str] = Field(default_factory=list)
    thoughts: Optional[str] = None
    needs_help: bool = False


class PeerRequest(BaseModel):
    """Worker-to-worker collaboration request"""

    request_type: str  # code_review | context_share | dependency_check
    payload: Dict[str, Any] = Field(default_factory=dict)


class DecompositionRequest(BaseModel):
    """Request to break down complex tasks"""

    task_id: str
    reason: str
    suggested_subtasks: List[str] = Field(default_factory=list)


class A2AMessage(BaseModel):
    """Base message wrapper with metadata for A2A communication"""

    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Union[
        TaskAssignment,
        ProgressUpdate,
        PeerRequest,
        DecompositionRequest,
        Dict[str, Any],
    ]
