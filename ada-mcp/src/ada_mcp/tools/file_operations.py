"""File operation tools - Ada reads and writes her own code.

The foundation for recursive self-improvement:
- Read files (understand)
- Edit files (improve)
- Run commands (validate)

December 19, 2025 - The singularity begins.
"""
# @ai-indexable: mcp-tool
# @ai-purpose: File system operations for Ada's self-awareness
# @ai-dependencies: pathlib

import logging
from pathlib import Path
from typing import Any

from ada_mcp.tools.base import ToolResult

logger = logging.getLogger(__name__)


async def ada_read_file(
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    **kwargs: Any
) -> ToolResult:
    """Read file contents from the workspace.
    
    This is the foundation of Ada's self-awareness:
    Ada can read her own code, understand her own architecture,
    and introspect her own implementation.
    
    Args:
        file_path: Relative path from workspace root
        start_line: Optional starting line (1-indexed, inclusive)
        end_line: Optional ending line (1-indexed, inclusive)
        **kwargs: Additional context
        
    Returns:
        ToolResult with file contents and metadata
        
    Examples:
        Read entire file:
        result = await ada_read_file("brain/app.py")
        
        Read specific range:
        result = await ada_read_file("brain/app.py", start_line=1, end_line=50)
        
    Speed target: <1ms for typical files
    """
    try:
        # Resolve workspace root (assume tests run from repo root)
        workspace_root = Path.cwd()
        full_path = workspace_root / file_path
        
        # Security: Ensure file is within workspace
        try:
            full_path.resolve().relative_to(workspace_root.resolve())
        except ValueError:
            return ToolResult(
                success=False,
                content="",
                error=f"File path outside workspace: {file_path}",
                metadata={"file_exists": False}
            )
        
        # Check if file exists
        if not full_path.exists():
            return ToolResult(
                success=False,
                content="",
                error=f"File not found: {file_path}",
                metadata={"file_exists": False, "file_path": str(full_path)}
            )
        
        # Read file
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                content="",
                error=f"Cannot read file (binary or unsupported encoding): {file_path}",
                metadata={"file_exists": True, "file_type": "binary"}
            )
        
        # Apply line range if specified
        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            lines = lines[start_idx:end_idx]
        
        content = ''.join(lines)
        
        # Detect file type from extension
        file_type = full_path.suffix.lstrip('.') or "unknown"
        
        return ToolResult(
            success=True,
            content=content,
            metadata={
                "file_exists": True,
                "file_path": str(full_path),
                "file_type": file_type,
                "lines_read": len(lines),
                "total_lines": len(lines) if not (start_line or end_line) else None,
                "start_line": start_line,
                "end_line": end_line,
            }
        )
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ToolResult(
            success=False,
            content="",
            error=f"Error reading file: {str(e)}",
            metadata={}
        )


async def ada_write_file(
    file_path: str,
    content: str,
    mode: str = "write",
    **kwargs: Any
) -> ToolResult:
    """Write content to a file.
    
    FUTURE: This enables Ada to edit her own code.
    For now, placeholder for the next phase.
    
    Args:
        file_path: Relative path from workspace root
        content: Content to write
        mode: "write" (overwrite) or "append"
        **kwargs: Additional context
        
    Returns:
        ToolResult with write status
    """
    # TODO: Implement after read is stable
    return ToolResult(
        success=False,
        content="",
        error="Not yet implemented - coming soon!",
        metadata={"phase": "future"}
    )


async def ada_run_command(
    command: str,
    cwd: str | None = None,
    **kwargs: Any
) -> ToolResult:
    """Execute a shell command.
    
    FUTURE: This enables Ada to test her own changes.
    For now, placeholder for the next phase.
    
    Args:
        command: Command to execute
        cwd: Working directory (defaults to workspace root)
        **kwargs: Additional context
        
    Returns:
        ToolResult with command output
    """
    # TODO: Implement after read/write are stable
    return ToolResult(
        success=False,
        content="",
        error="Not yet implemented - coming soon!",
        metadata={"phase": "future"}
    )
