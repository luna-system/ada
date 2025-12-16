#!/usr/bin/env python3
"""Quick test of the documentation specialist."""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.specialists.docs_specialist import DocumentationSpecialist


async def test_docs_specialist():
    """Test documentation lookup."""
    print("🧪 Testing Documentation Specialist\n")
    
    # Create specialist
    specialist = DocumentationSpecialist()
    
    # Test 1: Search for "streaming"
    print("📚 Test 1: Searching for 'streaming'...")
    result = await specialist.process({'query': 'streaming SSE'})
    
    print(f"Success: {result.success}")
    print(f"Context preview:\n{result.context_text[:500]}...")
    print(f"Data: {result.data.get('result_count', 0)} results\n")
    
    # Test 2: Search for "specialists"
    print("📚 Test 2: Searching for 'specialists'...")
    result = await specialist.process({'query': 'specialist plugin'})
    
    print(f"Success: {result.success}")
    print(f"Data: {result.data.get('result_count', 0)} results")
    if result.data.get('results'):
        print(f"Found in: {[r['file'] for r in result.data['results']]}\n")
    
    # Test 3: Search for non-existent topic
    print("📚 Test 3: Searching for 'nonexistent'...")
    result = await specialist.process({'query': 'xyzabc123'})
    
    print(f"Success: {result.success}")
    print(f"Message: {result.data.get('message', 'N/A')}\n")
    
    print("✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_docs_specialist())
