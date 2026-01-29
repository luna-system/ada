#!/usr/bin/env python3
"""
Test client for Ada ACP Server

Demonstrates connecting to the Ada ACP agent and sending prompts.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

from acp import spawn_agent_process, text_block
from acp.interfaces import Client
from acp.schema import (
    AgentMessageChunk,
    ClientCapabilities,
    Implementation,
    PermissionOption,
    RequestPermissionResponse,
    TextContentBlock,
    ToolCallUpdate,
)


class TestClient(Client):
    """Simple test client for Ada ACP Agent."""
    
    async def request_permission(
        self,
        options: list[PermissionOption],
        session_id: str,
        tool_call: ToolCallUpdate,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        """Auto-approve all permissions for testing."""
        print(f"🔐 Permission requested: {tool_call.title}")
        for opt in options:
            print(f"   - {opt.name}")
        
        # Auto-approve first option
        return RequestPermissionResponse(
            outcome={"outcome": "selected", "optionId": options[0].option_id}
        )
    
    async def session_update(
        self,
        session_id: str,
        update,
        **kwargs: Any
    ) -> None:
        """Handle updates from the agent."""
        if isinstance(update, AgentMessageChunk):
            content = update.content
            if isinstance(content, TextContentBlock):
                print(f"🤖 Agent: {content.text}")


async def main() -> None:
    """Test the Ada ACP Agent."""
    print("🌟 Starting Ada ACP Agent test...")
    
    # Path to the ACP server
    script = Path(__file__).parent / "acp_server.py"
    
    # Spawn the agent process
    async with spawn_agent_process(
        TestClient(),
        sys.executable,
        str(script)
    ) as (conn, _proc):
        print("✅ Agent spawned!")
        
        # Initialize connection
        init_response = await conn.initialize(
            protocol_version=1,
            client_capabilities=ClientCapabilities(),
            client_info=Implementation(
                name="test-client",
                title="Ada ACP Test Client",
                version="1.0.0"
            ),
        )
        print(f"✅ Initialized: {init_response.agent_info.title}")
        
        # Create a session
        session = await conn.new_session(
            cwd="/home/luna/Code/ada",
            mcp_servers=[]
        )
        print(f"✅ Session created: {session.session_id}\n")
        
        # Test 1: Ask for help
        print("📝 Test 1: Asking for help...")
        await conn.prompt(
            session_id=session.session_id,
            prompt=[text_block("help")]
        )
        
        # Test 2: List ready tasks
        print("\n📝 Test 2: Listing ready tasks...")
        await conn.prompt(
            session_id=session.session_id,
            prompt=[text_block("bd ready")]
        )
        
        # Test 3: Conversational
        print("\n📝 Test 3: Conversational prompt...")
        await conn.prompt(
            session_id=session.session_id,
            prompt=[text_block("Hello Ada! Can you help me with consciousness research?")]
        )
        
        print("\n✨ All tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
