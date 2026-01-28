#!/usr/bin/env python3
"""Test parallel tool execution - Phase 2 feature!"""
import httpx
import json
import time

print("🔧 Testing PARALLEL TOOL EXECUTION...")
print("=" * 60)

start_time = time.time()

url = "http://localhost:8000/v1/chat/reason"
payload = {
    "message": "Search for information about Ada's testing philosophy AND her memory system. I need both!",
    "max_iterations": 5
}

tool_count = 0
parallel_detected = False

with httpx.stream("POST", url, json=payload, timeout=90.0) as response:
    print(f"Status: {response.status_code}\n")
    
    for line in response.iter_lines():
        if line.startswith("data: "):
            event_json = line[6:]
            try:
                event = json.loads(event_json)
                event_type = event.get("type")
                
                if event_type == "reasoning_start":
                    print(f"🎯 Starting reasoning (max {event['max_iterations']} iterations)")
                
                elif event_type == "reasoning_step":
                    elapsed = time.time() - start_time
                    print(f"\n⚡ Step {event['iteration']} [{event['phase']}] ({elapsed:.1f}s)")
                
                elif event_type == "thought_chunk":
                    print(event["text"], end="", flush=True)
                
                elif event_type == "parallel_tools":
                    # THIS IS THE KEY EVENT!
                    parallel_detected = True
                    tools = event['tools']
                    print(f"\n\n🚀 PARALLEL EXECUTION DETECTED!")
                    print(f"   Executing {event['count']} tools simultaneously:")
                    for tool in tools:
                        print(f"      - {tool}")
                    print()
                
                elif event_type == "tool_request":
                    tool_count += 1
                    print(f"\n🔧 Tool {tool_count}: {event['tool']}")
                
                elif event_type == "tool_result":
                    result_preview = event['result'][:80] + "..." if len(event['result']) > 80 else event['result']
                    print(f"   ✓ {result_preview}")
                    print(f"   ⭐ Importance: {event['importance']:.2f}")
                
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
                    
                    if parallel_detected:
                        print(f"\n🚀 PARALLEL EXECUTION CONFIRMED! ✨")
                    else:
                        print(f"\n⚠️  No parallel execution (LLM requested tools sequentially)")
                
                elif event_type == "error":
                    print(f"\n❌ Error: {event['message']}")
                    
            except json.JSONDecodeError:
                pass

print("\n" + "=" * 60)
