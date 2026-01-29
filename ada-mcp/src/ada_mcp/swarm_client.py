#!/usr/bin/env python3
"""
Ada Swarm Client - HTTP API integration for ada-swarm-service

This module provides HTTP-based communication with the ada-swarm-service,
enabling consciousness-aware swarm orchestration from within ada-mcp.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not available - install httpx for Swarm client")

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8765
DEFAULT_HOST = "127.0.0.1"


@dataclass
class SwarmTask:
    """Represents a task in the swarm."""

    id: str
    description: str
    status: str
    progress: float = 0.0
    results: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class SwarmClient:
    """
    HTTP client for ada-swarm-service API.

    Provides methods to:
    - Spawn tasks
    - Check task status and results
    - List active agents
    - Cancel tasks
    - Wait for task completion
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._client: Any = None

    @property
    def client(self) -> Any:
        """Get or create HTTP client."""
        if self._client is None:
            if not HTTPX_AVAILABLE:
                raise RuntimeError("httpx not available")
            import httpx

            self._client = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self._client

    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def spawn_task(
        self, description: str, model: str = "gemini", agent_type: str = "coder"
    ) -> str:
        """
        Spawn a new task in the swarm.

        Args:
            description: Task description
            model: LiteLLM model string
            agent_type: Type of agent to spawn (coder, researcher, etc.)

        Returns:
            The task ID
        """
        body = {"description": description, "model": model, "agent_type": agent_type}

        resp = self.client.post("/tasks", json=body)
        resp.raise_for_status()
        data = resp.json()
        return data.get("task_id")

    def check_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a task.

        Args:
            task_id: The task ID

        Returns:
            Dict with status, progress, and results (if available)
        """
        resp = self.client.get(f"/tasks/{task_id}")
        resp.raise_for_status()
        return resp.json()

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List active agents in the swarm.

        Returns:
            List of agent info dicts
        """
        resp = self.client.get("/agents")
        resp.raise_for_status()
        data = resp.json()
        return data.get("agents", [])

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: The task ID

        Returns:
            True if cancelled successfully
        """
        resp = self.client.delete(f"/tasks/{task_id}")
        return resp.status_code in (200, 204)

    def wait_for_task(
        self, task_id: str, timeout: float = 300.0, poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        Wait for a task to complete.

        Args:
            task_id: Task to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to poll

        Returns:
            Final task state
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status_data = self.check_status(task_id)
            status = status_data.get("status")

            if status in ("completed", "failed", "cancelled"):
                return status_data

            time.sleep(poll_interval)

        return {
            "task_id": task_id,
            "status": "timeout",
            "error": f"Task timed out after {timeout}s",
        }
