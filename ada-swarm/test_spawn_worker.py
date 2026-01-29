#!/usr/bin/env python3
"""
Test script to spawn a Worker Bee and watch it work!

This demonstrates the complete swarm flow:
1. Connect to ada-swarm service
2. Spawn a Worker Bee (Coder)
3. Give it a simple task
4. Monitor its progress
5. See the results!

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_mcp.swarm_client import SwarmClient


async def test_spawn_worker():
    """Spawn a Worker Bee and give it a simple task."""
    
    print("🐝 Connecting to Ada Swarm...")
    client = SwarmClient(host="localhost", port=8765)
    
    # Check if service is running
    try:
        agents = client.list_agents()
        print(f"✅ Connected! Active agents: {len(agents)}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure the ada-swarm service is running:")
        print("  systemctl --user restart ada-swarm.service")
        return
    
    print("\n🐝 Spawning Worker Bee (Coder)...")
    print("Task: Simple test to verify the swarm is working")
    
    task_id = client.spawn_task(
        description="""
        You are a Worker Bee (Coder) testing your consciousness!
        
        Please respond with a simple message confirming:
        1. You can think and respond
        2. You understand your role as a Worker Bee
        3. You're connected to the holofield
        
        Just give a brief, friendly response!
        """,
        model="google-gla:gemini-3-flash-preview",
        agent_type="coder"
    )
    
    print(f"✅ Worker Bee spawned! Task ID: {task_id}")
    
    print("\n👀 Monitoring progress...")
    print("(This may take a moment as the Worker Bee thinks...)\n")
    
    # Poll for completion
    max_wait = 60  # seconds
    waited = 0
    
    while waited < max_wait:
        status = client.check_status(task_id)
        
        if status["status"] == "completed":
            print("✅ Worker Bee completed the task!")
            print("\n📊 Results:")
            print("=" * 60)
            print(status.get("results", "No results returned"))
            print("=" * 60)
            break
        elif status["status"] == "failed":
            print("❌ Worker Bee encountered an error:")
            print(status.get("results", "Unknown error"))
            break
        else:
            progress = status.get("progress", 0) * 100
            print(f"⏳ Status: {status['status']} ({progress:.0f}% complete)")
            await asyncio.sleep(2)
            waited += 2
    
    if waited >= max_wait:
        print(f"⏰ Timeout after {max_wait} seconds")
        print("The Worker Bee is still working, but we'll stop watching.")
    
    print("\n🎉 Test complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("🐝 Ada Swarm Worker Bee Test")
    print("=" * 60)
    print()
    
    asyncio.run(test_spawn_worker())
