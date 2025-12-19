#!/usr/bin/env python3
"""
Quick test to verify MCP server can start and connect to Ada brain.
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ada-mcp', 'src'))

from ada_mcp.ada_client import AdaClient

async def test_connection():
    """Test MCP client can reach Ada brain."""
    print("🧪 Testing MCP → Ada brain connection...\n")
    
    # Use same URL as VS Code config
    base_url = os.getenv("ADA_BASE_URL", "http://localhost:8000")
    client = AdaClient(base_url=base_url)
    
    print(f"🔗 Brain URL: {base_url}")
    
    try:
        # Test health check
        print("⚡ Checking brain health...")
        health = await client.health()
        
        print(f"✅ Brain: {health['ok']}")
        print(f"✅ Python: {health['python']}")
        print(f"✅ Model: {health['config']['OLLAMA_MODEL']}")
        
        # Test chat
        print("\n💬 Testing chat (non-streaming)...")
        response = await client.chat("what's 2+2?")
        print(f"✅ Response received ({len(response)} chars)")
        print(f"   Preview: {response[:100]}...")
        
        print("\n🎉 All tests passed! MCP connection ready for VS Code.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        print("\n⚠️  Make sure brain service is running:")
        print("   docker compose up -d brain")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
