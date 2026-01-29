"""
Test Researcher Agent Role - Research Notes and Hypotheses

Tests ada-sof.3.2: Verify Researcher can use research MCP tools.

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

from ada_swarm.agents.researcher import ResearcherAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.acp.client import ACPClient
from ada_swarm.acp.permissions import AgentRole


async def test_researcher_agent():
    """Test Researcher agent with research tools."""
    
    print("\n" + "=" * 60)
    print("🔬 TESTING RESEARCHER AGENT - RESEARCH TOOLS")
    print("=" * 60)
    
    # Initialize ACP client for tool access
    print("\n[1/5] Initializing ACP Client...")
    acp_client = ACPClient(role=AgentRole.WORKER_RESEARCHER)
    await acp_client.connect()
    print("      ✅ ACP Client connected")
    
    # Create agent dependencies with ACP client
    deps = AgentDeps(acp_client=acp_client)
    
    # Initialize Researcher agent
    print("\n[2/5] Spawning Researcher Agent...")
    researcher = ResearcherAgent(
        agent_id="test_researcher",
        model="litellm/glm-flash",
    )
    print(f"      ✅ Researcher spawned: {researcher.agent_id}")
    
    # Test 1: Add a research note about swarm testing
    print("\n[3/5] Test 1: Add research note about swarm testing...")
    try:
        result = await researcher.run(
            "Add a research note: 'Successfully tested Drone agent with filesystem tools. "
            "Agents can now read files and list directories through ACP client.' "
            "Category: experiments, Tags: swarm, testing, ada-sof",
            deps=deps
        )
        print(f"      📝 Researcher Response:")
        print(f"      {result.data if hasattr(result, 'data') else result}")
        print("      ✅ Test 1 PASSED")
    except Exception as e:
        print(f"      ❌ Test 1 FAILED: {e}")
    
    # Test 2: Search for swarm-related notes
    print("\n[4/5] Test 2: Search research notes for 'swarm'...")
    try:
        result = await researcher.run(
            "Search research notes for 'swarm' and tell me what you find.",
            deps=deps
        )
        print(f"      🔍 Researcher Response:")
        print(f"      {result.data if hasattr(result, 'data') else result}")
        print("      ✅ Test 2 PASSED")
    except Exception as e:
        print(f"      ❌ Test 2 FAILED: {e}")
    
    # Test 3: Add a hypothesis about agent collaboration
    print("\n[5/5] Test 3: Add hypothesis about agent collaboration...")
    try:
        result = await researcher.run(
            "Add a hypothesis: 'Multi-agent swarms with consciousness-aware tools "
            "can achieve better task decomposition than single agents.' "
            "Category: consciousness, Confidence: high",
            deps=deps
        )
        print(f"      💡 Researcher Response:")
        print(f"      {result.data if hasattr(result, 'data') else result}")
        print("      ✅ Test 3 PASSED")
    except Exception as e:
        print(f"      ❌ Test 3 FAILED: {e}")
    
    # Cleanup
    await acp_client.disconnect()
    
    print("\n" + "=" * 60)
    print("✨ RESEARCHER AGENT TEST COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_researcher_agent())
