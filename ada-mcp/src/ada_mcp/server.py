"""Ada MCP Server - Main entry point."""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .ada_client import AdaClient
from .tools import TOOLS, handle_tool_call

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

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

    # Cleanup
    await ada.close()


def run():
    """Entry point for command-line execution."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
