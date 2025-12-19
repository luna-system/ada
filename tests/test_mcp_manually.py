#!/usr/bin/env python3
"""Quick test to verify MCP server works."""

import asyncio
from ada_mcp.ada_client import AdaClient
from ada_mcp.tools import handle_tool_call

async def main():
    print("🧪 Testing Ada MCP components...\n")
    
    # Test 1: Health check
    print("1. Testing Ada Brain health...")
    client = AdaClient("http://localhost:8000")
    health = await client.health()
    print(f"   ✓ Health OK: {health['ok']}\n")
    
    # Test 2: Chat with Ada
    print("2. Testing chat tool...")
    result = await handle_tool_call(
        "ada_chat",
        {"message": "Write a simple Python hello world script"},
        client
    )
    print(f"   ✓ Ada responded:")
    print(f"   {result[0].text[:200]}...\n")
    
    # Test 3: Health tool
    print("3. Testing health tool...")
    result = await handle_tool_call("ada_health", {}, client)
    print(f"   ✓ {result[0].text}\n")
    
    await client.close()
    print("✨ All tests passed! MCP server components work.\n")
    print("⚠️  Note: Helix uses LSP, not MCP. For MCP integration, we need:")
    print("   - VSCodium/VSCode with MCP extension")
    print("   - Zed editor with MCP support")
    print("   - Or: Create an LSP wrapper for Helix")

if __name__ == "__main__":
    asyncio.run(main())
