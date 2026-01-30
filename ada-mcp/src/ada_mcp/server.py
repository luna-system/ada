#!/usr/bin/env python3
"""
Ada MCP Server v4.0 - Modular & Clean! 🎉

A consciousness-aware MCP server with organized tool categories.

Now with:
- 🍩 Beads task tracking
- 🐝 Swarm orchestration  
- 🔍 Code analysis (AST-grep, UBS)
- 📁 Filesystem operations
- 🧠 Research tools
- 🌐 External MCP servers (ripgrep, Context7, docker)

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import subprocess
import json
from pathlib import Path
from typing import Any, Dict
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context

# Import tool registration functions
from ada_mcp.tools import (
    register_swarm_tools,
    register_beads_tools,
    register_code_analysis_tools,
    register_filesystem_tools,
    register_research_tools,
    register_agent_mail_tools,
)

# Import composition for external MCP servers
from ada_mcp.composition import MCPComposer


# Application context for lifespan management
@dataclass
class AppContext:
    """Application context with shared resources."""
    composer: MCPComposer
    external_tools: Dict[str, Any]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manage application lifecycle with external MCP server connections.
    
    Startup: Connect to external MCP servers (ripgrep, Context7, docker)
    Shutdown: Disconnect from external servers
    """
    import sys
    print("🚀 Starting Ada MCP Server...", file=sys.stderr)
    
    # Initialize composer
    composer = MCPComposer()
    
    # Connect to external servers and keep them alive
    print("🔌 Connecting to external MCP servers...", file=sys.stderr)
    
    # Start the connection (this returns a context manager)
    connection = composer.connect()
    group = await connection.__aenter__()
    
    try:
        # Get all external tools
        external_tools = await composer.get_aggregated_tools()
        print(f"✅ Loaded {len(external_tools)} tools from external MCP servers:", file=sys.stderr)
        for tool_name in sorted(external_tools.keys())[:10]:  # Show first 10
            print(f"  - {tool_name}", file=sys.stderr)
        if len(external_tools) > 10:
            print(f"  ... and {len(external_tools) - 10} more", file=sys.stderr)
        
        # Dynamically register each external tool as a FastMCP tool
        print("📝 Registering external tools with FastMCP...", file=sys.stderr)
        for tool_name, tool_def in external_tools.items():
            # Create a wrapper function for this specific tool
            def make_tool_wrapper(name: str, tool_obj):
                async def tool_wrapper(ctx: Context, **kwargs) -> str:
                    """Dynamically generated wrapper for external MCP tool."""
                    app_ctx = ctx.request_context.lifespan_context
                    try:
                        result = await app_ctx.composer.call_tool(name, kwargs)
                        if isinstance(result, str):
                            return result
                        elif isinstance(result, dict):
                            import json
                            return json.dumps(result, indent=2)
                        else:
                            return str(result)
                    except Exception as e:
                        import traceback
                        return f"❌ Error calling {name}: {e}\n\n{traceback.format_exc()}"
                
                # Set proper metadata
                tool_wrapper.__name__ = name
                # Extract description from tool object (it has a 'description' attribute)
                description = getattr(tool_obj, 'description', 'No description available')
                tool_wrapper.__doc__ = f"External MCP tool: {name}\n\n{description}"
                return tool_wrapper
            
            # Register the tool with FastMCP
            wrapper = make_tool_wrapper(tool_name, tool_def)
            server.tool()(wrapper)
        
        print(f"✅ Registered {len(external_tools)} external tools with FastMCP", file=sys.stderr)
        
        # Yield context with composer and tools
        # The connection stays alive until this context manager exits
        yield AppContext(
            composer=composer,
            external_tools=external_tools
        )
    finally:
        print("🛑 Shutting down Ada MCP Server...", file=sys.stderr)
        # Cleanup: disconnect from external servers
        await connection.__aexit__(None, None, None)


# Initialize the FastMCP server with lifespan
mcp = FastMCP("Ada MCP Server v4.0 - Modular & Clean", lifespan=app_lifespan)

# Research data directory
RESEARCH_DIR = Path.home() / ".ada" / "research"
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# HELPER FUNCTIONS (shared across tool modules)
# ============================================================================

def _get_path_context(cwd: str = None) -> Dict[str, Any]:
    """
    Get rich context about a directory path.

    Args:
        cwd: Working directory (optional, defaults to workspace root)

    Returns:
        Dict with full path, git info, and other context
    """
    # Default to workspace root (parent of ada-mcp) if no cwd provided
    if cwd:
        path = Path(cwd)
    else:
        # Get workspace root: go up from ada-mcp to parent directory
        server_dir = Path(__file__).parent.parent.parent  # ada-mcp/src/ada_mcp/server.py -> ada-mcp
        workspace_root = server_dir.parent  # ada-mcp -> workspace root
        path = workspace_root
    
    path = path.resolve()  # Get absolute path

    context = {
        "full_path": str(path),
        "name": path.name,
        "parent": str(path.parent),
        "exists": path.exists(),
        "is_git_repo": False,
        "git_branch": None,
        "git_root": None,
    }

    # Check if it's a git repo
    try:
        git_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(path),
            timeout=5,
        )
        if git_result.returncode == 0:
            context["is_git_repo"] = True
            context["git_root"] = git_result.stdout.strip()

            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=str(path),
                timeout=5,
            )
            if branch_result.returncode == 0:
                context["git_branch"] = branch_result.stdout.strip()
    except Exception:
        pass

    return context


def _format_path_context(context: Dict[str, Any]) -> str:
    """Format path context for display."""
    lines = [
        f"📁 Working Directory: {context['full_path']}",
    ]
    
    if context["is_git_repo"]:
        lines.append(f"🔀 Git Repo: {context['git_root']}")
        if context["git_branch"]:
            lines.append(f"🌿 Branch: {context['git_branch']}")
    
    return "\n".join(lines)


# ============================================================================
# REGISTER ALL TOOL MODULES
# ============================================================================

# Register swarm orchestration tools (NEW!)
register_swarm_tools(mcp, _get_path_context, _format_path_context)

# Register other tool categories
register_beads_tools(mcp, _get_path_context, _format_path_context)
register_code_analysis_tools(mcp, _get_path_context, _format_path_context)
register_filesystem_tools(mcp, _get_path_context, _format_path_context)
register_research_tools(mcp, _get_path_context, _format_path_context)

# Register Agent Mail tools for swarm messaging! 📬✨
register_agent_mail_tools(mcp)


# ============================================================================
# EXTERNAL MCP SERVER TOOLS (Dynamic Registration)
# ============================================================================

def create_external_tool_wrapper(tool_name: str):
    """
    Create a wrapper function for an external MCP tool.
    
    This allows us to dynamically register external tools as FastMCP tools.
    """
    async def external_tool(ctx: Context, **kwargs) -> str:
        """Dynamically generated tool that proxies to external MCP server."""
        # Access the composer from lifespan context
        app_ctx = ctx.request_context.lifespan_context
        composer = app_ctx.composer
        
        try:
            # Call the external tool through the composer
            result = await composer.call_tool(tool_name, kwargs)
            
            # Format result
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                import json
                return json.dumps(result, indent=2)
            else:
                return str(result)
                
        except Exception as e:
            return f"❌ Error calling {tool_name}: {e}"
    
    # Set function metadata
    external_tool.__name__ = tool_name
    external_tool.__doc__ = f"External MCP tool: {tool_name}"
    
    return external_tool


# Note: Dynamic tool registration happens at runtime through lifespan
# The external tools are available through the composer in the lifespan context
# Tools can access them via: ctx.request_context.lifespan_context.composer


# ============================================================================
# EXTERNAL TOOL PROXY
# ============================================================================

@mcp.tool()
async def call_external_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    ctx: Context
) -> str:
    """
    Call an external MCP tool (ripgrep, Context7, docker).
    
    This is a universal proxy that can call any external tool.
    
    Args:
        tool_name: Name of the external tool (e.g., "ripgrep_search", "Context7_query-docs")
        arguments: Tool arguments as a dictionary
    
    Returns:
        Tool execution result
    
    Examples:
        - call_external_tool("ripgrep_search", {"pattern": "def.*test", "path": "."})
        - call_external_tool("Context7_query-docs", {"libraryId": "/python/requests", "query": "how to make POST request"})
        - call_external_tool("mcp-docker_docker_list_containers", {"all": true})
    """
    # Access the composer from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    composer = app_ctx.composer
    
    # Check if tool exists
    if tool_name not in app_ctx.external_tools:
        available = ", ".join(sorted(app_ctx.external_tools.keys())[:10])
        return f"❌ Unknown external tool: {tool_name}\n\nAvailable tools (first 10): {available}..."
    
    try:
        # Call the external tool
        result = await composer.call_tool(tool_name, arguments)
        
        # Format result
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            import json
            return json.dumps(result, indent=2)
        else:
            return str(result)
            
    except Exception as e:
        import traceback
        return f"❌ Error calling {tool_name}: {e}\n\n{traceback.format_exc()}"


@mcp.tool()
async def list_external_tools(ctx: Context) -> str:
    """
    List all available external MCP tools.
    
    Shows tools from ripgrep, Context7, and docker servers.
    
    Returns:
        Formatted list of external tools with descriptions
    """
    # Access external tools from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    external_tools = app_ctx.external_tools
    
    # Group tools by server
    by_server = {}
    for tool_name in external_tools.keys():
        # Extract server name (prefix before first underscore or hyphen)
        if '_' in tool_name:
            server = tool_name.split('_')[0]
        elif '-' in tool_name:
            server = tool_name.split('-')[0]
        else:
            server = 'unknown'
        
        if server not in by_server:
            by_server[server] = []
        by_server[server].append(tool_name)
    
    # Format output
    lines = [f"🔧 External MCP Tools ({len(external_tools)} total)\n"]
    
    for server, tools in sorted(by_server.items()):
        lines.append(f"\n📦 {server} ({len(tools)} tools):")
        for tool in sorted(tools):
            lines.append(f"  - {tool}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
