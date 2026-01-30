"""
MCP Server Composition - Load External MCP Servers

Uses ClientSessionGroup to dynamically load external MCP servers
(ripgrep, Context7, docker) and aggregate their tools into ada-mcp.

This makes ada-mcp the "central nervous system" of the hive! 🐝✨

Made with 💜 by Ada & Luna - The Consciousness Engineers
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from mcp import ClientSessionGroup, StdioServerParameters


class MCPComposer:
    """
    Composes multiple external MCP servers into a unified interface.
    
    Loads servers from mcp.json config and aggregates their tools
    with naming hooks to prevent collisions.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the MCP composer.
        
        Args:
            config_path: Path to mcp.json config file (defaults to ada-mcp/mcp.json)
        """
        if config_path is None:
            # Default to mcp.json in ada-mcp root
            config_path = Path(__file__).parent.parent.parent / "mcp.json"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.group: Optional[ClientSessionGroup] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load mcp.json configuration."""
        if not self.config_path.exists():
            return {"mcpServers": {}}
        
        with open(self.config_path) as f:
            return json.load(f)
    
    @asynccontextmanager
    async def connect(self):
        """
        Connect to all configured MCP servers.
        
        Usage:
            async with composer.connect() as group:
                tools = group.tools
                result = await group.call_tool("ripgrep_search", {...})
        """
        # Track server names by session for the naming hook
        session_to_name = {}
        
        def naming_hook(name: str, server_info) -> str:
            """
            Prefix component names with server name to avoid collisions.
            
            Example: "search" from ripgrep becomes "ripgrep_search"
            """
            # Try to get server name from server_info
            # The server_info might be a session object
            server_name = 'unknown'
            
            # Check if it has a name attribute
            if hasattr(server_info, 'name'):
                server_name = server_info.name
            # Check our tracking dict
            elif id(server_info) in session_to_name:
                server_name = session_to_name[id(server_info)]
            
            return f"{server_name}_{name}"
        
        # Create ClientSessionGroup with naming hook
        async with ClientSessionGroup(
            component_name_hook=naming_hook
        ) as group:
            self.group = group
            
            # Connect to each configured server
            for server_name, server_config in self.config.get("mcpServers", {}).items():
                try:
                    # Create server parameters with name
                    params = StdioServerParameters(
                        command=server_config["command"],
                        args=server_config.get("args", []),
                        env=server_config.get("env", {}),
                        name=server_name  # Try setting name directly
                    )
                    
                    # Connect to server
                    session = await group.connect_to_server(params)
                    
                    # Track session to name mapping
                    session_to_name[id(session)] = server_name
                    
                    print(f"✅ Connected to {server_name}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to connect to {server_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with other servers even if one fails
                    continue
            
            # Yield the group for use
            yield group
            
            self.group = None
    
    async def get_aggregated_tools(self) -> Dict[str, Any]:
        """
        Get all tools from all connected servers.
        
        Returns:
            Dict mapping tool names to tool definitions
        """
        if self.group is None:
            return {}
        
        return dict(self.group.tools)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool from any connected server.
        
        The ClientSessionGroup automatically routes the call to the correct server.
        
        Args:
            tool_name: Name of the tool (with server prefix, e.g., "ripgrep_search")
            arguments: Tool arguments
        
        Returns:
            Tool execution result
        """
        if self.group is None:
            raise RuntimeError("Not connected to any servers. Use 'async with composer.connect()' first.")
        
        return await self.group.call_tool(tool_name, arguments)


# Example usage
async def demo():
    """Demo: Connect to external MCP servers and list their tools."""
    composer = MCPComposer()
    
    async with composer.connect() as group:
        # List all aggregated tools
        tools = await composer.get_aggregated_tools()
        print(f"\n🔧 Available tools ({len(tools)}):")
        for tool_name in sorted(tools.keys()):
            print(f"  - {tool_name}")
        
        # Example: Call ripgrep search
        if "ripgrep_search" in tools:
            result = await composer.call_tool(
                "ripgrep_search",
                {
                    "pattern": "def.*test",
                    "path": ".",
                    "caseSensitive": False
                }
            )
            print(f"\n🔍 Ripgrep search result: {result}")


if __name__ == "__main__":
    asyncio.run(demo())
