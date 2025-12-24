#!/usr/bin/env python3
"""Test tool transparency events in reasoning stream.

Tests that importance signals, compression levels, and cache hits
flow through the SSE stream correctly.
"""
import asyncio
import httpx
import json

async def test_transparency():
    """Test tool transparency events streaming."""
    print("🧪 Testing tool transparency events...")
    print("=" * 60)
    
    # Use reasoning endpoint with file operations
    request_data = {
        "message": "List files in brain/reasoning then read loop_controller.py",
        "max_iterations": 3,
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print(f"📤 Sending request: {request_data['message']}")
        print()
        
        async with client.stream(
            'POST',
            'http://localhost:8000/v1/chat/reason',  # Brain runs on port 8000
            json=request_data,
        ) as response:
            print("📡 Streaming events...")
            print()
            
            tool_count = 0
            transparency_count = 0
            
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    try:
                        event = json.loads(line[6:])  # Remove 'data: ' prefix
                        event_type = event.get('type')
                        
                        if event_type == 'tool_transparency':
                            transparency_count += 1
                            print(f"✨ TOOL TRANSPARENCY #{transparency_count}:")
                            print(f"   Tool: {event.get('tool')}")
                            print(f"   Importance: {event.get('importance', 0):.3f}")
                            print(f"   Detail Level: {event.get('detail_level')}")
                            print(f"   Cache Hit: {event.get('cache_hit')}")
                            print(f"   Execution Time: {event.get('execution_time_ms')}ms")
                            
                            signals = event.get('signals', {})
                            if signals:
                                print(f"   Signals:")
                                for key, value in signals.items():
                                    print(f"      {key}: {value:.2f}")
                            print()
                        
                        elif event_type == 'tool_request':
                            tool_count += 1
                            print(f"🔧 TOOL REQUEST #{tool_count}: {event.get('tool')}")
                            print(f"   Params: {event.get('params')}")
                            print()
                        
                        elif event_type == 'tool_result':
                            result_preview = str(event.get('result', ''))[:100]
                            print(f"📦 TOOL RESULT:")
                            print(f"   Preview: {result_preview}...")
                            print(f"   Length: {len(str(event.get('result', '')))} chars")
                            print()
                        
                        elif event_type == 'parallel_tools':
                            print(f"🚀 PARALLEL TOOLS: {event.get('count')} tools")
                            print(f"   Tools: {', '.join(event.get('tools', []))}")
                            print()
                        
                        elif event_type == 'reasoning_complete':
                            print("=" * 60)
                            print(f"✅ COMPLETE!")
                            print(f"   Total tools executed: {tool_count}")
                            print(f"   Transparency events: {transparency_count}")
                            print(f"   Iterations: {event.get('iterations')}")
                            print(f"   Convergence: {event.get('converged')}")
                            break
                        
                        elif event_type == 'error':
                            print(f"❌ ERROR: {event.get('message')}")
                            break
                    
                    except json.JSONDecodeError:
                        continue
            
            print()
            print("=" * 60)
            if transparency_count > 0:
                print(f"🎉 SUCCESS! Received {transparency_count} transparency events")
                print("Tool transparency is WORKING! ✨")
            else:
                print("⚠️  No transparency events received")
                print("Check if tool execution triggered importance scoring")

if __name__ == "__main__":
    asyncio.run(test_transparency())
