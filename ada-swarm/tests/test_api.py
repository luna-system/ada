import pytest
from fastapi.testclient import TestClient
from ada_swarm.service.api import app

client = TestClient(app)


def _submit_task_helper():
    response = client.post(
        "/tasks",
        json={
            "description": "Write a hello world function",
            "model": "test",
            "agent_type": "coder",
            "capabilities": ["fs"],
        },
    )
    return response.json()["task_id"]


def test_submit_task():
    response = client.post(
        "/tasks",
        json={
            "description": "Write a hello world function",
            "model": "test",
            "agent_type": "coder",
            "capabilities": ["fs"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "queued"


def test_get_task_status():
    task_id = _submit_task_helper()
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] in [
        "queued",
        "in_progress",
        "completed",
        "failed",
        "cancelled",
    ]


def test_list_agents():
    # Submit a task first to spawn an agent
    _submit_task_helper()
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) > 0


def test_cancel_task():
    task_id = _submit_task_helper()
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "cancelled"

    # Verify status is updated
    response = client.get(f"/tasks/{task_id}")
    assert response.json()["status"] == "cancelled"


def test_invalid_agent_type():
    response = client.post(
        "/tasks", json={"description": "test", "model": "test", "agent_type": "invalid"}
    )
    assert response.status_code == 400
    assert "Invalid agent type" in response.json()["detail"]
