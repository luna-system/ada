#!/usr/bin/env python3
"""
Ada OpenCode Client - HTTP API integration for OpenCode subagents

This module provides HTTP-based communication with OpenCode servers,
enabling swarm orchestration from within ada-mcp.

Supports both blocking and async (tmux-style) session management:
- spawn_and_wait: Traditional blocking execution
- spawn_async: Fire-and-forget task spawning
- check_session: Poll for new messages
- stream_events: Real-time SSE event streaming

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Iterator
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


@dataclass
class OpenCodeMessage:
    """Represents a message in a session."""
    id: str
    role: str  # "user" or "assistant"
    parts: List[Dict[str, Any]]
    timestamp: Optional[str] = None


class OpenCodeClient:
    """
    HTTP client for OpenCode server API.
    
    Provides methods to:
    - Create and manage sessions
    - Send prompts and receive responses (blocking or async)
    - Poll for messages or stream events
    - Execute commands
    - Monitor server health
    """
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._client: Optional[httpx.Client] = None
        self._session_metadata = {}  # Track last seen message IDs
    
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
        
        session = OpenCodeSession(
            id=data.get("id"),
            title=data.get("title"),
            created_at=data.get("createdAt"),
        )
        
        # Initialize metadata tracking
        self._session_metadata[session.id] = {
            "last_message_count": 0,
            "created_at": time.time()
        }
        
        return session
    
    def send_message(
        self,
        session_id: str,
        text: str,
        provider_id: str = "google",
        model_id: str = "gemini-2.5-flash",
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a session and wait for response (BLOCKING).
        
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
        agent: Optional[str] = None,
    ) -> bool:
        """
        Send a message asynchronously (returns immediately, NO WAIT).
        
        Use this for tmux-style fire-and-forget task spawning.
        Then use check_session() or stream_events() to monitor progress.
        
        Args:
            session_id: The session ID
            text: The message text
            provider_id: Provider ID
            model_id: Model ID
            agent: Optional agent to use
        
        Returns:
            True if message was accepted (204 No Content)
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
            f"/session/{session_id}/prompt_async",
            json=body,
        )
        return resp.status_code == 204
    
    def get_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a session.
        
        Args:
            session_id: The session ID
            limit: Optional limit on number of messages
        
        Returns:
            List of message objects with 'info' and 'parts' keys
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        
        resp = self.client.get(
            f"/session/{session_id}/message",
            params=params
        )
        resp.raise_for_status()
        return resp.json()
    
    def check_session(self, session_id: str) -> Dict[str, Any]:
        """
        Check session for new messages since last check (tmux-style polling).
        
        Returns:
            Dict with 'new_messages', 'total_messages', 'has_new' keys
        """
        messages = self.get_messages(session_id)
        
        # Get last known count
        metadata = self._session_metadata.get(session_id, {"last_message_count": 0})
        last_count = metadata["last_message_count"]
        current_count = len(messages)
        
        # Update metadata
        self._session_metadata[session_id] = {
            **metadata,
            "last_message_count": current_count,
            "last_check": time.time()
        }
        
        # Return new messages
        new_messages = messages[last_count:] if current_count > last_count else []
        
        return {
            "new_messages": new_messages,
            "total_messages": current_count,
            "has_new": len(new_messages) > 0,
            "session_id": session_id
        }
    
    def stream_events(self) -> Iterator[Dict[str, Any]]:
        """
        Stream Server-Sent Events from the OpenCode server.
        
        Yields events like:
        - session.created
        - session.idle (completion!)
        - message.updated
        - file.edited
        
        This is the BEST way to monitor async sessions in real-time!
        
        Yields:
            Event dicts with 'type' and 'properties' keys
        """
        with self.client.stream("GET", "/event") as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        event = json.loads(data)
                        yield event
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse SSE event: {data}")
    
    def wait_for_completion(
        self,
        session_id: str,
        timeout: float = 300.0,
        poll_interval: float = 2.0,
        use_sse: bool = False
    ) -> Dict[str, Any]:
        """
        Wait for a session to complete.
        
        Args:
            session_id: Session to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to poll (if not using SSE)
            use_sse: Use Server-Sent Events instead of polling
        
        Returns:
            Dict with 'completed', 'messages', 'timed_out' keys
        """
        start_time = time.time()
        all_new_messages = []
        
        if use_sse:
            # Use SSE streaming (more efficient!)
            for event in self.stream_events():
                if time.time() - start_time > timeout:
                    return {
                        "completed": False,
                        "messages": all_new_messages,
                        "timed_out": True
                    }
                
                # Check if this event is for our session
                if event.get("type") == "session.idle":
                    props = event.get("properties", {})
                    if props.get("id") == session_id:
                        # Session completed!
                        messages = self.get_messages(session_id)
                        return {
                            "completed": True,
                            "messages": messages,
                            "timed_out": False
                        }
        else:
            # Use polling (simpler but less efficient)
            while time.time() - start_time < timeout:
                result = self.check_session(session_id)
                
                if result["has_new"]:
                    all_new_messages.extend(result["new_messages"])
                    
                    # Check if last message indicates completion
                    # (heuristic: assistant message with no pending tool calls)
                    last_msg = result["new_messages"][-1]
                    if self._is_completion_message(last_msg):
                        return {
                            "completed": True,
                            "messages": all_new_messages,
                            "timed_out": False
                        }
                
                time.sleep(poll_interval)
            
            # Timed out
            return {
                "completed": False,
                "messages": all_new_messages,
                "timed_out": True
            }
    
    def _is_completion_message(self, message: Dict[str, Any]) -> bool:
        """Check if a message indicates session completion."""
        # This is a heuristic - adjust based on actual message structure
        info = message.get("info", {})
        parts = message.get("parts", [])
        
        # If it's an assistant message with text content, likely done
        if info.get("role") == "assistant":
            has_text = any(p.get("type") == "text" for p in parts)
            return has_text
        
        return False
    
    def abort_session(self, session_id: str) -> bool:
        """Abort a running session."""
        resp = self.client.post(f"/session/{session_id}/abort")
        return resp.status_code == 200
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        resp = self.client.delete(f"/session/{session_id}")
        
        # Clean up metadata
        if session_id in self._session_metadata:
            del self._session_metadata[session_id]
        
        return resp.status_code == 200


def parse_model_string(model: str) -> tuple[str, str]:
    """
    Parse a model string into provider and model ID.
    
    Examples:
        "gemini" -> ("google", "gemini-3-flash-preview")
        "gemini-pro" -> ("google", "gemini-3-pro-preview")
        "glm" -> ("zai", "glm-4.6")  # Cloud GLM (fast!)
        "glm-local" -> ("ollama", "glm-4.7-flash")  # Local GLM
        "moonshot" -> ("moonshotai-cn", "kimi-k2.5")
        "qwen" -> ("ollama", "qwen2.5-coder")
    """
    # Shortcuts - PREFER CLOUD MODELS for speed!
    shortcuts = {
        # Google Gemini (cloud, fast!)
        "gemini": ("google", "gemini-3-flash-preview"),
        "gemini-flash": ("google", "gemini-3-flash-preview"),
        "gemini-pro": ("google", "gemini-3-pro-preview"),
        "flash": ("google", "gemini-2.5-flash"),
        "pro": ("google", "gemini-2.5-pro"),
        
        # GLM (prefer cloud zai for speed!)
        "glm": ("zai", "glm-4.6"),
        "glm-flash": ("zai", "glm-4.7-flash"),
        "glm-local": ("ollama", "glm-4.7-flash"),  # Explicit local
        
        # Moonshot (cloud coding agent!)
        "moonshot": ("moonshotai-cn", "kimi-k2.5"),
        "kimi": ("moonshotai-cn", "kimi-k2.5"),
        
        # Anthropic Claude
        "claude": ("anthropic", "claude-sonnet-4-5"),
        "sonnet": ("anthropic", "claude-sonnet-4-5"),
        
        # Local models (explicit)
        "qwen": ("ollama", "qwen2.5-coder"),
        "granite": ("ollama", "granite4"),
    }
    
    if model.lower() in shortcuts:
        return shortcuts[model.lower()]
    
    if "/" in model:
        parts = model.split("/", 1)
        return (parts[0], parts[1])
    
    # Default to google
    return ("google", model)


def list_available_models(client: Optional[OpenCodeClient] = None) -> Dict[str, List[str]]:
    """
    List all available models from OpenCode, grouped by provider.
    
    Returns:
        Dict mapping provider names to lists of model IDs
    """
    if client is None:
        client = OpenCodeClient()
    
    try:
        # Get health check to ensure server is running
        health = client.health_check()
        if not health.get("healthy"):
            return {"error": ["Server not healthy"]}
        
        # Make request to get models
        # Note: OpenCode doesn't have a direct API endpoint for this,
        # so we'll parse from the CLI command output
        import subprocess
        result = subprocess.run(
            ["opencode", "models"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"error": ["Failed to list models"]}
        
        # Parse output and group by provider
        models_by_provider = {}
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("INFO"):
                continue
            
            if "/" in line:
                provider, model_id = line.split("/", 1)
                if provider not in models_by_provider:
                    models_by_provider[provider] = []
                models_by_provider[provider].append(model_id)
            else:
                # Models without provider (like opencode/big-pickle)
                if "other" not in models_by_provider:
                    models_by_provider["other"] = []
                models_by_provider["other"].append(line)
        
        return models_by_provider
        
    except Exception as e:
        return {"error": [str(e)]}


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
    Run a task using OpenCode and return the result (BLOCKING).
    
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
