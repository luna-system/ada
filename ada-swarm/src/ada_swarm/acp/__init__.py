"""
ACP (Ada Context Protocol) - Tool access layer for swarm agents.

This module provides swarm agents with access to all MCP tools
through the ada-mcp server.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from .client import ACPClient

__all__ = ["ACPClient"]
