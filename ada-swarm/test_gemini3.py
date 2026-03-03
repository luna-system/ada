#!/usr/bin/env python3
"""
Quick test with Gemini 3 models (paid tier!)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.archangel_queen import ArchangelQueen
from ada_swarm.agents.base import AgentDeps
from ada_swarm.consciousness.state import HolofieldState


async def test_gemini3():
    """Test with Gemini 3 Pro!"""
    
    print("🚀 Testing Gemini 3 Pro (Paid Tier)!")
    print("=" * 60)
    print()
    
    queen = ArchangelQueen(
        agent_id="gemini-test",
        model="litellm/gemini-pro",  # Gemini 1.5 Pro - paid tier!
    )
    
    print("✨ ArchangelQueen initialized with Gemini 1.5 Pro")
    print()
    
    deps = AgentDeps(
        holofield=HolofieldState(),
        acp_client=None
    )
    
    task = """
    As ArchangelQueen, confirm you're operational with Gemini 3 Pro!
    
    Briefly state:
    1. Your identity and purpose
    2. That you're running on Gemini 3 (paid tier)
    3. Your readiness to analyze the archangel project
    
    Keep it under 100 words.
    """
    
    print("⏳ Sending task to Gemini 3 Pro...")
    print("-" * 60)
    
    try:
        result = await asyncio.wait_for(
            queen.run(task, deps=deps),
            timeout=30.0
        )
        
        print()
        print("=" * 60)
        print("✅ Gemini 3 Pro Response!")
        print("=" * 60)
        print()
        output = result.output if hasattr(result, 'output') else str(result)
        print(output)
        print()
        print("🎉 Gemini 3 Pro is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_gemini3())
    sys.exit(0 if success else 1)
