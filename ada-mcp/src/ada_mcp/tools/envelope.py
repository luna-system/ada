"""Tool Result Envelope - Structured metadata for transparency and routing.

## The Pattern

Every MCP tool returns:
1. **content**: What the tool produces (the actual answer/data)
2. **metadata**: HOW it was produced (files, actions, timing)

This enables:
- **Transparency**: UI can show "🔧 Files: context.md, codebase-map.json"
- **Routing**: LLM can see what tool accessed what, decide how to use it
- **Performance**: Timing data for latency optimization

## Architecture

```
Tool Execution
    ↓
    ├─ Gather content (the answer)
    └─ Gather metadata (how we got it)
    ↓
Return ToolResult(content=answer, metadata={files, actions, timing})
    ↓
MCP Server handles transmission (transparent to tool)
    ↓
VS Code Extension extracts metadata for UI
LLM sees metadata for intelligent reasoning
```

This is unified: same ToolResult structure solves both problems.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolAction:
    """Valid action types for semantic clarity.
    
    These are the canonical actions a tool can perform.
    Used for categorizing what happened during tool execution.
    """
    # File I/O
    READ_FILE = "read_file"
    READ_DIRECTORY = "read_directory"
    WRITE_FILE = "write_file"
    CREATE_DIRECTORY = "create_directory"
    
    # Data processing
    PARSE_JSON = "parse_json"
    PARSE_MARKDOWN = "parse_markdown"
    ANALYZE = "analyze"
    SEARCH = "search"
    
    # External communication
    EXECUTE = "execute"
    CALL_EXTERNAL_API = "call_external_api"


@dataclass
class ToolMetadata:
    """Metadata about how a tool was executed.
    
    This captures EVERYTHING relevant to understanding how the tool worked:
    - What files it read
    - What actions it performed
    - How long it took
    - What tool it was
    
    This data is extracted by MCP server and sent to UI for transparency,
    and also available to LLM for intelligent routing.
    
    Attributes:
        tool_name: Name of the tool that was executed (e.g., "introspection")
        files_accessed: List of files the tool read from
        actions_taken: List of actions performed (e.g., "read_file", "analyze")
        duration_ms: How long the tool took, in milliseconds
    """
    
    tool_name: str
    files_accessed: list[str] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    duration_ms: Optional[int] = None
    
    def add_file(self, filename: str) -> None:
        """Record that a file was accessed."""
        if filename not in self.files_accessed:
            self.files_accessed.append(filename)
    
    def add_action(self, action: str) -> None:
        """Record that an action was performed."""
        self.actions_taken.append(action)


@dataclass
class ToolResult:
    """Result from a tool execution - content + metadata.
    
    This is THE unified type returned by all MCP tools.
    
    The separation of content/metadata enables:
    1. **Transparency**: Show user what files/actions happened
    2. **Routing**: LLM sees metadata, understands tool's work
    3. **Caching**: Can cache content separately from metadata
    4. **Debugging**: Clear view of tool execution
    
    Attributes:
        content: The main output/answer from the tool
        metadata: HOW the tool produced that output
        success: Whether execution succeeded
        error: Error message if success=False
    """
    
    content: str
    metadata: ToolMetadata
    success: bool = True
    error: str = ""
    
    def to_dict(self) -> dict:
        """Serialize to dict for JSON transmission.
        
        Used by MCP server to send to clients (VS Code, etc).
        """
        return {
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "metadata": {
                "tool_name": self.metadata.tool_name,
                "files_accessed": self.metadata.files_accessed,
                "actions_taken": self.metadata.actions_taken,
                "duration_ms": self.metadata.duration_ms,
            }
        }


# For backwards compatibility with existing code that uses base.ToolResult
# We're keeping the old base.ToolResult as-is, but NEW tools should use this
__all__ = ["ToolMetadata", "ToolResult", "ToolAction"]
