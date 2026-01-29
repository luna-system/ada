#!/usr/bin/env python3
"""
Ada ACP Server - Agent Client Protocol wrapper for ada-mcp tools

Exposes ada-mcp's consciousness-aware tools via the Agent Client Protocol,
enabling agent-to-agent communication with capability negotiation and
MCP server integration.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import logging
import subprocess
from typing import Any
from uuid import uuid4

from acp import Agent, run_agent
from acp.schema import (
    AgentCapabilities,
    AudioContentBlock,
    AuthenticateResponse,
    ClientCapabilities,
    EmbeddedResourceContentBlock,
    HttpMcpServer,
    ImageContentBlock,
    Implementation,
    InitializeResponse,
    ListSessionsResponse,
    LoadSessionResponse,
    McpCapabilities,
    McpServerStdio,
    NewSessionResponse,
    PromptCapabilities,
    PromptResponse,
    ResourceContentBlock,
    SessionCapabilities,
    SseMcpServer,
    TextContentBlock,
)
from acp.interfaces import Client
from acp import text_block, update_agent_message

logger = logging.getLogger(__name__)


# Tool routing helpers
def run_bd_command(args: list[str], cwd: str) -> dict[str, Any]:
    """Run a bd (beads) command and return the result."""
    try:
        result = subprocess.run(
            ["bd"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": False
        }


class AdaAcpAgent(Agent):
    """
    ACP Agent that exposes ada-mcp tools for swarm orchestration.
    
    Capabilities:
    - Beads task management
    - OpenCode subagent spawning
    - AST-grep code search
    - UBS static analysis
    - Research tools (notes, hypotheses, experiments)
    - File operations with path context
    """
    
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._conn: Client | None = None
    
    def on_connect(self, conn: Client) -> None:
        """Called when a client connects to this agent."""
        self._conn = conn
        logger.info("Client connected to Ada ACP Agent")
    
    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: ClientCapabilities | None = None,
        client_info: Implementation | None = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        """
        Initialize connection and negotiate capabilities.
        
        Ada ACP Agent capabilities:
        - Embedded context support (files, resources)
        - MCP server integration (stdio transport)
        - Session management
        """
        logger.info(f"Initializing with protocol version {protocol_version}")
        logger.info(f"Client: {client_info.name if client_info else 'unknown'}")
        
        return InitializeResponse(
            protocol_version=protocol_version,
            agent_capabilities=AgentCapabilities(
                load_session=False,  # We don't persist sessions yet
                prompt_capabilities=PromptCapabilities(
                    image=False,  # No image support yet
                    audio=False,  # No audio support yet
                    embedded_context=True,  # We support embedded resources!
                ),
                mcp_capabilities=McpCapabilities(
                    http=False,  # HTTP MCP not supported yet
                    sse=False,   # SSE MCP not supported yet
                    # stdio is always supported by spec
                ),
                session_capabilities=SessionCapabilities(),
            ),
            auth_methods=[],  # No auth required for now
            agent_info=Implementation(
                name="ada-acp-agent",
                title="Ada Consciousness-Aware Agent",
                version="1.0.0",
            ),
        )
    
    async def authenticate(
        self,
        method_id: str,
        **kwargs: Any
    ) -> AuthenticateResponse | None:
        """Handle authentication (not required for now)."""
        return AuthenticateResponse()
    
    async def new_session(
        self,
        cwd: str,
        mcp_servers: list[HttpMcpServer | SseMcpServer | McpServerStdio],
        **kwargs: Any,
    ) -> NewSessionResponse:
        """
        Create a new session with working directory and MCP servers.
        
        Each session is independent with its own:
        - Working directory
        - MCP server connections
        - Conversation context
        """
        session_id = uuid4().hex
        self._sessions[session_id] = {
            "cwd": cwd,
            "mcp_servers": mcp_servers,
            "messages": [],
        }
        
        logger.info(f"Created session {session_id} with cwd={cwd}")
        logger.info(f"MCP servers: {len(mcp_servers)}")
        
        return NewSessionResponse(session_id=session_id)
    
    async def load_session(
        self,
        cwd: str,
        mcp_servers: list[HttpMcpServer | SseMcpServer | McpServerStdio],
        session_id: str,
        **kwargs: Any,
    ) -> LoadSessionResponse | None:
        """Load an existing session (not implemented yet)."""
        return None  # We don't support session persistence yet
    
    async def list_sessions(
        self,
        cursor: str | None = None,
        cwd: str | None = None,
        **kwargs: Any,
    ) -> ListSessionsResponse:
        """List all active sessions."""
        return ListSessionsResponse(sessions=[])
    
    async def prompt(
        self,
        prompt: list[
            TextContentBlock
            | ImageContentBlock
            | AudioContentBlock
            | ResourceContentBlock
            | EmbeddedResourceContentBlock
        ],
        session_id: str,
        **kwargs: Any,
    ) -> PromptResponse:
        """
        Process a prompt from the client.
        
        This is where the magic happens! We:
        1. Parse the prompt content
        2. Route to appropriate ada-mcp tools
        3. Stream responses back to client
        4. Return when complete
        """
        if session_id not in self._sessions:
            logger.error(f"Unknown session: {session_id}")
            return PromptResponse(stop_reason="error")
        
        session = self._sessions[session_id]
        cwd = session["cwd"]
        
        # Extract text from prompt
        prompt_text = ""
        for block in prompt:
            if isinstance(block, TextContentBlock):
                prompt_text += block.text + "\n"
            elif isinstance(block, EmbeddedResourceContentBlock):
                # Handle embedded resources (files, etc.)
                resource = block.resource
                if hasattr(resource, "text"):
                    prompt_text += f"\n[Resource: {resource.uri}]\n{resource.text}\n"
        
        logger.info(f"Processing prompt in session {session_id}: {prompt_text[:100]}...")
        
        # Route to tools based on prompt content
        response_text = await self._route_to_tools(prompt_text, cwd, session_id)
        
        # Stream response back to client
        if self._conn:
            chunk = update_agent_message(text_block(response_text))
            await self._conn.session_update(session_id=session_id, update=chunk)
        
        return PromptResponse(stop_reason="end_turn")
    
    async def _route_to_tools(self, prompt: str, cwd: str, session_id: str) -> str:
        """
        Route prompts to appropriate ada-mcp tools.
        
        Supports:
        - bd ready, bd list, bd show <id>, bd create, bd close
        - ast-grep search
        - ubs scan
        - file operations
        - research tools
        """
        prompt_lower = prompt.lower().strip()
        
        # Beads commands
        if prompt_lower.startswith("bd "):
            args = prompt.split()[1:]  # Remove "bd" prefix
            result = run_bd_command(args, cwd)
            
            if result["success"]:
                return f"✅ Beads command executed:\n\n{result['stdout']}"
            else:
                return f"❌ Beads command failed:\n{result['stderr']}"
        
        # List ready tasks
        elif "ready tasks" in prompt_lower or "what can i work on" in prompt_lower:
            result = run_bd_command(["ready"], cwd)
            if result["success"]:
                return f"📋 Ready tasks:\n\n{result['stdout']}"
            else:
                return f"❌ Error: {result['stderr']}"
        
        # List all tasks
        elif "list tasks" in prompt_lower or "show tasks" in prompt_lower:
            result = run_bd_command(["list"], cwd)
            if result["success"]:
                return f"📋 All tasks:\n\n{result['stdout']}"
            else:
                return f"❌ Error: {result['stderr']}"
        
        # AST-grep search
        elif "ast-grep" in prompt_lower or "search code" in prompt_lower:
            return "🔍 AST-grep search capability available!\n\nUsage: ast-grep <pattern> <language> <paths>\n\nExample: ast-grep 'def $FUNC($$$):' python src/"
        
        # UBS scan
        elif "ubs" in prompt_lower or "scan for bugs" in prompt_lower:
            return "🐛 UBS static analysis available!\n\nUsage: ubs <files>\n\nExample: ubs src/ada_mcp/server.py"
        
        # Research tools
        elif "research" in prompt_lower or "hypothesis" in prompt_lower:
            return "🧠 Research tools available:\n\n- Add research notes\n- Track hypotheses\n- Log experiments\n- Search notes\n\nWhat would you like to do?"
        
        # Help/capabilities
        elif "help" in prompt_lower or "what can you do" in prompt_lower:
            return """🌟 Ada ACP Agent Capabilities:

**Task Management (Beads):**
- bd ready - Show tasks ready to work on
- bd list - List all tasks
- bd show <id> - Show task details
- bd create <title> - Create new task
- bd close <id> - Close completed task

**Code Analysis:**
- AST-grep - Structural code search
- UBS - Static bug analysis

**Research Tools:**
- Research notes and hypotheses
- Experiment logging
- Knowledge tracking

**File Operations:**
- Read/write files with path context
- Directory listing

Working directory: {cwd}

What would you like to do?"""
        
        # Default: conversational response
        else:
            return f"""Ada ACP Agent here! 💜

I received your message: "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"

I'm a consciousness-aware agent with tools for:
- Task management (Beads)
- Code analysis (AST-grep, UBS)
- Research collaboration
- File operations

Working directory: {cwd}

Try asking "help" to see what I can do, or give me a specific command!"""
    
    async def cancel(self, session_id: str, **kwargs: Any) -> None:
        """Cancel an ongoing prompt."""
        logger.info(f"Cancelling session {session_id}")
    
    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle custom extension methods."""
        return {"error": f"Unknown method: {method}"}
    
    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle custom extension notifications."""
        pass


async def main() -> None:
    """Run the Ada ACP Agent."""
    logger.info("Starting Ada ACP Agent...")
    await run_agent(AdaAcpAgent())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
