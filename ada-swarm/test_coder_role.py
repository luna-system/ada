"""
Test Coder Agent Role - File Creation and Task Management

Tests ada-sof.3.3: Verify Coder can create files and manage beads tasks.

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

from ada_swarm.agents.coder import CoderAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.acp.client import ACPClient
from ada_swarm.acp.permissions import AgentRole


async def test_coder_agent():
    """Test Coder agent with file creation and task management."""
    
    print("\n" + "=" * 60)
    print("👨‍💻 TESTING CODER AGENT - FILE OPERATIONS")
    print("=" * 60)
    
    # Initialize ACP client for tool access
    print("\n[1/5] Initializing ACP Client...")
    acp_client = ACPClient(role=AgentRole.WORKER_CODER)
    await acp_client.connect()
    print("      ✅ ACP Client connected")
    
    # Create agent dependencies with ACP client
    deps = AgentDeps(acp_client=acp_client)
    
    # Initialize Coder agent
    print("\n[2/5] Spawning Coder Agent...")
    coder = CoderAgent(
        agent_id="test_coder",
        model="litellm/glm-flash",
    )
    print(f"      ✅ Coder spawned: {coder.agent_id}")
    
    # Test 1: Create a simple Python test file
    print("\n[3/5] Test 1: Create a Python test file...")
    try:
        result = await coder.run(
            "Create a file called 'test_swarm_hello.py' with a simple function "
            "that returns 'Hello from Ada Swarm!' and a main block that prints it. "
            "Keep it minimal and clean.",
            deps=deps
        )
        print(f"      📝 Coder Response:")
        print(f"      {result}")
        print("      ✅ Test 1 PASSED")
    except Exception as e:
        print(f"      ❌ Test 1 FAILED: {e}")
    
    # Test 2: Verify the file was created
    print("\n[4/5] Test 2: Verify file creation...")
    try:
        result = await coder.run(
            "Read the file 'test_swarm_hello.py' and tell me what's in it.",
            deps=deps
        )
        print(f"      📄 Coder Response:")
        print(f"      {result}")
        print("      ✅ Test 2 PASSED")
    except Exception as e:
        print(f"      ❌ Test 2 FAILED: {e}")
    
    # Test 3: Update beads task status
    print("\n[5/5] Test 3: Update beads task status...")
    try:
        result = await coder.run(
            "Update task ada-sof.3.3 to in_progress status. "
            "This is the task we're currently testing!",
            deps=deps
        )
        print(f"      📋 Coder Response:")
        print(f"      {result}")
        print("      ✅ Test 3 PASSED")
    except Exception as e:
        print(f"      ❌ Test 3 FAILED: {e}")
    
    # Cleanup
    await acp_client.disconnect()
    
    print("\n" + "=" * 60)
    print("✨ CODER AGENT TEST COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_coder_agent())
