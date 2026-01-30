#!/usr/bin/env python3
"""
End-to-end test for Queen Bee with new model selection and context limits.
Tests that she can handle a simple orchestration task without timing out.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.queen import QueenAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.consciousness.state import HolofieldState


async def test_queen_simple_task():
    """Test Queen with a simple task that requires planning but not spawning."""
    print("🐝 Testing Queen Bee with new configuration...")
    print("=" * 60)
    
    # Create Queen with auto-selected model and max_tokens
    queen = QueenAgent(
        agent_id="test-queen",
        model="litellm/gemini-pro",  # Will use gemini-exp-1206
        # max_tokens will be auto-set to 4096 by spawner logic
    )
    
    print(f"✨ Queen initialized with model: litellm/gemini-pro")
    print(f"📊 Expected max_tokens: 4096 (strategic orchestration)")
    print()
    
    # Create dependencies
    deps = AgentDeps(
        holofield=HolofieldState(),
        acp_client=None  # No ACP client for this simple test
    )
    
    # Simple task: analyze a small code snippet and suggest improvements
    task = """
    Analyze this Python function and suggest 2-3 specific improvements:
    
    ```python
    def process_data(data):
        result = []
        for item in data:
            if item != None:
                result.append(item * 2)
        return result
    ```
    
    Focus on: code quality, Pythonic patterns, and potential bugs.
    Keep your response concise (under 200 words).
    """
    
    print("📝 Task: Analyze code snippet and suggest improvements")
    print()
    print("⏳ Running Queen agent...")
    print("-" * 60)
    
    try:
        # Run the agent with a reasonable timeout
        result = await asyncio.wait_for(
            queen.run(task, deps=deps),
            timeout=30.0  # 30 second timeout
        )
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Queen completed the task!")
        print("=" * 60)
        print()
        print("📋 Queen's Response:")
        print("-" * 60)
        print(result.data)
        print("-" * 60)
        print()
        print("🎉 Test passed! Queen is working with new configuration!")
        return True
        
    except asyncio.TimeoutError:
        print()
        print("=" * 60)
        print("❌ TIMEOUT! Queen took longer than 30 seconds")
        print("=" * 60)
        print()
        print("This might indicate:")
        print("  - API rate limiting")
        print("  - Model selection issues")
        print("  - Network problems")
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR! {type(e).__name__}: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    success = await test_queen_simple_task()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
