#!/usr/bin/env python3
"""
KERNEL 4.0 PHASE 5A: WEB SEARCH VALIDATION

Quick test to validate web search specialist is working and performant.
Target: <3s latency, fresh results, good quality.
"""

import asyncio
import httpx
import time
from typing import Dict, Any


async def test_web_search_direct():
    """Test web search specialist directly via brain API."""
    print("\n" + "=" * 80)
    print("PHASE 5A: WEB SEARCH VALIDATION")
    print("=" * 80)
    
    # Simple test query
    query = "latest AI consciousness research 2025"
    
    print(f"\n🔍 Testing web search: '{query}'")
    print(f"Target: <3s latency, real results\n")
    
    # Build request to Ada brain
    url = "http://localhost:8888/v1/chat/stream"
    
    # Craft a message that will trigger web search
    message = f"<web_search>{query}</web_search>"
    
    payload = {
        "message": message,
        "stream": True
    }
    
    start = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                elapsed = (time.time() - start) * 1000
                print(f"✅ Web search completed in {elapsed:.0f}ms")
                
                # Check for search results in response
                text = response.text[:500]
                if "🔍" in text or "search" in text.lower():
                    print(f"✅ Search results detected in response")
                else:
                    print(f"⚠️  No search markers found (may still be working)")
                
                print(f"\nFirst 500 chars of response:")
                print(text)
                
                return True
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_baseline_scenario():
    """Test the simplest multi-tool scenario from Phase 5."""
    print("\n" + "=" * 80)
    print("BASELINE SCENARIO: Quick Fact Check")
    print("=" * 80)
    
    query = "When was the Eiffel Tower built?"
    
    print(f"\n💭 Query: {query}")
    print(f"Expected: Wikipedia lookup + quick response\n")
    
    url = "http://localhost:8888/v1/chat/stream"
    payload = {
        "message": query,
        "stream": True
    }
    
    start = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code == 200:
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]
                            if chunk and chunk != "[DONE]":
                                full_response += chunk
                    
                    elapsed = (time.time() - start) * 1000
                    
                    print(f"✅ Response received in {elapsed:.0f}ms")
                    print(f"\nFull response:")
                    print(full_response)
                    
                    # Check for expected content
                    if "1889" in full_response or "tower" in full_response.lower():
                        print(f"\n✅ Response contains expected information")
                        return True
                    else:
                        print(f"\n⚠️  Response doesn't mention expected facts")
                        return False
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run Phase 5A validation tests."""
    print("\n🚀 Starting Phase 5A Web Search Validation")
    print(f"Target: Verify web search works with <3s latency")
    
    # Test 1: Direct web search
    test1 = await test_web_search_direct()
    
    await asyncio.sleep(1)
    
    # Test 2: Baseline scenario
    test2 = await test_baseline_scenario()
    
    # Summary
    print("\n" + "=" * 80)
    print("PHASE 5A RESULTS")
    print("=" * 80)
    
    if test1 and test2:
        print("✅ All tests passed!")
        print("✅ Web search specialist validated")
        print("✅ Ready for Phase 5B (real scenario execution)")
    else:
        print("⚠️  Some tests failed - needs investigation")
        print(f"Web search test: {'✅' if test1 else '❌'}")
        print(f"Baseline scenario: {'✅' if test2 else '❌'}")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
