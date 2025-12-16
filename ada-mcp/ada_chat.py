#!/usr/bin/env -S uv run --directory /home/luna/Code/ada-v1/ada-mcp
"""Simple CLI to chat with Ada via MCP."""

import asyncio
import sys
from ada_mcp.ada_client import AdaClient
from ada_mcp.tools import handle_tool_call


async def main():
    if len(sys.argv) < 2:
        print("Usage: ada-chat <your message>")
        print("\nExamples:")
        print("  ada-chat 'Write a Python hello world script'")
        print("  ada-chat 'What is the meaning of life?'")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    
    print(f"🤖 Asking Ada: {message}\n")
    
    client = AdaClient("http://localhost:8000")
    
    try:
        result = await handle_tool_call(
            "ada_chat",
            {"message": message},
            client
        )
        print("💬 Ada says:")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
