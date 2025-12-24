"""Brain-side reasoning tools for recursive reasoning loop.

These tools run within the Ada brain process and can access internal
state, files, and data structures without needing VS Code.

@ai-indexable: reasoning-tools
@ai-purpose: Brain-side tool implementations for v4.0 recursive reasoning
"""
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BrainTools:
    """Collection of brain-side tools for reasoning loop."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize brain tools.
        
        Args:
            workspace_root: Root directory of workspace for file operations.
                           Defaults to /workspace (Docker mount) if None.
        """
        self.workspace_root = workspace_root or Path("/workspace")
        logger.info(f"BrainTools initialized with workspace: {self.workspace_root}")
    
    def read_file(self, file_path: str, start_line: Optional[int] = None, 
                  end_line: Optional[int] = None) -> str:
        """Read contents of a file in the workspace.
        
        Args:
            file_path: Path relative to workspace root
            start_line: Optional starting line number (1-indexed)
            end_line: Optional ending line number (1-indexed, inclusive)
            
        Returns:
            File contents or error message
        """
        try:
            # Resolve path relative to workspace
            full_path = self.workspace_root / file_path
            
            # Security check - stay within workspace
            if not full_path.resolve().is_relative_to(self.workspace_root.resolve()):
                return f"ERROR: Path {file_path} is outside workspace"
            
            if not full_path.exists():
                return f"ERROR: File not found: {file_path}"
            
            if not full_path.is_file():
                return f"ERROR: Not a file: {file_path}"
            
            # Read file
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply line range if specified
            if start_line is not None or end_line is not None:
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                lines = lines[start_idx:end_idx]
                
                header = f"File: {file_path} (lines {start_line or 1}-{end_line or len(lines)})\n"
            else:
                header = f"File: {file_path} ({len(lines)} lines)\n"
            
            content = ''.join(lines)
            return header + "=" * 60 + "\n" + content
            
        except UnicodeDecodeError:
            return f"ERROR: Cannot read {file_path} (binary file?)"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"ERROR: {str(e)}"
    
    def list_directory(self, dir_path: str = ".", pattern: str = "*") -> str:
        """List files in a directory.
        
        Args:
            dir_path: Directory path relative to workspace root
            pattern: Glob pattern for filtering (e.g., "*.py", "test_*")
            
        Returns:
            Formatted directory listing or error message
        """
        try:
            # Resolve path
            full_path = self.workspace_root / dir_path
            
            # Security check
            if not full_path.resolve().is_relative_to(self.workspace_root.resolve()):
                return f"ERROR: Path {dir_path} is outside workspace"
            
            if not full_path.exists():
                return f"ERROR: Directory not found: {dir_path}"
            
            if not full_path.is_dir():
                return f"ERROR: Not a directory: {dir_path}"
            
            # List files matching pattern
            entries = sorted(full_path.glob(pattern))
            
            if not entries:
                return f"Directory: {dir_path}\nNo files matching '{pattern}'"
            
            # Format output
            lines = [f"Directory: {dir_path} (pattern: {pattern})", "=" * 60]
            
            for entry in entries:
                rel_path = entry.relative_to(self.workspace_root)
                if entry.is_dir():
                    lines.append(f"📁 {rel_path}/")
                else:
                    size_kb = entry.stat().st_size / 1024
                    lines.append(f"📄 {rel_path} ({size_kb:.1f} KB)")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            return f"ERROR: {str(e)}"
    
    def grep_search(self, pattern: str, file_pattern: str = "**/*.py", 
                   max_results: int = 20) -> str:
        """Search for a pattern in files.
        
        Args:
            pattern: Text pattern to search for (simple string match)
            file_pattern: Glob pattern for files to search
            max_results: Maximum number of matches to return
            
        Returns:
            Formatted search results or error message
        """
        try:
            results = []
            files_searched = 0
            
            # Find matching files
            for file_path in self.workspace_root.glob(file_pattern):
                if not file_path.is_file():
                    continue
                
                files_searched += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                rel_path = file_path.relative_to(self.workspace_root)
                                results.append((str(rel_path), line_num, line.strip()))
                                
                                if len(results) >= max_results:
                                    break
                    
                    if len(results) >= max_results:
                        break
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            # Format output
            if not results:
                return f"Pattern '{pattern}' not found in {files_searched} files matching '{file_pattern}'"
            
            lines = [
                f"Search: '{pattern}' in {file_pattern}",
                f"Found {len(results)} matches in {files_searched} files searched",
                "=" * 60
            ]
            
            for file_path, line_num, line_text in results:
                lines.append(f"{file_path}:{line_num}")
                lines.append(f"  {line_text}")
            
            if len(results) >= max_results:
                lines.append(f"\n(Showing first {max_results} results)")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error searching for pattern '{pattern}': {e}")
            return f"ERROR: {str(e)}"
