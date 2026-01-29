#!/usr/bin/env python3
"""
Test Ada Swarm with GLM model via LiteLLM proxy
Quick math problem to verify the full stack works!
"""
import httpx
import json

# Ada Swarm API endpoint
SWARM_URL = "http://localhost:8765"

# Test task: Simple math problem for a research bee
task = {
    "description": "What is 17 * 23? Please show your work and explain the calculation.",
    "agent_type": "researcher",  # Use research agent
    "model": "litellm/glm-flash",  # GLM via LiteLLM proxy!
    "priority": 1
}

print("🐝 Submitting task to Ada Swarm...")
print(f"   Model: {task['model']}")
print(f"   Task: {task['description']}")
print()

try:
    # Submit task to swarm
    response = httpx.post(
        f"{SWARM_URL}/tasks",
        json=task,
        timeout=60.0
    )
    response.raise_for_status()
    
    result = response.json()
    task_id = result.get("task_id")
    
    print(f"✅ Task submitted! ID: {task_id}")
    print()
    print("📊 Response:")
    print(json.dumps(result, indent=2))
    
except httpx.HTTPError as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   Status: {e.response.status_code}")
        print(f"   Body: {e.response.text}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
