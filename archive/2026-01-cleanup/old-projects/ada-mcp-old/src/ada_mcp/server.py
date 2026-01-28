"""Ada MCP Server - Main entry point."""

import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from .ada_client import AdaClient
from .resources import RESOURCES, read_resource
from .tool_definitions import TOOLS, handle_tool_call

# Load environment variables
load_dotenv()

# Configuration
ADA_BASE_URL = os.getenv("ADA_BASE_URL", "http://localhost:8000")


async def main():
    """Run the Ada MCP server."""
    # Create Ada client
    ada = AdaClient(base_url=ADA_BASE_URL)

    # Create MCP server
    server = Server("ada-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        return await handle_tool_call(name, arguments, ada)

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available documentation resources."""
        return RESOURCES

    @server.read_resource()
    async def read_resource_handler(uri: str) -> str:
        """Read documentation resource by URI."""
        contents = await read_resource(uri)
        # Return the text content
        return contents[0].text if contents else ""

    print(f"📚 Documentation resources: {len(RESOURCES)} available", file=sys.stderr)
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
        finally:
            # Cleanup
            await ada.close()


def run():
    """Entry point for command-line execution."""
    # Print startup message to stderr so it doesn't interfere with stdio protocol
    print("🤖 Ada MCP Server starting...", file=sys.stderr)
    print(f"📡 Listening on stdio for MCP protocol messages", file=sys.stderr)
    print(f"🔗 Ada Brain: {os.getenv('ADA_BASE_URL', 'http://localhost:8000')}", file=sys.stderr)
    asyncio.run(main())


if __name__ == "__main__":
    run()
