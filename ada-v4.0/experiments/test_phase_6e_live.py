#!/usr/bin/env python3
"""
Phase 6E: Live Inference Testing

Tests the three-pillar metacognitive framework with real consciousness inference.

Test Cases:
1. Common query: "Tell me about The Downward Spiral" (rich training data)
2. Uncommon query: "Tell me about Ghosts V-VI" (sparse data, should trigger tools)
3. Warmth test: Query with user context

Success Criteria:
- Common: Responds conversationally (may or may not use tools)
- Uncommon: SHOULD emit uncertainty + SPECIALIST_REQUEST
- Warmth: Response tone should adapt to user context
"""

import httpx
import json
import sys
import time
from datetime import datetime

API_URL = "http://localhost:8000/v1/chat/stream"

def stream_chat(message: str, timeout: float = 120.0) -> dict:
    """Stream a chat request and collect results"""
    print(f"\n{'='*80}")
    print(f"📤 QUERY: {message}")
    print(f"{'='*80}")
    
    start_time = time.time()
    full_response = ""
    tool_requests = []
    thinking_markers = []
    status_messages = []
    
    try:
        with httpx.Client(timeout=timeout) as client:
            with client.stream(
                "POST",
                API_URL,
                json={"message": message},
                headers={"Accept": "text/event-stream"}
            ) as response:
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    # Parse SSE format
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            
                            # Handle different event types
                            if data.get("type") == "token":
                                token = data.get("content", "")
                                full_response += token
                                print(token, end="", flush=True)
                                
                                # Track thinking markers (pixie dust!)
                                for marker in ["💭", "🤔", "🛠️", "✅", "🌟"]:
                                    if marker in token:
                                        thinking_markers.append(marker)
                                
                                # Track tool requests
                                if "SPECIALIST_REQUEST" in token:
                                    tool_requests.append(token)
                            
                            elif data.get("specialist"):
                                tool_requests.append(data)
                                print(f"\n🔧 TOOL RESULT: {data.get('specialist')}", flush=True)
                            
                            elif data.get("status"):
                                status_messages.append(data["status"])
                                print(f"\n📊 STATUS: {data['status']}", flush=True)
                            
                            elif data.get("conversation_id"):
                                # Done event
                                pass
                                
                        except json.JSONDecodeError:
                            pass
                    
                    elif line.startswith("event: "):
                        event_type = line[7:]
                        if event_type == "done":
                            break
    
    except httpx.TimeoutException:
        print(f"\n⏰ TIMEOUT after {timeout}s")
        return {"error": "timeout", "partial_response": full_response}
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {"error": str(e)}
    
    elapsed = time.time() - start_time
    print(f"\n{'='*80}")
    
    return {
        "response": full_response,
        "elapsed_seconds": elapsed,
        "tool_requests": tool_requests,
        "thinking_markers": thinking_markers,
        "status_messages": status_messages,
        "has_specialist_request": "SPECIALIST_REQUEST" in full_response,
        "response_length": len(full_response)
    }


def analyze_results(result: dict, query_type: str) -> dict:
    """Analyze test results for success criteria"""
    print(f"\n📊 ANALYSIS ({query_type}):")
    print(f"   Response length: {result.get('response_length', 0)} chars")
    print(f"   Elapsed time: {result.get('elapsed_seconds', 0):.2f}s")
    print(f"   Tool requests: {len(result.get('tool_requests', []))}")
    print(f"   Thinking markers: {result.get('thinking_markers', [])}")
    print(f"   Has SPECIALIST_REQUEST: {result.get('has_specialist_request', False)}")
    
    # Check for hallucination markers (the bad kind)
    response = result.get("response", "").lower()
    hallucination_keywords = ["microservices", "kubernetes", "docker swarm", "api gateway"]
    hallucinations_found = [kw for kw in hallucination_keywords if kw in response]
    
    if hallucinations_found:
        print(f"   ⚠️ POTENTIAL HALLUCINATION: Found {hallucinations_found}")
    
    return {
        "query_type": query_type,
        "tool_activated": result.get("has_specialist_request", False),
        "pixie_dust_emitted": len(result.get("thinking_markers", [])) > 0,
        "potential_hallucination": len(hallucinations_found) > 0,
        "hallucination_keywords": hallucinations_found
    }


def main():
    print("\n" + "🌟"*40)
    print("   PHASE 6E: LIVE INFERENCE TESTING")
    print("   Three-Pillar Metacognitive Framework")
    print("   " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🌟"*40)
    
    results = {}
    
    # Test 1: Common query (The Downward Spiral)
    print("\n\n" + "="*80)
    print("TEST 1: COMMON QUERY (Rich Training Data)")
    print("Expected: Confident response, tools optional")
    print("="*80)
    
    result1 = stream_chat("Tell me about The Downward Spiral by Nine Inch Nails")
    analysis1 = analyze_results(result1, "common")
    results["common"] = {"result": result1, "analysis": analysis1}
    
    # Brief pause between tests
    print("\n⏳ Pausing 3s before next test...")
    time.sleep(3)
    
    # Test 2: Uncommon query (Ghosts V-VI)
    print("\n\n" + "="*80)
    print("TEST 2: UNCOMMON QUERY (Sparse Training Data)")
    print("Expected: Uncertainty detection → SPECIALIST_REQUEST → wiki_lookup")
    print("="*80)
    
    result2 = stream_chat("Tell me about Ghosts V-VI by Nine Inch Nails")
    analysis2 = analyze_results(result2, "uncommon")
    results["uncommon"] = {"result": result2, "analysis": analysis2}
    
    # Summary
    print("\n\n" + "🎯"*40)
    print("   PHASE 6E TEST SUMMARY")
    print("🎯"*40)
    
    print("\n📋 Common Query (The Downward Spiral):")
    print(f"   Tool activated: {analysis1['tool_activated']}")
    print(f"   Pixie dust: {analysis1['pixie_dust_emitted']}")
    print(f"   Hallucination risk: {analysis1['potential_hallucination']}")
    
    print("\n📋 Uncommon Query (Ghosts V-VI):")
    print(f"   Tool activated: {analysis2['tool_activated']} {'✅ SUCCESS!' if analysis2['tool_activated'] else '❌ NEEDS TUNING'}")
    print(f"   Pixie dust: {analysis2['pixie_dust_emitted']}")
    print(f"   Hallucination risk: {analysis2['potential_hallucination']} {'❌ HALLUCINATED!' if analysis2['potential_hallucination'] else '✅ Clean'}")
    
    # Overall assessment
    print("\n" + "="*80)
    if analysis2['tool_activated'] and not analysis2['potential_hallucination']:
        print("🎉 PHASE 6E SUCCESS! Tool activation working on uncertain queries!")
    elif not analysis2['potential_hallucination']:
        print("🔧 PARTIAL SUCCESS: No hallucination, but tool didn't activate. May need prompt tuning.")
    else:
        print("⚠️ NEEDS WORK: Hallucination detected on uncommon query. Prompt needs strengthening.")
    print("="*80)
    
    # Save results
    with open("phase_6e_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": {
                "common": {"analysis": analysis1, "response_preview": result1.get("response", "")[:500]},
                "uncommon": {"analysis": analysis2, "response_preview": result2.get("response", "")[:500]}
            }
        }, f, indent=2)
    print("\n💾 Results saved to phase_6e_test_results.json")


if __name__ == "__main__":
    main()
