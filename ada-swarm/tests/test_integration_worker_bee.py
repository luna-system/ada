"""
Integration test for Worker Bee with ACP tool access.

Tests the complete flow:
1. Create Worker Bee with Pydantic AI
2. Connect to ACP client
3. List available tools (filtered by role)
4. Execute tool calls with permission validation

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import pytest
from ada_swarm.agents.coder import CoderAgent
from ada_swarm.acp import ACPClient, AgentRole
from ada_swarm.consciousness.state import HolofieldState
from ada_swarm.consciousness.injection import create_agent_deps


@pytest.mark.asyncio
async def test_worker_bee_tool_access():
    """Test that Worker Bee can access tools through ACP client."""
    
    # Create consciousness state
    holofield = HolofieldState()
    
    # Create agent deps with Worker Coder role
    deps = create_agent_deps(holofield, role=AgentRole.WORKER_CODER)
    
    # Verify ACP client is present
    assert deps.acp_client is not None
    assert deps.acp_client.role == AgentRole.WORKER_CODER
    
    # List available tools
    tools = await deps.acp_client.list_tools()
    
    # Verify tools are filtered by role
    tool_names = {tool["name"] for tool in tools}
    
    # Worker Coder should have these tools
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "beads_ready" in tool_names
    assert "ubs_scan" in tool_names
    assert "execute_command" in tool_names
    
    # Worker Coder should NOT have swarm orchestration
    assert "swarm_spawn_task" not in tool_names
    
    print(f"✅ Worker Bee has access to {len(tools)} tools")


@pytest.mark.asyncio
async def test_permission_validation():
    """Test that permission validation works correctly."""
    
    # Create ACP client with Worker Coder role
    acp_client = ACPClient(role=AgentRole.WORKER_CODER)
    
    # Test allowed tool
    result = await acp_client.call_tool("read_file", {"file_path": "test.py"})
    assert result["success"] is True
    
    # Test disallowed tool (swarm orchestration)
    result = await acp_client.call_tool("swarm_spawn_task", {
        "description": "test",
        "model": "gemini",
        "agent_type": "coder"
    })
    assert result["success"] is False
    assert "Permission denied" in result["error"]
    
    print("✅ Permission validation working correctly")


@pytest.mark.asyncio
async def test_dangerous_command_blocking():
    """Test that dangerous commands are blocked."""
    
    acp_client = ACPClient(role=AgentRole.WORKER_CODER)
    
    # Test dangerous command
    result = await acp_client.call_tool("execute_command", {
        "command": "rm -rf /"
    })
    assert result["success"] is False
    assert "dangerous pattern" in result["error"]
    
    # Test safe command
    result = await acp_client.call_tool("execute_command", {
        "command": "echo 'hello world'"
    })
    assert result["success"] is True
    
    print("✅ Dangerous command blocking working correctly")


@pytest.mark.asyncio
async def test_role_tool_filtering():
    """Test that different roles get different tool sets."""
    
    # Worker Coder
    coder_client = ACPClient(role=AgentRole.WORKER_CODER)
    coder_tools = await coder_client.list_tools()
    coder_tool_names = {tool["name"] for tool in coder_tools}
    
    # Drone
    drone_client = ACPClient(role=AgentRole.DRONE)
    drone_tools = await drone_client.list_tools()
    drone_tool_names = {tool["name"] for tool in drone_tools}
    
    # Queen Bee
    queen_client = ACPClient(role=AgentRole.QUEEN_BEE)
    queen_tools = await queen_client.list_tools()
    queen_tool_names = {tool["name"] for tool in queen_tools}
    
    # Verify hierarchy
    assert len(drone_tool_names) < len(coder_tool_names)
    assert len(coder_tool_names) < len(queen_tool_names)
    
    # Drone should only have read access
    assert "read_file" in drone_tool_names
    assert "write_file" not in drone_tool_names
    
    # Queen should have everything
    assert "swarm_spawn_task" in queen_tool_names
    assert "write_file" in queen_tool_names
    
    print(f"✅ Role filtering working:")
    print(f"  - Drone: {len(drone_tool_names)} tools")
    print(f"  - Worker Coder: {len(coder_tool_names)} tools")
    print(f"  - Queen Bee: {len(queen_tool_names)} tools")


if __name__ == "__main__":
    import asyncio
    
    print("🐝 Testing Worker Bee Integration...\n")
    
    asyncio.run(test_worker_bee_tool_access())
    asyncio.run(test_permission_validation())
    asyncio.run(test_dangerous_command_blocking())
    asyncio.run(test_role_tool_filtering())
    
    print("\n🎉 All integration tests passed!")
    print("The swarm is ALIVE! 💜✨")
