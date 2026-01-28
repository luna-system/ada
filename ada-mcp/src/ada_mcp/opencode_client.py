#!/usr/bin/env python3
"""
Ada OpenCode Client - HTTP API integration for OpenCode subagents

This module provides HTTP-based communication with OpenCode servers,
enabling swarm orchestration from within ada-mcp.

Uses the OpenCode REST API (opencode serve) for reliable, synchronous
agent interactions.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not available - install httpx for OpenCode client")

logger = logging.getLogger(__name__)

DEFAULT_PORT = 4096
DEFAULT_HOST = "127.0.0.1"


@dataclass
class OpenCodeSession:
    """Represents an OpenCode session."""
    id: str
    title: Optional[str] = None
    model: Optional[str] = None
    created_at: Optional[str] = None


class OpenCodeClient:
    """
    HTTP client for OpenCode server API.
    
    Provides methods to:
    - Create and manage sessions
    - Send prompts and receive responses
    - Execute commands
    - Monitor server health
    """
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> "httpx.Client":
        """Get or create HTTP client."""
        if self._client is None:
            if not HTTPX_AVAILABLE:
                raise RuntimeError("httpx not available")
            self._client = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self._client
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        try:
            resp = self.client.get("/global/health")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        resp = self.client.get("/session")
        resp.raise_for_status()
        return resp.json()
    
    def create_session(self, title: Optional[str] = None) -> OpenCodeSession:
        """Create a new session."""
        body = {}
        if title:
            body["title"] = title
        
        resp = self.client.post("/session", json=body)
        resp.raise_for_status()
        data = resp.json()
        
        return OpenCodeSession(
            id=data.get("id"),
            title=data.get("title"),
            created_at=data.get("createdAt"),
        )
    
    def send_message(
        self,
        session_id: str,
        text: str,
        provider_id: str = "google",
        model_id: str = "gemini-2.5-flash",
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a session and wait for response.
        
        Args:
            session_id: The session ID
            text: The message text
            provider_id: Provider ID (e.g., "google", "anthropic", "ollama")
            model_id: Model ID (e.g., "gemini-2.5-flash", "granite4:3b")
            agent: Optional agent to use
        
        Returns:
            Response containing message info and parts
        """
        body = {
            "model": {
                "providerID": provider_id,
                "modelID": model_id,
            },
            "parts": [
                {"type": "text", "text": text}
            ],
        }
        
        if agent:
            body["agent"] = agent
        
        resp = self.client.post(
            f"/session/{session_id}/message",
            json=body,
        )
        resp.raise_for_status()
        return resp.json()
    
    def send_message_async(
        self,
        session_id: str,
        text: str,
        provider_id: str = "google",
        model_id: str = "gemini-2.5-flash",
    ) -> bool:
        """Send a message asynchronously (returns immediately)."""
        body = {
            "model": {
                "providerID": provider_id,
                "modelID": model_id,
            },
            "parts": [
                {"type": "text", "text": text}
            ],
        }
        
        resp = self.client.post(
            f"/session/{session_id}/prompt_async",
            json=body,
        )
        return resp.status_code == 204
    
    def abort_session(self, session_id: str) -> bool:
        """Abort a running session."""
        resp = self.client.post(f"/session/{session_id}/abort")
        return resp.status_code == 200
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        resp = self.client.delete(f"/session/{session_id}")
        return resp.status_code == 200
    
    def get_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get messages from a session."""
        resp = self.client.get(
            f"/session/{session_id}/message",
            params={"limit": limit}
        )
        resp.raise_for_status()
        return resp.json()


def parse_model_string(model: str) -> tuple[str, str]:
    """
    Parse a model string into provider and model ID.
    
    Examples:
        "gemini" -> ("google", "gemini-2.5-flash")
        "google/gemini-2.5-flash" -> ("google", "gemini-2.5-flash")
        "ollama/granite4:3b" -> ("ollama", "granite4:3b")
        "anthropic/claude-sonnet-4-5" -> ("anthropic", "claude-sonnet-4-5")
    """
    # Shortcuts
    shortcuts = {
        "gemini": ("google", "gemini-2.5-flash"),
        "flash": ("google", "gemini-2.5-flash"),
        "pro": ("google", "gemini-2.5-pro"),
        "claude": ("anthropic", "claude-sonnet-4-5"),
        "sonnet": ("anthropic", "claude-sonnet-4-5"),
        "glm": ("ollama", "glm-4.7-flash"),
        "granite": ("ollama", "granite4:3b"),
    }
    
    if model.lower() in shortcuts:
        return shortcuts[model.lower()]
    
    if "/" in model:
        parts = model.split("/", 1)
        return (parts[0], parts[1])
    
    # Default to google
    return ("google", model)


def spawn_opencode_server(
    port: int = DEFAULT_PORT,
    cwd: str = None,
) -> subprocess.Popen:
    """
    Spawn an OpenCode server process.
    
    Args:
        port: Port to listen on
        cwd: Working directory
    
    Returns:
        The subprocess.Popen object
    """
    cmd = ["opencode", "serve", "--port", str(port)]
    
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait a bit for server to start
    time.sleep(2)
    
    return proc


def run_opencode_task(
    task: str,
    model: str = "gemini",
    cwd: str = None,
    timeout: float = 120.0,
    server_url: str = None,
) -> str:
    """
    Run a task using OpenCode and return the result.
    
    This is the main entry point for spawning subagent tasks.
    
    Args:
        task: The task description
        model: Model to use (e.g., "gemini", "ollama/granite4:3b")
        cwd: Working directory
        timeout: Timeout in seconds
        server_url: Optional existing server URL (e.g., "http://localhost:4096")
    
    Returns:
        The agent's response text
    """
    if not HTTPX_AVAILABLE:
        return "❌ httpx not available - run: uv add httpx"
    
    provider_id, model_id = parse_model_string(model)
    
    # Use existing server or spawn one
    server_proc = None
    port = DEFAULT_PORT
    
    if server_url:
        # Parse existing URL
        parts = server_url.replace("http://", "").split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else DEFAULT_PORT
    else:
        # Check if server is already running
        client = OpenCodeClient(port=port)
        health = client.health_check()
        
        if not health.get("healthy"):
            # Need to spawn server
            server_proc = spawn_opencode_server(port=port, cwd=cwd)
            time.sleep(3)  # Give it time to start
    
    try:
        client = OpenCodeClient(port=port)
        
        # Verify server is healthy
        health = client.health_check()
        if not health.get("healthy"):
            return f"❌ Server not healthy: {health.get('error', 'unknown')}"
        
        # Create session
        session = client.create_session(title=f"Ada Task: {task[:50]}")
        
        # Send message and wait for response
        response = client.send_message(
            session_id=session.id,
            text=task,
            provider_id=provider_id,
            model_id=model_id,
        )
        
        # Extract response text
        parts = response.get("parts", [])
        texts = []
        for part in parts:
            if isinstance(part, dict):
                # Only get actual text responses, not reasoning or metadata
                if part.get("type") == "text":
                    texts.append(part.get("text", ""))
        
        result = "\n".join(texts) if texts else "(No text response)"
        
        # Clean up session
        client.delete_session(session.id)
        client.close()
        
        return result
        
    except Exception as e:
        logger.error(f"OpenCode task failed: {e}")
        return f"❌ Error: {str(e)}"
    
    finally:
        if server_proc:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
