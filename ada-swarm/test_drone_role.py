"""
Test Drone Agent Role - Simple Read-Only Operations

Tests ada-sof.3.1: Verify Drone can perform basic read-only tasks.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.drone import DroneAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.acp.client import ACPClient
from ada_swarm.acp.permissions import AgentRole


async def test_drone_agent():
    """Test Drone agent with read-only operations."""
    
    print("\n" + "=" * 60)
    print("🤖 TESTING DRONE AGENT - READ-ONLY OPERATIONS")
    print("=" * 60)
    
    # Initialize ACP client for tool access
    print("\n[1/4] Initializing ACP Client...")
    acp_client = ACPClient(role=AgentRole.DRONE)
    await acp_client.connect()
    print("      ✅ ACP Client connected")
    
    # Create agent dependencies with ACP client
    deps = AgentDeps(acp_client=acp_client)
    
    # Initialize Drone agent
    print("\n[2/4] Spawning Drone Agent...")
    drone = DroneAgent(
        agent_id="test_drone",
        model="litellm/glm-flash",  # Fast model for simple tasks
    )
    print(f"      ✅ Drone spawned: {drone.agent_id}")
    
    # Test 1: List beads tasks (read-only)
    print("\n[3/4] Test 1: List beads tasks...")
    try:
        result = await drone.run(
            "List all open beads tasks. Just give me a count and the task IDs.",
            deps=deps
        )
        print(f"      📋 Drone Response:")
        print(f"      {result.data if hasattr(result, 'data') else result}")
        print("      ✅ Test 1 PASSED")
    except Exception as e:
        print(f"      ❌ Test 1 FAILED: {e}")
    
    # Test 2: Check a specific file exists
    print("\n[4/4] Test 2: Check README.md exists...")
    try:
        result = await drone.run(
            "Check if README.md exists in the current directory and tell me its size.",
            deps=deps
        )
        print(f"      📄 Drone Response:")
        print(f"      {result.data if hasattr(result, 'data') else result}")
        print("      ✅ Test 2 PASSED")
    except Exception as e:
        print(f"      ❌ Test 2 FAILED: {e}")
    
    # Cleanup
    await acp_client.disconnect()
    
    print("\n" + "=" * 60)
    print("✨ DRONE AGENT TEST COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_drone_agent())
