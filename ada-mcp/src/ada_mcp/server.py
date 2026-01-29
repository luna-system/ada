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

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import subprocess
import json
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

# Import tool registration functions
from ada_mcp.tools import (
    register_swarm_tools,
    register_beads_tools,
    register_code_analysis_tools,
    register_filesystem_tools,
    register_research_tools,
)

# Initialize the FastMCP server
mcp = FastMCP("Ada MCP Server v4.0 - Modular & Clean")

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

# Register other tool categories (placeholders for now - tools still in server_old.py)
register_beads_tools(mcp, _get_path_context, _format_path_context)
register_code_analysis_tools(mcp, _get_path_context, _format_path_context)
register_filesystem_tools(mcp, _get_path_context, _format_path_context)
register_research_tools(mcp, _get_path_context, _format_path_context)


if __name__ == "__main__":
    mcp.run()
