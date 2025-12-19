"""Base classes and types for MCP tools."""
# @ai-indexable: mcp-infrastructure
# @ai-purpose: Common types for all MCP tools

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result from a tool execution.
    
    Attributes:
        success: Whether the tool execution succeeded
        content: Main content/output from the tool
        error: Error message if success=False
        metadata: Additional data about the execution
    """
    success: bool
    content: str
    error: str = ""
    metadata: dict[str, Any] | None = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
