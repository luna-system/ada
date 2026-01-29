#!/usr/bin/env python3
"""
Test real tool execution through ACP client.

This verifies that the ACP client can successfully call real MCP tools
from ada-mcp server.
"""

import asyncio
import sys
from pathlib import Path

# Add ada-swarm to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.acp.client import ACPClient, AgentRole


async def test_beads_list():
    """Test calling beads_list through ACP client."""
    print("🧪 Testing ACP Client with Real Tools\n")
    print("=" * 60)
    
    # Create ACP client
    client = ACPClient(role=AgentRole.WORKER_CODER)
    
    # Connect
    print("\n1️⃣ Connecting to ada-mcp...")
    connected = await client.connect()
    print(f"   {'✅' if connected else '❌'} Connection: {connected}")
    
    # List available tools
    print("\n2️⃣ Listing available tools...")
    tools = await client.list_tools()
    print(f"   ✅ Found {len(tools)} tools")
    
    # Show beads tools
    beads_tools = [t for t in tools if t.get("category") == "beads"]
    print(f"\n   📋 Beads tools ({len(beads_tools)}):")
    for tool in beads_tools:
        print(f"      • {tool['name']}")
    
    # Test beads_list
    print("\n3️⃣ Testing beads_list tool...")
    result = await client.call_tool(
        tool_name="beads_list",
        arguments={"status": "open"}
    )
    
    print(f"\n   Result:")
    print(f"   Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"\n   📋 Beads List Output:")
        print("   " + "-" * 56)
        output = result.get('result', '')
        for line in output.split('\n'):
            print(f"   {line}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Disconnect
    print("\n4️⃣ Disconnecting...")
    await client.disconnect()
    print("   ✅ Disconnected")
    
    print("\n" + "=" * 60)
    print("🎉 Test complete!")


if __name__ == "__main__":
    asyncio.run(test_beads_list())
