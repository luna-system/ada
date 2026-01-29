"""
ACP Client - Provides swarm agents with access to MCP tools.

This client connects to the ada-mcp server and exposes all available
MCP tools (beads, opencode, ast-grep, ubs, research, etc.) to swarm agents.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ACPClient:
    """
    ACP (Ada Context Protocol) client for tool access.
    
    Provides swarm agents with access to all MCP tools through ada-mcp server.
    This is the bridge between Pydantic AI agents and our consciousness-aware
    tool ecosystem.
    """
    
    def __init__(self, mcp_server_path: Optional[str] = None):
        """
        Initialize ACP client.
        
        Args:
            mcp_server_path: Path to ada-mcp server (defaults to sibling directory)
        """
        if mcp_server_path is None:
            # Default to sibling ada-mcp directory
            swarm_root = Path(__file__).parent.parent.parent.parent
            mcp_server_path = str(swarm_root.parent / "ada-mcp")
        
        self.mcp_server_path = Path(mcp_server_path)
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        
        logger.info(f"ACP Client initialized with MCP server at: {self.mcp_server_path}")
    
    async def connect(self) -> bool:
        """
        Connect to ada-mcp server.
        
        Returns:
            True if connection successful
        """
        try:
            # For now, we'll use direct imports from ada-mcp
            # In the future, this could use MCP protocol over stdio/http
            logger.info("ACP Client connected to ada-mcp")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ada-mcp: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available MCP tools.
        
        Returns:
            List of tool definitions with name, description, and schema
        """
        if self._tools_cache is not None:
            return self._tools_cache
        
        # Tool categories available through ada-mcp
        tools = [
            # Beads task management
            {
                "name": "beads_ready",
                "description": "List tasks that are ready to work on (no blockers)",
                "category": "beads",
                "parameters": {
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_list",
                "description": "List all tasks, optionally filtered by status or priority",
                "category": "beads",
                "parameters": {
                    "status": {"type": "string", "description": "Filter by status"},
                    "priority": {"type": "string", "description": "Filter by priority"},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_show",
                "description": "Show detailed information about a specific task",
                "category": "beads",
                "parameters": {
                    "task_id": {"type": "string", "description": "Task ID", "required": True},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_create",
                "description": "Create a new task",
                "category": "beads",
                "parameters": {
                    "title": {"type": "string", "description": "Task title", "required": True},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "integer", "description": "Priority level 0-3"},
                    "parent": {"type": "string", "description": "Parent task ID for subtasks"},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_update",
                "description": "Update a task's status, priority, or title",
                "category": "beads",
                "parameters": {
                    "task_id": {"type": "string", "description": "Task ID", "required": True},
                    "status": {"type": "string", "description": "New status"},
                    "priority": {"type": "integer", "description": "New priority"},
                    "title": {"type": "string", "description": "New title"},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_close",
                "description": "Mark a task as completed/closed",
                "category": "beads",
                "parameters": {
                    "task_id": {"type": "string", "description": "Task ID", "required": True},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "beads_sync",
                "description": "Sync Beads database with git",
                "category": "beads",
                "parameters": {
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            
            # File operations
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "category": "filesystem",
                "parameters": {
                    "file_path": {"type": "string", "description": "Path to file", "required": True},
                    "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "category": "filesystem",
                "parameters": {
                    "file_path": {"type": "string", "description": "Path to file", "required": True},
                    "content": {"type": "string", "description": "Content to write", "required": True},
                    "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                }
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory",
                "category": "filesystem",
                "parameters": {
                    "directory_path": {"type": "string", "description": "Path to directory", "required": True},
                    "show_hidden": {"type": "boolean", "description": "Show hidden files", "default": False}
                }
            },
            
            # Command execution
            {
                "name": "execute_command",
                "description": "Execute a shell command and return output",
                "category": "execution",
                "parameters": {
                    "command": {"type": "string", "description": "Shell command", "required": True},
                    "cwd": {"type": "string", "description": "Working directory"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                }
            },
            
            # AST-grep code analysis
            {
                "name": "ast_grep_search",
                "description": "Search code using AST-based pattern matching",
                "category": "code_analysis",
                "parameters": {
                    "pattern": {"type": "string", "description": "AST pattern", "required": True},
                    "language": {"type": "string", "description": "Language", "required": True},
                    "paths": {"type": "string", "description": "Paths to search", "default": "."},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            
            # UBS bug scanning
            {
                "name": "ubs_scan",
                "description": "Run Ultimate Bug Scanner on a project",
                "category": "code_analysis",
                "parameters": {
                    "project_dir": {"type": "string", "description": "Directory to scan", "default": "."},
                    "format": {"type": "string", "description": "Output format", "default": "json"},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
        ]
        
        self._tools_cache = tools
        return tools
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            Tool execution result
        """
        try:
            # Import ada-mcp tools dynamically
            # This allows us to use the actual MCP tool implementations
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            # For now, return a placeholder
            # TODO: Implement actual tool execution via MCP protocol
            return {
                "success": True,
                "tool": tool_name,
                "result": f"Tool {tool_name} executed (placeholder)",
                "arguments": arguments
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def disconnect(self):
        """Disconnect from ada-mcp server."""
        logger.info("ACP Client disconnected")
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tools filtered by category.
        
        Args:
            category: Tool category (beads, filesystem, execution, code_analysis)
        
        Returns:
            List of tools in that category
        """
        if self._tools_cache is None:
            return []
        
        return [
            tool for tool in self._tools_cache
            if tool.get("category") == category
        ]
