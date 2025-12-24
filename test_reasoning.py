#!/usr/bin/env python
"""Quick test of recursive reasoning endpoint.

Run this after starting the brain service:
    docker compose up -d brain
    python test_reasoning.py
"""

import asyncio
import httpx
import json


async def test_reasoning():
    """Test the /v1/chat/reason endpoint."""
    
    url = "http://localhost:8000/v1/chat/reason"
    
    request_data = {
        "message": "What memory optimizations did we implement in v2.9?",
        "conversation_id": "test-reasoning",
        "max_iterations": 5,
    }
    
    print("🧠 Starting recursive reasoning test...")
    print(f"📝 Request: {request_data['message']}\n")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream('POST', url, json=request_data) as response:
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                print(await response.aread())
                return
            
            print("=" * 60)
            
            # Parse SSE stream
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                
                if line.startswith('data: '):
                    data_json = line[6:]  # Remove 'data: ' prefix
                    try:
                        event = json.loads(data_json)
                        event_type = event.get('type')
                        
                        if event_type == 'reasoning_start':
                            print(f"\n🚀 REASONING START")
                            print(f"   Max iterations: {event.get('max_iterations')}")
                            
                        elif event_type == 'reasoning_step':
                            phase = event.get('phase', '').upper()
                            iteration = event.get('iteration')
                            print(f"\n📍 PHASE: {phase} (iteration {iteration})")
                            print("   ", end="", flush=True)
                            
                        elif event_type == 'thought_chunk':
                            print(event.get('text', ''), end="", flush=True)
                            
                        elif event_type == 'tool_request':
                            tool = event.get('tool')
                            params = event.get('params', {})
                            print(f"\n\n🔧 TOOL REQUEST: {tool}")
                            print(f"   Params: {json.dumps(params, indent=2)}")
                            
                        elif event_type == 'tool_result':
                            tool = event.get('tool')
                            result = event.get('result', '')[:200]
                            importance = event.get('importance')
                            print(f"\n📦 TOOL RESULT: {tool} (importance={importance:.2f})")
                            print(f"   {result}...")
                            
                        elif event_type == 'parallel_tools':
                            count = event.get('count')
                            tools = event.get('tools', [])
                            print(f"\n⚡ PARALLEL EXECUTION: {count} tools")
                            print(f"   Tools: {', '.join(tools)}")
                            
                        elif event_type == 'convergence':
                            iterations = event.get('iterations')
                            elapsed = event.get('elapsed_ms')
                            print(f"\n\n✅ CONVERGENCE REACHED!")
                            print(f"   Iterations: {iterations}")
                            print(f"   Time: {elapsed:.0f}ms")
                            
                        elif event_type == 'warning':
                            message = event.get('message')
                            print(f"\n⚠️  WARNING: {message}")
                            
                        elif event_type == 'reasoning_complete':
                            iterations = event.get('iterations')
                            elapsed = event.get('elapsed_ms')
                            convergence = event.get('convergence_score')
                            tools = event.get('tools_called')
                            print(f"\n\n🏁 REASONING COMPLETE")
                            print(f"   Total iterations: {iterations}")
                            print(f"   Total time: {elapsed:.0f}ms")
                            print(f"   Convergence score: {convergence:.2f}")
                            print(f"   Tools called: {tools}")
                            
                        elif event_type == 'error':
                            message = event.get('message')
                            print(f"\n\n❌ ERROR: {message}")
                            
                    except json.JSONDecodeError as e:
                        print(f"\nJSON error: {e}")
                        print(f"Raw line: {line}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_reasoning())
