#!/usr/bin/env python3
"""Test the new file operation tools!"""
import httpx
import json
import time

print("📂 Testing FILE OPERATION TOOLS...")
print("=" * 60)

start_time = time.time()

url = "http://localhost:8000/v1/chat/reason"
payload = {
    "message": """I need to understand the reasoning system architecture by reading ACTUAL FILES from the workspace.

IMPORTANT: Do NOT use brain_search - that's for memory! Use the FILE TOOLS:
1. Use brain_list_dir to list files in brain/reasoning/ directory
2. Use brain_read_file to read loop_controller.py (first 100 lines)
3. Use brain_grep to search for 'async def' in all reasoning files

Remember: brain_search = memory, brain_read_file = actual file contents!""",
    "max_iterations": 8
}

tool_count = 0
file_tools_used = []

with httpx.stream("POST", url, json=payload, timeout=120.0) as response:
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
                    tools = event['tools']
                    print(f"\n\n🚀 PARALLEL EXECUTION: {len(tools)} tools simultaneously!")
                    for tool in tools:
                        print(f"      - {tool}")
                        if tool.startswith("brain_"):
                            file_tools_used.append(tool)
                    print()
                
                elif event_type == "tool_request":
                    tool_count += 1
                    tool_name = event['tool']
                    if tool_name.startswith("brain_") and tool_name != "brain_search":
                        file_tools_used.append(tool_name)
                    print(f"\n🔧 Tool {tool_count}: {tool_name}")
                    if event.get('params'):
                        print(f"   Params: {event['params']}")
                
                elif event_type == "tool_result":
                    result = event['result']
                    # Show preview of result
                    lines = result.split('\n')[:5]
                    print(f"   ✓ Result ({len(result)} chars):")
                    for line in lines:
                        print(f"     {line}")
                    if len(result.split('\n')) > 5:
                        print(f"     ... ({len(result.split('\n'))-5} more lines)")
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
                    
                    print(f"\n📂 FILE TOOLS USED:")
                    unique_tools = set(file_tools_used)
                    if unique_tools:
                        for tool in sorted(unique_tools):
                            count = file_tools_used.count(tool)
                            print(f"   ✅ {tool} ({count}x)")
                    else:
                        print(f"   ⚠️  No file tools used!")
                
                elif event_type == "error":
                    print(f"\n❌ Error: {event['message']}")
                    
            except json.JSONDecodeError:
                pass

print("\n" + "=" * 60)
