#!/usr/bin/env python3
"""
Test reasoning mode integration for ada-chat extension

Tests that /v1/chat/reason endpoint streams proper events:
- tool_transparency with importance/signals
- tool_result with actual results
- token events with response content
- done event

This validates the FULL PIPELINE for ada-chat's big debut!
"""
import requests
import json
import time
import sys

BRAIN_URL = "http://localhost:8000"

def test_reasoning_integration():
    """Test reasoning mode with complex query"""
    
    print("🧠 Testing reasoning mode integration...")
    print("=" * 60)
    
    # Complex query that should trigger reasoning mode
    query = "Analyze the brain/reasoning directory - list files then read loop_controller.py"
    
    print(f"Query: {query}")
    print()
    
    # Make request to reason endpoint
    response = requests.post(
        f"{BRAIN_URL}/v1/chat/reason",
        json={
            "messages": [
                {"role": "user", "content": query}
            ]
        },
        stream=True,
        timeout=60,
        headers={"Accept": "text/event-stream"}
    )
    
    if response.status_code != 200:
        print(f"❌ ERROR: {response.status_code} - {response.text}")
        return False
    
    # Track what we receive
    events_received = {
        'tool_transparency': [],
        'tool_result': [],
        'thinking': [],
        'token': 0,
        'done': False
    }
    
    print("📡 Streaming events:")
    print()
    
    # Process SSE stream
    for line in response.iter_lines():
        if not line:
            continue
            
        line = line.decode('utf-8')
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                event_type = data.get('type')
                
                if event_type == 'tool_transparency':
                    events_received['tool_transparency'].append(data)
                    print(f"✨ TOOL TRANSPARENCY:")
                    print(f"   Tool: {data.get('tool')}")
                    print(f"   Importance: {data.get('importance', 0):.3f}")
                    print(f"   Detail Level: {data.get('detail_level', 'unknown')}")
                    print(f"   Cache Hit: {data.get('cache_hit', False)}")
                    print(f"   Execution Time: {data.get('execution_time_ms', 0):.2f}ms")
                    
                    signals = data.get('signals', {})
                    if signals:
                        print(f"   Signals:")
                        for name, value in signals.items():
                            print(f"      {name}: {value:.2f}")
                    print()
                    
                elif event_type == 'tool_result':
                    events_received['tool_result'].append(data)
                    result_preview = str(data.get('result', ''))[:100]
                    print(f"🔧 TOOL RESULT:")
                    print(f"   Tool: {data.get('tool')}")
                    print(f"   Success: {data.get('success', False)}")
                    print(f"   Result preview: {result_preview}...")
                    print()
                    
                elif event_type == 'thinking':
                    events_received['thinking'].append(data)
                    # Don't print every thinking event, just count
                    
                elif event_type == 'token':
                    events_received['token'] += 1
                    # Don't print every token, just accumulate
                    
                elif event_type == 'done':
                    events_received['done'] = True
                    print("✅ DONE")
                    break
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parse error: {e}")
                continue
    
    # Summary
    print()
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"   Tool Transparency Events: {len(events_received['tool_transparency'])}")
    print(f"   Tool Result Events: {len(events_received['tool_result'])}")
    print(f"   Thinking Events: {len(events_received['thinking'])}")
    print(f"   Token Events: {events_received['token']}")
    print(f"   Done: {events_received['done']}")
    print()
    
    # Validate we got what we expected
    success = True
    
    if len(events_received['tool_transparency']) == 0:
        print("❌ FAIL: No tool_transparency events received")
        success = False
    else:
        # Check first transparency event has all required fields
        first = events_received['tool_transparency'][0]
        required = ['tool', 'importance', 'detail_level', 'cache_hit', 'execution_time_ms', 'signals']
        missing = [f for f in required if f not in first]
        if missing:
            print(f"❌ FAIL: tool_transparency missing fields: {missing}")
            success = False
        else:
            print("✅ PASS: tool_transparency events have all required fields")
    
    if len(events_received['tool_result']) == 0:
        print("❌ FAIL: No tool_result events received")
        success = False
    else:
        print("✅ PASS: tool_result events received")
    
    if events_received['token'] == 0:
        print("❌ FAIL: No token events received")
        success = False
    else:
        print(f"✅ PASS: {events_received['token']} token events received")
    
    if not events_received['done']:
        print("❌ FAIL: No done event received")
        success = False
    else:
        print("✅ PASS: done event received")
    
    print()
    
    if success:
        print("🎉 ALL TESTS PASSED! Ada-chat is ready for the big debut! ✨")
        return True
    else:
        print("😞 Some tests failed. Check the output above.")
        return False


if __name__ == '__main__':
    try:
        success = test_reasoning_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
