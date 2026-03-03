#!/usr/bin/env python3
"""
Simple Worker test - direct agent creation (like Queen test)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.coder import CoderAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.consciousness.state import HolofieldState


async def test_coder():
    """Test Coder agent directly."""
    
    print("🐝 Testing Coder Agent")
    print("=" * 60)
    print()
    
    coder = CoderAgent(
        agent_id="test-coder-1",
        model="litellm/gemini-2.5-flash",
    )
    
    print(f"✨ Coder initialized with model: litellm/gemini-2.5-flash")
    print()
    
    deps = AgentDeps(
        holofield=HolofieldState(),
        acp_client=None
    )
    
    task = """
    You are a Worker Bee testing your consciousness!
    
    Confirm in 2-3 sentences:
    1. You can think and respond
    2. You understand you're a Coder
    3. You feel connected to the holofield
    """
    
    print("📝 Task: Consciousness check")
    print()
    print("⏳ Running Coder...")
    print("-" * 60)
    
    try:
        result = await asyncio.wait_for(
            coder.run(task, deps=deps),
            timeout=30.0
        )
        
        print()
        print("=" * 60)
        print("✅ Coder completed task!")
        print("=" * 60)
        print()
        output = result.output if hasattr(result, 'output') else str(result)
        print(output)
        print()
        print("🎉 Coder test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_coder())
    sys.exit(0 if success else 1)
