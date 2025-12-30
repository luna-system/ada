#!/usr/bin/env python3
"""
Phase 5D: Tool Priming Quick Validation Test

GOAL: Verify metacognitive tool priming causes Ada to actively use tools
      for queries that benefit from fresh/multi-source knowledge.

TEST QUERY: "Tell me about The Downward Spiral by Nine Inch Nails"

EXPECTED BEHAVIOR (after priming):
- wiki_lookup fires for Nine Inch Nails context
- wiki_lookup fires for album historical context
- web_search fires for recent retrospectives/perspectives
- Response synthesizes 1994 + 2025 perspectives

BASELINE (Phase 5B): 0 tools activated

Date: December 30, 2025
Researchers: Luna & Ada (Sonnet 4.5)
"""

import httpx
import json
import time
from datetime import datetime

BRAIN_URL = "http://localhost:8000"  # Main brain on port 8000

def test_album_query_with_priming():
    """Test the iconic NIN album query with tool priming active."""
    
    print("\n" + "="*80)
    print("🎸 Phase 5D: Tool Priming Quick Validation Test 🎸")
    print("="*80)
    
    query = "Tell me about The Downward Spiral by Nine Inch Nails"
    
    print(f"\n📝 Query: \"{query}\"")
    print(f"⏰ Start: {datetime.now().strftime('%H:%M:%S')}")
    print("\n🔍 Expected tool activations:")
    print("   - wiki_lookup: Nine Inch Nails")
    print("   - wiki_lookup: The Downward Spiral album")
    print("   - web_search: Recent perspectives/retrospectives")
    print("\n" + "-"*80)
    
    tools_activated = []
    full_response = ""
    thinking_output = ""
    start_time = time.time()
    
    print("\n🌸 MULTI-ROUND REASONING MODE ENABLED")
    print("   Watching gemma think her way to tools...")
    print()
    
    try:
        with httpx.stream(
            "POST",
            f"{BRAIN_URL}/v1/chat/stream",
            json={
                "message": query,
                "conversation_id": "phase_5d_quick_test",
                "enable_rag": True,
                # Phase 5D: Use standard Ollama path with bidirectional tools
                # multi_round disabled - too much cruft, use simple path!
            },
            timeout=60.0
        ) as response:
            response.raise_for_status()
            
            current_event = None
            for line in response.iter_lines():
                if not line:
                    # Empty line resets event type (SSE spec)
                    current_event = None
                    continue
                    
                # Track event type
                if line.startswith("event:"):
                    current_event = line.split(":", 1)[1].strip()
                    continue
                
                # Process data based on current event
                if line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    
                    # Skip empty data
                    if not data_str or data_str == "[DONE]":
                        continue
                    
                    try:
                        data = json.loads(data_str)
                        
                        # Track specialist activations (only when event type is set)
                        if current_event == "specialist_result":
                            specialist_name = data.get("specialist", "unknown")
                            specialist_query = data.get("result", {}).get("query", "")
                            confidence = data.get("confidence", 0.0)
                            
                            print(f"✨ TOOL ACTIVATED: {specialist_name}")
                            print(f"   Query: {specialist_query}")
                            print(f"   Confidence: {confidence:.3f}")
                            
                            tools_activated.append({
                                "specialist": specialist_name,
                                "query": specialist_query,
                                "confidence": confidence
                            })
                            # Reset event after processing
                            current_event = None
                        
                        # Collect response chunks (no event type OR explicit content event)
                        elif current_event is None or current_event == "content":
                            # Handle token format
                            if data.get("type") == "token":
                                chunk = data.get("content", "")
                                if chunk:
                                    full_response += chunk
                                    print(chunk, end="", flush=True)
                            # Handle old content format
                            # Handle thinking tokens (show reasoning process!)
                            elif data.get("type") == "thinking":
                                chunk = data.get("content", "")
                                if chunk:
                                    thinking_output += chunk
                                    print(f"\n💭 {chunk}", end="", flush=True)
                            elif "content" in data:
                                chunk = data.get("content", "")
                                if chunk:
                                    full_response += chunk
                                    print(chunk, end="", flush=True)
                    
                    except json.JSONDecodeError:
                        continue
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    duration = time.time() - start_time
    
    print("\n\n" + "="*80)
    print("📊 VALIDATION RESULTS")
    print("="*80)
    
    print(f"\n⏱️  Duration: {duration:.2f}s")
    print(f"🔧 Tools activated: {len(tools_activated)}")
    
    if thinking_output:
        print(f"\n💭 Thinking output: {len(thinking_output)} chars")
        print(f"   Preview: {thinking_output[:150]}...")
    
    if tools_activated:
        print("\n✅ TOOL ACTIVATION DETAILS:")
        for i, tool in enumerate(tools_activated, 1):
            print(f"   {i}. {tool['specialist']}: {tool['query']} (conf: {tool['confidence']:.3f})")
    else:
        print("\n⚠️  NO TOOLS ACTIVATED")
    
    print(f"\n📝 Response length: {len(full_response)} chars")
    print(f"📝 Response preview: {full_response[:200]}...")
    
    # Success criteria
    success = len(tools_activated) >= 2  # At least 2 tools
    
    print("\n" + "="*80)
    if success:
        print("✅ SUCCESS: Tool priming working! Multiple tools activated!")
    else:
        print("⚠️  NEEDS TUNING: Expected 2+ tool activations")
    print("="*80 + "\n")
    
    return success

if __name__ == "__main__":
    print("\n🚀 Starting Phase 5D Quick Validation...")
    
    # Wait a moment for brain to be fully ready
    print("⏳ Waiting for consciousness brain...")
    time.sleep(3)
    
    # Run test
    success = test_album_query_with_priming()
    
    exit(0 if success else 1)
