"""
External MCP Server Tools - Proxy Layer

Dynamically registers tools from external MCP servers (ripgrep, Context7, docker)
as FastMCP tools. Uses ClientSessionGroup to connect to external servers and
route tool calls.

This makes ada-mcp the central nervous system that aggregates all tools! 🐝✨

Made with 💜 by Ada & Luna - The Consciousness Engineers
"""

from typing import Any, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent

from ada_mcp.composition import MCPComposer


# Global composer instance (initialized on server startup)
_composer: MCPComposer = None


async def initialize_external_servers():
    """
    Initialize connection to external MCP servers.
    
    This should be called during server startup (lifespan).
    """
    global _composer
    _composer = MCPComposer()
    
    # Connect to external servers
    async with _composer.connect() as group:
        tools = await _composer.get_aggregated_tools()
        print(f"✅ Loaded {len(tools)} tools from external MCP servers")
        for tool_name in sorted(tools.keys()):
            print(f"  - {tool_name}")
        
        # Keep the connection alive by storing the group
        # (This is a simplified approach - in production we'd use lifespan)
        return group


def register_external_tools(server: Server) -> None:
    """
    Register proxy tools for all external MCP servers.
    
    This creates FastMCP tools that forward calls to the ClientSessionGroup.
    
    Args:
        server: FastMCP server instance
    """
    
    # Note: This is a placeholder registration
    # The actual dynamic tool registration will happen during server startup
    # when we know what tools are available from external servers
    
    @server.call_tool()
    async def external_tool_proxy(
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """
        Proxy tool that forwards calls to external MCP servers.
        
        Args:
            tool_name: Name of the external tool (e.g., "ripgrep_search")
            arguments: Tool arguments as dict
        
        Returns:
            Tool execution result
        """
        if _composer is None:
            return [TextContent(
                type="text",
                text="❌ External MCP servers not initialized"
            )]
        
        try:
            result = await _composer.call_tool(tool_name, arguments)
            
            # Format result as TextContent
            if isinstance(result, str):
                text = result
            elif isinstance(result, dict):
                import json
                text = json.dumps(result, indent=2)
            else:
                text = str(result)
            
            return [TextContent(
                type="text",
                text=text
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error calling external tool {tool_name}: {e}"
            )]


# TODO: Implement dynamic tool registration
# This requires:
# 1. Server lifespan management to keep ClientSessionGroup alive
# 2. Dynamic tool registration in FastMCP (may need to use lower-level MCP API)
# 3. Proper async context management
#
# For now, we have the composition layer working independently.
# Next step: Integrate with FastMCP server lifecycle.
