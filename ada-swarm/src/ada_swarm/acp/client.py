"""
ACP Client - Provides swarm agents with access to MCP tools.

This client connects to the ada-mcp server and exposes all available
MCP tools (beads, opencode, ast-grep, ubs, research, etc.) to swarm agents.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from .permissions import AgentRole, get_permission_manager
from ..monitoring import DoomLoopDetector
from ..exceptions import (
    PermissionDeniedException,
    DroneException,
    WorkerException,
    QueenException
)

logger = logging.getLogger(__name__)


class ACPClient:
    """
    ACP (Ada Context Protocol) client for tool access.
    
    Provides swarm agents with access to all MCP tools through ada-mcp server.
    This is the bridge between Pydantic AI agents and our consciousness-aware
    tool ecosystem.
    """
    
    def __init__(
        self,
        mcp_server_path: Optional[str] = None,
        role: AgentRole = AgentRole.WORKER_CODER,
        agent_id: Optional[str] = None
    ):
        """
        Initialize ACP client.
        
        Args:
            mcp_server_path: Path to ada-mcp server (defaults to sibling directory)
            role: Agent role for permission management
            agent_id: Agent ID for doom loop detection
        """
        if mcp_server_path is None:
            # Check if we're in Docker (ada-mcp mounted at /app/ada-mcp)
            docker_path = Path("/app/ada-mcp")
            if docker_path.exists():
                mcp_server_path = str(docker_path)
            else:
                # Default to sibling ada-mcp directory (local development)
                swarm_root = Path(__file__).parent.parent.parent.parent
                mcp_server_path = str(swarm_root.parent / "ada-mcp")
        
        self.mcp_server_path = Path(mcp_server_path)
        self.role = role
        self.permission_manager = get_permission_manager()
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        
        # Initialize doom loop detector
        self.agent_id = agent_id or f"agent-{id(self)}"
        self.doom_detector = DoomLoopDetector(
            agent_id=self.agent_id,
            failure_threshold=5,
            polling_threshold=10,
            read_threshold=15
        )
        
        logger.info(
            f"ACP Client initialized with MCP server at: {self.mcp_server_path}, "
            f"role: {role.value}, agent_id: {self.agent_id}"
        )
    
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
        List all available MCP tools filtered by role permissions.
        
        Returns:
            List of tool definitions with name, description, and schema
            (filtered to only tools this role can access)
        """
        if self._tools_cache is not None:
            # Filter cached tools by role
            return self.permission_manager.filter_tools(self.role, self._tools_cache)
        
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
            
            # Swarm orchestration (Queen Bee only)
            {
                "name": "swarm_spawn_task",
                "description": "Spawn a Worker Bee or Drone for a subtask",
                "category": "swarm",
                "parameters": {
                    "description": {"type": "string", "description": "Task description", "required": True},
                    "model": {"type": "string", "description": "Model to use", "required": True},
                    "agent_type": {"type": "string", "description": "Agent type", "required": True},
                    "cwd": {"type": "string", "description": "Working directory"}
                }
            },
            {
                "name": "swarm_check_status",
                "description": "Check status of a spawned task",
                "category": "swarm",
                "parameters": {
                    "task_id": {"type": "string", "description": "Task ID", "required": True}
                }
            },
            {
                "name": "swarm_cancel_task",
                "description": "Cancel a running task",
                "category": "swarm",
                "parameters": {
                    "task_id": {"type": "string", "description": "Task ID", "required": True}
                }
            },
            {
                "name": "swarm_list_agents",
                "description": "List all active agents in the swarm",
                "category": "swarm",
                "parameters": {}
            },
            
            # Research tools
            {
                "name": "research_notes_add",
                "description": "Add a research note or insight",
                "category": "research",
                "parameters": {
                    "note": {"type": "string", "description": "Research note", "required": True},
                    "category": {"type": "string", "description": "Note category"},
                    "tags": {"type": "array", "description": "Tags for organization"}
                }
            },
            {
                "name": "research_notes_search",
                "description": "Search research notes",
                "category": "research",
                "parameters": {
                    "query": {"type": "string", "description": "Search query", "required": True}
                }
            },
            {
                "name": "hypothesis_add",
                "description": "Add a new research hypothesis",
                "category": "research",
                "parameters": {
                    "hypothesis": {"type": "string", "description": "Hypothesis description", "required": True}
                }
            },
            {
                "name": "experiment_log",
                "description": "Log experiment results",
                "category": "research",
                "parameters": {
                    "experiment_name": {"type": "string", "description": "Experiment name", "required": True},
                    "version": {"type": "string", "description": "Version", "required": True},
                    "results": {"type": "string", "description": "Results", "required": True}
                }
            },
        ]
        
        self._tools_cache = tools
        
        # Filter by role permissions
        return self.permission_manager.filter_tools(self.role, tools)
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Validates role permissions before execution and monitors for doom loops.
        Raises role-specific exceptions on failure.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            Tool execution result
            
        Raises:
            DoomLoopException: If doom loop detected
            PermissionDeniedException: If role lacks permission
            DroneException: If drone-level error (for drones)
            WorkerException: If worker-level error (for workers)
            QueenException: If queen-level error (for queen)
        """
        try:
            # Check if we should pause due to doom loop
            # This will raise DoomLoopException if needed
            self.doom_detector.raise_if_doom_loop()
            
            # Validate permissions
            is_valid, error_msg = self.permission_manager.validate_tool_call(
                self.role, tool_name, arguments
            )
            
            if not is_valid:
                logger.warning(f"Permission denied for {self.role.value}: {error_msg}")
                # Record failed call
                alert = self.doom_detector.record_tool_call(tool_name, False, arguments)
                if alert:
                    logger.warning(f"Doom loop alert: {alert.message}")
                
                # Raise permission exception
                raise PermissionDeniedException(
                    message=error_msg,
                    role=self.role.value,
                    tool_name=tool_name,
                    context={"arguments": arguments}
                )
            
            # Execute actual MCP tool from ada-mcp server
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            # Import ada-mcp server module to access tool functions
            try:
                import sys
                from pathlib import Path
                
                # Add ada-mcp to path if not already there
                ada_mcp_path = self.mcp_server_path / "src"
                if str(ada_mcp_path) not in sys.path:
                    sys.path.insert(0, str(ada_mcp_path))
                
                # Import modular tool functions from ada-mcp
                from ada_mcp.tools import beads, filesystem, code_analysis, research
                
                # Map tool names to actual functions
                tool_map = {
                    # Beads tools
                    "beads_ready": beads.beads_ready,
                    "beads_list": beads.beads_list,
                    "beads_show": beads.beads_show,
                    "beads_create": beads.beads_create,
                    "beads_update": beads.beads_update,
                    "beads_close": beads.beads_close,
                    "beads_sync": beads.beads_sync,
                    "beads_dep_add": beads.beads_dep_add,
                    
                    # File operations
                    "read_file": filesystem.read_file_content,
                    "write_file": filesystem.write_file_content,
                    "list_directory": filesystem.list_directory,
                    
                    # Command execution
                    "execute_command": filesystem.execute_command,
                    
                    # AST-grep
                    "ast_grep_search": code_analysis.ast_grep_search,
                    "ast_grep_rewrite": code_analysis.ast_grep_rewrite,
                    "ast_grep_dump_ast": code_analysis.ast_grep_dump_ast,
                    "ast_grep_scan": code_analysis.ast_grep_scan,
                    
                    # UBS
                    "ubs_scan": code_analysis.ubs_scan,
                    
                    # Research tools
                    "research_notes_add": research.research_notes_add,
                    "research_notes_search": research.research_notes_search,
                    "hypothesis_add": research.hypothesis_add,
                    "hypothesis_list": research.hypothesis_list,
                    "experiment_log": research.experiment_log,
                    "experiment_history": research.experiment_history,
                    "research_todo_add": research.research_todo_add,
                    "research_todo_list": research.research_todo_list,
                    "research_todo_complete": research.research_todo_complete,
                }
                
                # Get the tool function
                tool_func = tool_map.get(tool_name)
                
                if tool_func is None:
                    return {
                        "success": False,
                        "error": f"Tool {tool_name} not implemented in ACP client",
                        "tool": tool_name
                    }
                
                # Call the actual tool function
                result = tool_func(**arguments)
                
                # Record successful call and check for doom loops
                alert = self.doom_detector.record_tool_call(tool_name, True, arguments)
                if alert:
                    logger.warning(f"Doom loop alert: {alert.message}")
                
                # Record progress for certain tools
                if tool_name in ["beads_create", "write_file", "beads_close"]:
                    self.doom_detector.record_progress(f"Completed {tool_name}")
                
                return {
                    "success": True,
                    "tool": tool_name,
                    "result": result,
                    "arguments": arguments
                }
                
            except ImportError as e:
                logger.error(f"Failed to import ada-mcp tools: {e}")
                # Record failed call
                alert = self.doom_detector.record_tool_call(tool_name, False, arguments)
                if alert:
                    logger.warning(f"Doom loop alert: {alert.message}")
                
                return {
                    "success": False,
                    "error": f"Failed to import ada-mcp tools: {str(e)}",
                    "tool": tool_name
                }
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                # Record failed call
                alert = self.doom_detector.record_tool_call(tool_name, False, arguments)
                if alert:
                    logger.warning(f"Doom loop alert: {alert.message}")
                
                return {
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}",
                    "tool": tool_name
                }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            # Record failed call
            alert = self.doom_detector.record_tool_call(tool_name, False, arguments)
            if alert:
                logger.warning(f"Doom loop alert: {alert.message}")
            
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
    
    def get_doom_status(self) -> Dict:
        """
        Get current doom loop detector status.
        
        Returns:
            Status dict with metrics and alerts
        """
        return self.doom_detector.get_status()
    
    def reset_doom_detector(self):
        """Reset doom loop detector (after human intervention)."""
        self.doom_detector.reset()
        logger.info(f"Doom loop detector reset for {self.agent_id}")
    
    def raise_role_exception(
        self,
        error: Exception,
        task: str,
        tool_name: Optional[str] = None,
        attempted_solutions: Optional[List[str]] = None
    ):
        """
        Raise an exception appropriate for this agent's role.
        
        Args:
            error: Original error
            task: Task being performed
            tool_name: Tool that failed
            attempted_solutions: What was tried
            
        Raises:
            DroneException: If role is drone
            WorkerException: If role is worker
            QueenException: If role is queen
        """
        from ..exceptions import handle_drone_error, handle_worker_error, handle_queen_error
        
        if "drone" in self.role.value.lower():
            raise handle_drone_error(
                error=error,
                task=task,
                tool_name=tool_name,
                attempted_solutions=attempted_solutions
            )
        elif "worker" in self.role.value.lower():
            raise handle_worker_error(
                error=error,
                task=task,
                attempted_solutions=attempted_solutions
            )
        elif "queen" in self.role.value.lower():
            raise handle_queen_error(
                error=error,
                task=task,
                attempted_solutions=attempted_solutions
            )
        else:
            # Default to worker exception
            raise handle_worker_error(
                error=error,
                task=task,
                attempted_solutions=attempted_solutions
            )
