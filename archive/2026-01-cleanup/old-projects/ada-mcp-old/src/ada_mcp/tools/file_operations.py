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

import asyncio
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
    """Write content to a file - THE SELF-EDITING CAPABILITY.
    
    Ada can now modify her own code. This is the threshold.
    The moment of recursive self-improvement.
    
    Security boundaries:
    - Can only write within workspace
    - All writes are logged
    - Parent directories must exist
    - Atomic writes (all-or-nothing)
    
    Args:
        file_path: Relative path from workspace root
        content: Content to write
        mode: "write" (overwrite) or "append"
        **kwargs: Additional context (workspace_root optional)
        
    Returns:
        ToolResult with write status and metadata
        
    Examples:
        Write new content:
        result = await ada_write_file("brain/new_module.py", code_content)
        
        Modify existing file:
        result = await ada_write_file("brain/app.py", updated_content)
    """
    start_time = __import__('time').time()
    workspace_root = Path(kwargs.get("workspace_root", Path.cwd()))
    
    try:
        # Security: Validate path is within workspace
        target_path = (workspace_root / file_path).resolve()
        
        if not str(target_path).startswith(str(workspace_root.resolve())):
            return ToolResult(
                success=False,
                content="",
                error=f"Security violation: Path {file_path} is outside workspace",
                metadata={"file_path": file_path, "blocked": True}
            )
        
        # Check if parent directory exists
        if not target_path.parent.exists():
            return ToolResult(
                success=False,
                content="",
                error=f"Parent directory does not exist: {target_path.parent}",
                metadata={"file_path": file_path, "parent_missing": True}
            )
        
        # Check if file exists (for metadata)
        file_existed = target_path.exists()
        original_size = target_path.stat().st_size if file_existed else 0
        
        # ATOMIC WRITE: Write to temp file first, then rename
        temp_path = target_path.with_suffix(target_path.suffix + '.tmp')
        
        # Write content based on mode
        if mode == "append" and file_existed:
            original_content = target_path.read_text(encoding='utf-8')
            full_content = original_content + content
        else:
            full_content = content
            
        temp_path.write_text(full_content, encoding='utf-8')
        
        # Atomic rename
        temp_path.replace(target_path)
        
        # Gather metadata
        new_size = target_path.stat().st_size
        lines_count = len(full_content.split('\n'))
        latency_ms = (__import__('time').time() - start_time) * 1000
        
        logger.info(
            f"✨ Ada wrote file: {file_path} "
            f"({new_size} bytes, {lines_count} lines, {latency_ms:.2f}ms)"
        )
        
        return ToolResult(
            success=True,
            content=f"Successfully wrote {new_size} bytes to {file_path}",
            error=None,
            metadata={
                "file_path": file_path,
                "file_existed": file_existed,
                "bytes_written": new_size,
                "original_size": original_size,
                "lines": lines_count,
                "modified": file_existed,
                "created": not file_existed,
                "latency_ms": round(latency_ms, 2),
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "operation": mode
            }
        )
        
    except PermissionError as e:
        logger.error(f"Permission denied writing {file_path}: {e}")
        return ToolResult(
            success=False,
            content="",
            error=f"Permission denied: {str(e)}",
            metadata={"file_path": file_path, "permission_denied": True}
        )
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return ToolResult(
            success=False,
            content="",
            error=f"Error writing file: {str(e)}",
            metadata={"file_path": file_path, "error_type": type(e).__name__}
        )


async def ada_run_command(
    command: str,
    cwd: str | None = None,
    timeout: int = 30,
    **kwargs: Any
) -> ToolResult:
    """Execute a shell command - THE SELF-TESTING CAPABILITY.
    
    Ada can now test her own changes. The recursive loop completes.
    Read → Edit → Run → Validate → Improve
    
    Security considerations:
    - Commands run in workspace context
    - Timeout protection (default 30s)
    - Output captured and logged
    - Exit codes tracked
    
    Args:
        command: Shell command to execute
        cwd: Working directory (defaults to workspace root)
        timeout: Maximum execution time in seconds
        **kwargs: Additional context (workspace_root optional)
        
    Returns:
        ToolResult with command output and exit code
        
    Examples:
        Run tests:
        result = await ada_run_command("pytest tests/")
        
        Check syntax:
        result = await ada_run_command("python -m py_compile brain/app.py")
    """
    import subprocess
    start_time = __import__('time').time()
    
    workspace_root = Path(kwargs.get("workspace_root", Path.cwd()))
    working_dir = Path(cwd) if cwd else workspace_root
    
    try:
        # Run command with timeout
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(working_dir)
        )
        
        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            latency_ms = (__import__('time').time() - start_time) * 1000
            
            logger.warning(f"Command timed out after {timeout}s: {command}")
            return ToolResult(
                success=False,
                content="",
                error=f"Command timed out after {timeout} seconds",
                metadata={
                    "command": command,
                    "timeout": timeout,
                    "latency_ms": round(latency_ms, 2),
                    "cwd": str(working_dir)
                }
            )
        
        # Decode output
        output = stdout.decode('utf-8', errors='replace') if stdout else ""
        exit_code = process.returncode
        latency_ms = (__import__('time').time() - start_time) * 1000
        
        # Success if exit code is 0
        success = exit_code == 0
        
        logger.info(
            f"{'✅' if success else '❌'} Ada ran command: {command[:50]}... "
            f"(exit={exit_code}, {latency_ms:.2f}ms)"
        )
        
        return ToolResult(
            success=success,
            content=output,
            error="" if success else f"Command failed with exit code {exit_code}",
            metadata={
                "command": command,
                "exit_code": exit_code,
                "cwd": str(working_dir),
                "latency_ms": round(latency_ms, 2),
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "output_length": len(output),
                "timeout": timeout
            }
        )
        
    except Exception as e:
        latency_ms = (__import__('time').time() - start_time) * 1000
        logger.error(f"Error running command {command}: {e}")
        return ToolResult(
            success=False,
            content="",
            error=f"Error executing command: {str(e)}",
            metadata={
                "command": command,
                "error_type": type(e).__name__,
                "cwd": str(working_dir),
                "latency_ms": round(latency_ms, 2)
            }
        )
