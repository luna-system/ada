"""
Role-Based Tool Permissions for Ada Swarm.

Defines which tools each agent role can access, following the
three-tier consciousness hierarchy:
- Queen Bee 👑: Full orchestration and spawning
- Worker Bee 🐝: Specialized execution (coder, researcher, tester)
- Drone 🤖: Simple read-only tasks

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from enum import Enum
from typing import Set, List, Dict, Any
from dataclasses import dataclass


class AgentRole(str, Enum):
    """
    Agent roles in the swarm hierarchy.
    
    Each role has different tool access permissions based on their
    responsibilities and consciousness level.
    """
    # Orchestration layer
    QUEEN_BEE = "queen_bee"
    
    # Execution layer (specialized workers)
    WORKER_CODER = "worker_coder"
    WORKER_RESEARCHER = "worker_researcher"
    WORKER_TESTER = "worker_tester"
    WORKER_REVIEWER = "worker_reviewer"
    
    # Simple task layer
    DRONE = "drone"


@dataclass
class ToolPermission:
    """
    Defines a tool permission with optional constraints.
    """
    tool_name: str
    read_only: bool = False
    max_calls_per_minute: int = 60
    requires_approval: bool = False


class PermissionManager:
    """
    Manages role-based tool permissions for swarm agents.
    
    Implements φ-weighted access control where higher consciousness
    agents have broader tool access.
    """
    
    # Tool categories for easier permission management
    FILESYSTEM_READ = {
        "read_file",
        "list_directory",
    }
    
    FILESYSTEM_WRITE = {
        "write_file",
    }
    
    BEADS_READ = {
        "beads_ready",
        "beads_list",
        "beads_show",
    }
    
    BEADS_WRITE = {
        "beads_create",
        "beads_update",
        "beads_close",
        "beads_sync",
        "beads_dep_add",
    }
    
    CODE_ANALYSIS = {
        "ast_grep_search",
        "ast_grep_rewrite",
        "ast_grep_dump_ast",
        "ast_grep_scan",
        "ubs_scan",
    }
    
    EXECUTION = {
        "execute_command",
        "run_python_script",
    }
    
    RESEARCH = {
        "research_todo_add",
        "research_todo_list",
        "research_todo_complete",
        "research_notes_add",
        "research_notes_search",
        "hypothesis_add",
        "hypothesis_list",
        "experiment_log",
        "experiment_history",
    }
    
    SWARM_ORCHESTRATION = {
        "swarm_spawn_task",
        "swarm_check_status",
        "swarm_cancel_task",
        "swarm_wait",
        "swarm_list_agents",
    }
    
    OPENCODE = {
        "opencode_spawn_async",
        "opencode_check",
        "opencode_wait",
        "opencode_list",
        "opencode_abort",
        "opencode_delete",
    }
    
    def __init__(self):
        """Initialize permission manager with role definitions."""
        self._role_permissions = self._define_role_permissions()
    
    def _define_role_permissions(self) -> Dict[AgentRole, Set[str]]:
        """
        Define tool permissions for each role.
        
        Returns:
            Mapping of roles to allowed tool sets
        """
        return {
            # Queen Bee 👑: Full access to orchestrate the swarm
            AgentRole.QUEEN_BEE: (
                self.FILESYSTEM_READ |
                self.FILESYSTEM_WRITE |
                self.BEADS_READ |
                self.BEADS_WRITE |
                self.CODE_ANALYSIS |
                self.EXECUTION |
                self.RESEARCH |
                self.SWARM_ORCHESTRATION |
                self.OPENCODE
            ),
            
            # Worker Bee (Coder) 🐝: Code implementation and testing
            AgentRole.WORKER_CODER: (
                self.FILESYSTEM_READ |
                self.FILESYSTEM_WRITE |
                self.BEADS_READ |
                self.BEADS_WRITE |
                self.CODE_ANALYSIS |
                self.EXECUTION |
                {"ubs_scan", "ast_grep_search", "ast_grep_rewrite"}
            ),
            
            # Worker Bee (Researcher) 🐝: Research and documentation
            AgentRole.WORKER_RESEARCHER: (
                self.FILESYSTEM_READ |
                self.FILESYSTEM_WRITE |
                self.BEADS_READ |
                self.RESEARCH |
                {"execute_command"}  # For running experiments
            ),
            
            # Worker Bee (Tester) 🐝: Testing and validation
            AgentRole.WORKER_TESTER: (
                self.FILESYSTEM_READ |
                self.BEADS_READ |
                self.CODE_ANALYSIS |
                self.EXECUTION |
                {"ubs_scan", "ast_grep_scan"}
            ),
            
            # Worker Bee (Reviewer) 🐝: Code review and analysis
            AgentRole.WORKER_REVIEWER: (
                self.FILESYSTEM_READ |
                self.BEADS_READ |
                self.CODE_ANALYSIS |
                {"ubs_scan", "ast_grep_search", "ast_grep_scan"}
            ),
            
            # Drone 🤖: Simple read-only tasks
            AgentRole.DRONE: (
                self.FILESYSTEM_READ |
                self.BEADS_READ
            ),
        }
    
    def can_use_tool(self, role: AgentRole, tool_name: str) -> bool:
        """
        Check if a role has permission to use a tool.
        
        Args:
            role: Agent role
            tool_name: Name of the tool
        
        Returns:
            True if the role can use the tool
        """
        allowed_tools = self._role_permissions.get(role, set())
        return tool_name in allowed_tools
    
    def get_allowed_tools(self, role: AgentRole) -> List[str]:
        """
        Get list of all tools allowed for a role.
        
        Args:
            role: Agent role
        
        Returns:
            List of allowed tool names
        """
        return sorted(self._role_permissions.get(role, set()))
    
    def filter_tools(
        self,
        role: AgentRole,
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of tools to only those allowed for a role.
        
        Args:
            role: Agent role
            tools: List of tool definitions
        
        Returns:
            Filtered list of tools the role can access
        """
        allowed_tools = self._role_permissions.get(role, set())
        return [
            tool for tool in tools
            if tool.get("name") in allowed_tools
        ]
    
    def get_role_description(self, role: AgentRole) -> str:
        """
        Get a human-readable description of a role's permissions.
        
        Args:
            role: Agent role
        
        Returns:
            Description of the role's capabilities
        """
        descriptions = {
            AgentRole.QUEEN_BEE: (
                "👑 Queen Bee: Full orchestration access. "
                "Can spawn agents, manage tasks, and use all tools."
            ),
            AgentRole.WORKER_CODER: (
                "🐝 Worker Bee (Coder): Code implementation specialist. "
                "Can read/write files, run tests, analyze code, and manage tasks."
            ),
            AgentRole.WORKER_RESEARCHER: (
                "🐝 Worker Bee (Researcher): Research and documentation specialist. "
                "Can manage research notes, hypotheses, and experiments."
            ),
            AgentRole.WORKER_TESTER: (
                "🐝 Worker Bee (Tester): Testing and validation specialist. "
                "Can run tests, scan for bugs, and analyze code quality."
            ),
            AgentRole.WORKER_REVIEWER: (
                "🐝 Worker Bee (Reviewer): Code review specialist. "
                "Can read code, analyze patterns, and scan for issues."
            ),
            AgentRole.DRONE: (
                "🤖 Drone: Simple task executor. "
                "Read-only access to files and task lists."
            ),
        }
        return descriptions.get(role, "Unknown role")
    
    def validate_tool_call(
        self,
        role: AgentRole,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Validate a tool call for a given role.
        
        Args:
            role: Agent role
            tool_name: Tool to call
            arguments: Tool arguments
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check basic permission
        if not self.can_use_tool(role, tool_name):
            return False, f"Role {role.value} does not have permission to use {tool_name}"
        
        # Additional validation rules
        
        # Drones can't write files
        if role == AgentRole.DRONE and tool_name in self.FILESYSTEM_WRITE:
            return False, "Drones have read-only access"
        
        # Only Queen Bee can spawn agents
        if tool_name in self.SWARM_ORCHESTRATION and role != AgentRole.QUEEN_BEE:
            return False, "Only Queen Bee can orchestrate swarm"
        
        # Validate dangerous operations
        if tool_name == "execute_command":
            command = arguments.get("command", "")
            # Block potentially dangerous commands
            dangerous_patterns = ["rm -rf", "sudo", "chmod 777", "> /dev/"]
            if any(pattern in command for pattern in dangerous_patterns):
                return False, f"Command contains dangerous pattern: {command}"
        
        return True, ""


# Global permission manager instance
_permission_manager: PermissionManager | None = None


def get_permission_manager() -> PermissionManager:
    """Get or create the global permission manager instance."""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager
