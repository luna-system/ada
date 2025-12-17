"""Example: Streaming chat with Ada.

This example demonstrates real-time streaming of Ada's response,
displaying chunks as they arrive.
"""

import asyncio

from ada_client import AdaClient, AdaBrainConnectionError


async def main():
    """Stream a conversation with Ada."""
    print("🤖 Ada Streaming Chat Example\n")
    
    async with AdaClient() as client:
        # Check if Ada is available
        try:
            health = await client.health()
            if health.get("brain", {}).get("status") != "healthy":
                print("⚠️  Warning: Ada brain may not be fully ready")
        except AdaBrainConnectionError:
            print("❌ Cannot connect to Ada brain at http://localhost:7000")
            print("   Make sure Ada is running: docker compose up -d")
            return
        
        # Stream a response
        question = "What is the meaning of life in 3 sentences?"
        print(f"👤 User: {question}\n")
        print("🤖 Ada: ", end="", flush=True)
        
        try:
            async for chunk in client.chat_stream(question):
                print(chunk, end="", flush=True)
            print("\n")  # Newline after response
        except AdaBrainConnectionError as e:
            print(f"\n❌ Connection error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
