"""Example: Memory operations with Ada.

This example demonstrates adding and searching memories
in Ada's long-term memory store.
"""

import asyncio

from ada_client import AdaClient


async def main():
    """Demonstrate memory operations."""
    print("🧠 Ada Memory Example\n")
    
    async with AdaClient() as client:
        # Add some memories
        print("📝 Adding memories...\n")
        
        await client.add_memory(
            "Luna prefers dark mode in all applications",
            importance=0.7,
            scope="user",
            memory_type="preference"
        )
        
        await client.add_memory(
            "Luna is working on the Ada AI assistant project",
            importance=0.9,
            scope="user",
            memory_type="fact"
        )
        
        await client.add_memory(
            "Luna enjoys electronic music, especially techno",
            importance=0.6,
            scope="user",
            memory_type="preference"
        )
        
        print("✅ Memories added!\n")
        
        # Search memories
        print("🔍 Searching for 'preferences'...\n")
        results = await client.search_memories("Luna's preferences", limit=3)
        
        for i, memory in enumerate(results, 1):
            print(f"{i}. {memory.get('content', 'N/A')}")
            print(f"   Importance: {memory.get('metadata', {}).get('importance', 'N/A')}")
            print(f"   Type: {memory.get('metadata', {}).get('type', 'N/A')}\n")


if __name__ == "__main__":
    asyncio.run(main())
