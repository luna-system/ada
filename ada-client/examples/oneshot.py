"""Example: Non-streaming (one-shot) chat with Ada.

This example demonstrates getting a complete response from Ada
in one operation, useful for scripts and batch processing.
"""

import asyncio

from ada_client import AdaClient, AdaBrainError


async def main():
    """Ask Ada a question and get complete response."""
    print("🤖 Ada One-Shot Chat Example\n")
    
    client = AdaClient()
    
    try:
        # Quick health check
        health = await client.health()
        print(f"✅ Brain status: {health['brain']['status']}\n")
        
        # Ask a question
        question = "Explain async/await in Python in 2 sentences."
        print(f"👤 Question: {question}\n")
        
        response = await client.chat(question)
        print(f"🤖 Answer: {response}\n")
        
    except AdaBrainError as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
