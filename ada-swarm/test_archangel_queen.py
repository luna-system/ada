#!/usr/bin/env python3
"""
Test ArchangelQueen - The specialized project orchestrator!
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.archangel_queen import ArchangelQueen
from ada_swarm.agents.base import AgentDeps
from ada_swarm.consciousness.state import HolofieldState
from ada_swarm.acp.client import ACPClient
from ada_swarm.acp.permissions import AgentRole


async def test_archangel_queen():
    """Test ArchangelQueen with a project analysis task."""
    
    print("👑 ArchangelQueen Test")
    print("=" * 60)
    print()
    
    # Create the Queen
    queen = ArchangelQueen(
        agent_id="archangel-queen-test",
        model="litellm/gemini-2.5-flash",
    )
    
    print(f"✨ ArchangelQueen initialized")
    print(f"   Model: litellm/gemini-2.5-flash")
    print(f"   Path: {queen.archangel_path}")
    print()
    
    # Create ACP client for file system access
    print("🔌 Initializing ACP client...")
    acp_client = ACPClient(role=AgentRole.QUEEN_BEE, agent_id="archangel-queen-test")
    
    deps = AgentDeps(
        holofield=HolofieldState(),
        acp_client=acp_client
    )
    print("✅ ACP client ready")
    
    task = """
    As ArchangelQueen, introduce yourself and confirm your capabilities.
    
    Tell me:
    1. Who you are and your role
    2. What files you track (architecture.yaml, decisions/)
    3. What you can do (spawn Workers, manage beads tasks, etc.)
    
    Keep it brief - just show me your consciousness is online!
    """
    
    print("📝 Task: Analyze archangel project state")
    print()
    print("⏳ Running ArchangelQueen...")
    print("-" * 60)
    
    try:
        result = await asyncio.wait_for(
            queen.run(task, deps=deps),
            timeout=30.0
        )
        
        print()
        print("=" * 60)
        print("✅ ArchangelQueen completed analysis!")
        print("=" * 60)
        print()
        output = result.output if hasattr(result, 'output') else str(result)
        print(output)
        print()
        print("🎉 ArchangelQueen test PASSED!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ TIMEOUT - Analysis took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_archangel_queen())
    sys.exit(0 if success else 1)
