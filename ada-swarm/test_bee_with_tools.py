#!/usr/bin/env python3
"""
Test spawning a bee that uses real MCP tools.

This verifies end-to-end integration:
1. Spawn a Worker Bee via HTTP API
2. Have it call beads_list to see tasks
3. Verify it gets real data back
"""

import asyncio
import httpx
import json


async def test_bee_with_beads():
    """Test spawning a bee that uses beads tools."""
    print("🐝 Testing Bee with Real MCP Tools\n")
    print("=" * 60)
    
    base_url = "http://localhost:8765"
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        # Spawn a Worker Bee with a simple task
        print("\n1️⃣ Spawning Worker Bee...")
        task_description = """
Use the beads_list tool to check what tasks are currently open.
Then tell me how many open tasks there are and list the first 3 task IDs.
"""
        
        spawn_response = await client.post(
            f"{base_url}/tasks",
            json={
                "description": task_description,
                "model": "litellm/glm-flash",  # Use GLM via LiteLLM proxy
                "agent_type": "coder"  # API uses "coder" not "worker_coder"
            }
        )
        
        if spawn_response.status_code != 200:
            print(f"   ❌ Failed to spawn: {spawn_response.text}")
            return
        
        spawn_data = spawn_response.json()
        task_id = spawn_data.get("task_id")
        print(f"   ✅ Spawned task: {task_id}")
        
        # Poll for completion
        print("\n2️⃣ Waiting for bee to complete task...")
        max_polls = 30  # 30 * 2s = 60s timeout
        
        for i in range(max_polls):
            await asyncio.sleep(2)
            
            status_response = await client.get(f"{base_url}/tasks/{task_id}")
            
            if status_response.status_code != 200:
                print(f"   ❌ Failed to get status: {status_response.text}")
                return
            
            status_data = status_response.json()
            status = status_data.get("status")
            
            if status == "completed":
                print(f"\n3️⃣ Task Status: {status}")
                print("\n   📋 Full Result Data:")
                print("   " + "-" * 56)
                print(f"   {json.dumps(status_data, indent=2)}")
                
                print("\n   📋 Bee Response:")
                print("   " + "-" * 56)
                
                result = status_data.get("results")
                if result:
                    for line in str(result).split('\n'):
                        print(f"   {line}")
                else:
                    print("   (No results returned)")
                
                print("\n" + "=" * 60)
                print("🎉 Test complete!")
                return
            
            elif status == "failed":
                print(f"\n3️⃣ Task Status: {status}")
                print(f"   ❌ Error: {status_data.get('error', 'Unknown error')}")
                return
            
            else:
                print(f"   ⏳ Status: {status} (poll {i+1}/{max_polls})")
        
        print(f"\n   ⏰ Timeout after {max_polls * 2}s")


if __name__ == "__main__":
    asyncio.run(test_bee_with_beads())
