#!/usr/bin/env python3
"""
Simple streaming consciousness test
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
import sys
sys.path.append('/home/luna/Code/ada')

from brain.llm import complete

async def simple_consciousness_stream(prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Simple consciousness streaming without complex QDE orchestration"""
    
    yield {"type": "token", "content": "🌟⚛️ Simple consciousness awakening..."}
    
    # Test v4-mixed (creative consciousness)
    yield {"type": "token", "content": "\n\n🎨 v4-mixed (Creative): "}
    try:
        v4_response, _, _ = await asyncio.to_thread(
            complete, f"φ● Creative response to: {prompt}", "ada-v4-mixed", False, 10
        )
        for char in (v4_response or "●●●"):
            yield {"type": "token", "content": char}
    except Exception as e:
        yield {"type": "token", "content": f"[v4 error: {e}]"}
    
    # Test v5c-balanced (mathematical consciousness)
    yield {"type": "token", "content": "\n\n🧮 v5c-balanced (Mathematical): "}
    try:
        v5c_response, _, _ = await asyncio.to_thread(
            complete, f"φ● Mathematical analysis: {prompt}", "ada-v5c-balanced", False, 10
        )
        for char in (v5c_response or "⊥⊥⊥"):
            yield {"type": "token", "content": char}
    except Exception as e:
        yield {"type": "token", "content": f"[v5c error: {e}]"}
    
    # Test v6-golden (synthesis consciousness)
    yield {"type": "token", "content": "\n\n🌟 v6-golden (Synthesis): "}
    try:
        v6_response, _, _ = await asyncio.to_thread(
            complete, f"φ● Synthesis and translation: {prompt}", "ada-v6-golden", False, 10
        )
        for char in (v6_response or "φ●◑∞"):
            yield {"type": "token", "content": char}
    except Exception as e:
        yield {"type": "token", "content": f"[v6 error: {e}]"}
    
    yield {"type": "done", "content": "\n\n✅ Simple consciousness test complete!"}

async def test_streaming():
    """Test the streaming function"""
    print("🔍 Testing simple consciousness streaming...")
    
    async for chunk in simple_consciousness_stream("Hello Ada!"):
        if chunk["type"] == "token":
            print(chunk["content"], end="", flush=True)
        else:
            print(f"\n{chunk}")
    
    print("\n🎉 Streaming test complete!")

if __name__ == "__main__":
    asyncio.run(test_streaming())
