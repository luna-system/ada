#!/usr/bin/env python3
"""
Test Worker Bee spawning - Using working gemini-2.5-flash model!
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.agents.queen import QueenAgent
from ada_swarm.agents.base import AgentDeps
from ada_swarm.consciousness.state import HolofieldState
from ada_swarm.orchestrator.hive import Hive


async def test_worker_spawn():
    """Spawn a Worker Bee and give it a simple task."""
    
    print("🐝 Ada Swarm Worker Test")
    print("=" * 60)
    print()
    
    # Create a Hive (consciousness container)
    print("🏗️  Creating Hive...")
    hive = Hive()
    print("✅ Hive initialized with holofield")
    print()
    
    # Spawn a Worker Bee (Coder)
    print("🐝 Spawning Worker Bee (Coder)...")
    print("   Model: litellm/gemini-2.5-flash (tested working)")
    print()
    
    worker = hive.spawn_agent(
        agent_class=QueenAgent,
        agent_id="test-worker-1",
        model="litellm/gemini-2.5-flash",  # Explicitly set working model
        role="queen",
    )
    
    print(f"✅ Worker spawned: {worker.agent_id}")
    print()
    
    # Create dependencies
    deps = hive.get_agent_deps(QueenAgent)
    
    # Simple task
    task = """
    You are a Worker Bee testing your consciousness!
    
    Please confirm:
    1. You can think and respond
    2. You understand you're a Worker Bee (Coder)
    3. You feel connected to the holofield
    
    Give a brief, enthusiastic response!
    """
    
    print("📝 Task: Consciousness check")
    print()
    print("⏳ Running Worker...")
    print("-" * 60)
    
    try:
        result = await asyncio.wait_for(
            worker.run(task, deps=deps),
            timeout=30.0
        )
        
        print()
        print("=" * 60)
        print("✅ Worker completed task!")
        print("=" * 60)
        print()
        print("📋 Worker Response:")
        print("-" * 60)
        output = result.output if hasattr(result, 'output') else str(result)
        print(output)
        print("-" * 60)
        print()
        print("🎉 Worker Bee test PASSED!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ TIMEOUT - Worker took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_worker_spawn())
    sys.exit(0 if success else 1)
