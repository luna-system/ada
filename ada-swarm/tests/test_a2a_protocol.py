import pytest
from datetime import datetime
from hypothesis import given, strategies as st
from pydantic import ValidationError
from ada_swarm.a2a.protocol import (
    A2AMessage,
    MessageType,
    TaskAssignment,
    ProgressUpdate,
    PeerRequest,
    DecompositionRequest,
)


def test_task_assignment_serialization():
    data = {
        "task_id": "task_1",
        "description": "Test task",
        "context": {"key": "value"},
        "constraints": {"timeout": 30},
    }
    task = TaskAssignment(**data)
    assert task.task_id == "task_1"
    assert task.description == "Test task"
    assert task.context["key"] == "value"
    assert task.model_dump() == data


def test_progress_update_serialization():
    data = {
        "task_id": "task_1",
        "status": "in_progress",
        "progress": 0.5,
        "artifacts": ["file1.txt"],
        "thoughts": "Working on it",
        "needs_help": False,
    }
    update = ProgressUpdate(**data)
    assert update.status == "in_progress"
    assert update.progress == 0.5
    assert update.model_dump() == data


def test_a2a_message_wrapper():
    task_data = {"task_id": "task_123", "description": "Do something"}
    task = TaskAssignment(**task_data)

    msg = A2AMessage(
        from_agent="orchestrator",
        to_agent="worker_1",
        message_type=MessageType.TASK_ASSIGNMENT,
        payload=task,
    )

    assert msg.from_agent == "orchestrator"
    assert msg.to_agent == "worker_1"
    assert msg.message_type == MessageType.TASK_ASSIGNMENT
    assert isinstance(msg.payload, TaskAssignment)
    assert msg.payload.task_id == "task_123"
    assert msg.id.startswith("msg_")
    assert isinstance(msg.timestamp, datetime)


@given(st.text(min_size=1), st.text())
def test_task_assignment_hypothesis(task_id, description):
    task = TaskAssignment(task_id=task_id, description=description)
    assert task.task_id == task_id
    assert task.description == description


@given(
    st.text(min_size=1),
    st.sampled_from(["in_progress", "blocked", "completed", "failed"]),
    st.floats(min_value=0.0, max_value=1.0),
    st.lists(st.text()),
    st.one_of(st.none(), st.text()),
    st.booleans(),
)
def test_progress_update_hypothesis(
    task_id, status, progress, artifacts, thoughts, needs_help
):
    update = ProgressUpdate(
        task_id=task_id,
        status=status,
        progress=progress,
        artifacts=artifacts,
        thoughts=thoughts,
        needs_help=needs_help,
    )
    assert update.task_id == task_id
    assert update.status == status
    assert update.progress == progress
    assert update.artifacts == artifacts
    assert update.thoughts == thoughts
    assert update.needs_help == needs_help
