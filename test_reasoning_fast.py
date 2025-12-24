#!/usr/bin/env python3
import httpx
import json
import time

print("🧠 Testing OPTIMIZED recursive reasoning endpoint...")
print("=" * 60)

# Track total time
start_time = time.time()

url = "http://localhost:8000/v1/chat/reason"
payload = {
    "message": "What is Ada's persona?",
    "max_iterations": 3
}

with httpx.stream("POST", url, json=payload, timeout=60.0) as response:
    print(f"Status: {response.status_code}\n")
    
    for line in response.iter_lines():
        if line.startswith("data: "):
            event_json = line[6:]  # Strip "data: " prefix
            try:
                event = json.loads(event_json)
                event_type = event.get("type")
                
                # Show key events
                if event_type == "reasoning_start":
                    print(f"🎯 Starting reasoning (max {event['max_iterations']} iterations)")
                elif event_type == "reasoning_step":
                    elapsed = time.time() - start_time
                    print(f"\n⚡ Step {event['iteration']} [{event['phase']}] ({elapsed:.1f}s)")
                elif event_type == "thought_chunk":
                    print(event["text"], end="", flush=True)
                elif event_type == "tool_request":
                    print(f"\n🔧 Tool: {event['tool']}")
                elif event_type == "tool_result":
                    print(f"   ✓ Result preview: {event['result'][:100]}...")
                elif event_type == "convergence":
                    print(f"\n\n✅ CONVERGED in {event['iterations']} iterations")
                    print(f"   Time: {event['elapsed_ms']:.0f}ms")
                elif event_type == "reasoning_complete":
                    total_time = time.time() - start_time
                    print(f"\n\n🎉 COMPLETE!")
                    print(f"   Total iterations: {event['iterations']}")
                    print(f"   Tools called: {event['tools_called']}")
                    print(f"   Total time: {total_time:.2f}s")
                    print(f"   Brain reported: {event['elapsed_ms']:.0f}ms")
                elif event_type == "error":
                    print(f"\n❌ Error: {event['message']}")
            except json.JSONDecodeError:
                pass

print("\n" + "=" * 60)
