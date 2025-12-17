#!/usr/bin/env python3
"""Quick test of MCP → Brain → Now Playing Specialist"""
import asyncio
import sys
sys.path.insert(0, '/home/luna/Code/ada-v1/ada-mcp/src')

from ada_mcp.ada_client import AdaClient

async def test_now_playing():
    """Test the now_playing specialist through MCP client."""
    client = AdaClient(base_url="http://localhost:8000")
    
    try:
        print("🎵 Testing Now Playing Specialist via MCP Client...\n")
        
        # Ask Ada what's playing
        response = await client.chat(
            message="What am I listening to?",
            conversation_id="mcp-test-now-playing"
        )
        
        print(f"✅ Ada's Response:\n{response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_now_playing())
