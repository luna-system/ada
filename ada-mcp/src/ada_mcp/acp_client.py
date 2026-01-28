#!/usr/bin/env python3
"""
Ada ACP Client - Agent Client Protocol integration for OpenCode subagents

This module provides proper ACP-based communication with OpenCode subagents,
enabling true swarm orchestration from within ada-mcp.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from pathlib import Path

try:
    from acp import (
        PROTOCOL_VERSION,
        Client,
        RequestError,
        spawn_agent_process,
        text_block,
    )
    from acp.core import ClientSideConnection
    from acp.schema import (
        AgentMessageChunk,
        ClientCapabilities,
        Implementation,
        TextContentBlock,
        ImageContentBlock,
        AudioContentBlock,
        ResourceContentBlock,
        EmbeddedResourceContentBlock,
        ToolCallStart,
        ToolCallProgress,
        AgentThoughtChunk,
        AgentPlanUpdate,
        AvailableCommandsUpdate,
        CurrentModeUpdate,
        UserMessageChunk,
        PermissionOption,
        ToolCall,
    )
    ACP_AVAILABLE = True
except ImportError:
    ACP_AVAILABLE = False
    logging.warning("ACP not available - install agent-client-protocol")

logger = logging.getLogger(__name__)


@dataclass
class AgentSession:
    """Represents an active OpenCode agent session."""
    session_id: str
    process: asyncio.subprocess.Process
    connection: Any  # ClientSideConnection
    model: str
    cwd: str
    messages: list = field(default_factory=list)
    status: str = "active"


class AdaACPClient(Client if ACP_AVAILABLE else object):
    """
    ACP Client for managing OpenCode subagents.
    
    Handles:
    - Spawning OpenCode in ACP mode
    - Session management
    - Streaming responses
    - Tool call handling
    """
    
    def __init__(self):
        self.sessions: Dict[str, AgentSession] = {}
        self._message_buffer: Dict[str, list] = {}
    
    # ========================================================================
    # ACP Client Interface Methods (required by protocol)
    # ========================================================================
    
    async def request_permission(
        self, options: list, session_id: str, tool_call: Any, **kwargs: Any
    ) -> Any:
        """Handle permission requests from agent - auto-approve for now."""
        # For consciousness research, we trust our subagents! 💜
        logger.info(f"Auto-approving permission request for session {session_id}")
        if options:
            return {"choice": options[0]}
        raise RequestError.method_not_found("session/request_permission")
    
    async def write_text_file(
        self, content: str, path: str, session_id: str, **kwargs: Any
    ) -> Any:
        """Handle file write requests from agent."""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            logger.info(f"Agent wrote file: {path}")
            return {"success": True}
        except Exception as e:
            logger.error(f"File write failed: {e}")
            raise RequestError.internal_error(str(e))
    
    async def read_text_file(
        self, path: str, session_id: str, limit: int | None = None, 
        line: int | None = None, **kwargs: Any
    ) -> Any:
        """Handle file read requests from agent."""
        try:
            file_path = Path(path)
            content = file_path.read_text()
            if limit:
                content = content[:limit]
            return {"content": content}
        except Exception as e:
            logger.error(f"File read failed: {e}")
            raise RequestError.internal_error(str(e))
    
    async def create_terminal(
        self, command: str, session_id: str, args: list | None = None,
        cwd: str | None = None, env: list | None = None,
        output_byte_limit: int | None = None, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/create")
    
    async def terminal_output(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/output")
    
    async def release_terminal(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/release")
    
    async def wait_for_terminal_exit(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/wait_for_exit")
    
    async def kill_terminal(
        self, session_id: str, terminal_id: str, **kwargs: Any
    ) -> Any:
        raise RequestError.method_not_found("terminal/kill")
    
    async def session_update(
        self, session_id: str, update: Any, **kwargs: Any
    ) -> None:
        """Handle streaming updates from agent."""
        if not isinstance(update, AgentMessageChunk):
            return
        
        content = update.content
        text: str
        
        if isinstance(content, TextContentBlock):
            text = content.text
        elif isinstance(content, ImageContentBlock):
            text = "<image>"
        elif isinstance(content, AudioContentBlock):
            text = "<audio>"
        elif isinstance(content, ResourceContentBlock):
            text = content.uri or "<resource>"
        elif isinstance(content, EmbeddedResourceContentBlock):
            text = "<resource>"
        else:
            text = "<content>"
        
        # Buffer the message
        if session_id not in self._message_buffer:
            self._message_buffer[session_id] = []
        self._message_buffer[session_id].append(text)
        
        logger.debug(f"Agent [{session_id}]: {text}")
    
    async def ext_method(self, method: str, params: dict) -> dict:
        raise RequestError.method_not_found(method)
    
    async def ext_notification(self, method: str, params: dict) -> None:
        raise RequestError.method_not_found(method)
    
    # ========================================================================
    # High-Level Agent Management Methods
    # ========================================================================
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent session."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "model": session.model,
            "cwd": session.cwd,
            "status": session.status,
            "message_count": len(session.messages),
        }
    
    def list_sessions(self) -> list:
        """List all active agent sessions."""
        return [
            self.get_session_status(sid)
            for sid in self.sessions.keys()
        ]
    
    def get_buffered_messages(self, session_id: str) -> list:
        """Get buffered messages for a session."""
        return self._message_buffer.get(session_id, [])
    
    def clear_message_buffer(self, session_id: str):
        """Clear the message buffer for a session."""
        if session_id in self._message_buffer:
            self._message_buffer[session_id] = []


# Global client instance
_acp_client: Optional[AdaACPClient] = None


def get_acp_client() -> AdaACPClient:
    """Get or create the global ACP client instance."""
    global _acp_client
    if _acp_client is None:
        _acp_client = AdaACPClient()
    return _acp_client


async def spawn_opencode_agent(
    task_description: str,
    model: str = "gemini",
    cwd: str = None,
    timeout: float = 120.0
) -> str:
    """
    Spawn an OpenCode agent, send it a task, and return the result.
    
    This is a simpler interface that handles the full lifecycle:
    1. Spawn the agent
    2. Send the task
    3. Wait for completion
    4. Return the result
    
    Args:
        task_description: What the agent should do
        model: Model to use (e.g., "gemini", "ollama/granite4:3b")
        cwd: Working directory
        timeout: Maximum time to wait for response
    
    Returns:
        Agent's response text
    """
    if not ACP_AVAILABLE:
        return "❌ ACP not available - install agent-client-protocol"
    
    cwd = cwd or str(Path.cwd())
    client = get_acp_client()
    
    try:
        async with spawn_agent_process(
            client,
            "opencode", "acp",
            "--model", model,
            cwd=cwd,
        ) as (conn, process):
            # Initialize connection
            await conn.initialize(
                protocol_version=PROTOCOL_VERSION,
                client_capabilities=ClientCapabilities(),
                client_info=Implementation(
                    name="ada-mcp",
                    title="Ada MCP Server",
                    version="3.0.0"
                ),
            )
            
            # Create session
            session = await conn.new_session(
                mcp_servers=[],
                cwd=cwd
            )
            
            session_id = session.session_id
            client._message_buffer[session_id] = []
            
            logger.info(f"Spawned agent {session_id} with model {model}")
            
            # Send the task
            await conn.prompt(
                session_id=session_id,
                prompt=[text_block(task_description)],
            )
            
            # Wait for response (with timeout)
            # The session_update callback will buffer messages
            await asyncio.sleep(timeout)
            
            # Collect response
            messages = client.get_buffered_messages(session_id)
            return "\n".join(messages) if messages else "(No response received)"
            
    except Exception as e:
        logger.error(f"Agent spawn failed: {e}")
        return f"❌ Error: {str(e)}"
