"""
ACP (Ada Context Protocol) - Tool access layer for swarm agents.

This module provides swarm agents with access to all MCP tools
through the ada-mcp server, with role-based permission management.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from .client import ACPClient
from .permissions import AgentRole, PermissionManager, get_permission_manager

__all__ = ["ACPClient", "AgentRole", "PermissionManager", "get_permission_manager"]
