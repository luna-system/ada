"""
Filesystem Tools 📁

Basic file and directory operations.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import subprocess
from pathlib import Path
from typing import List


def register_filesystem_tools(mcp, get_path_context, format_path_context):
    """Register filesystem operation tools."""

    @mcp.tool()
    def execute_command(command: str, cwd: str = None, timeout: int = 30) -> str:
        """
        Execute a shell command and return the full output (stdout + stderr).

        Args:
            command: The shell command to execute
            cwd: Working directory (optional, defaults to current directory)
            timeout: Timeout in seconds (optional, defaults to 30)

        Returns:
            Full command output including stdout, stderr, exit code, and path context
        """
        path_context = get_path_context(cwd)
        working_dir = path_context["full_path"]

        output = format_path_context(path_context) + "\n"
        output += f"💻 Command: {command}\n\n"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=timeout,
            )

            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"EXIT CODE: {result.returncode}"

            return output

        except subprocess.TimeoutExpired:
            return output + f"❌ Command timed out after {timeout} seconds"
        except Exception as e:
            return output + f"❌ Error executing command: {str(e)}"

    @mcp.tool()
    def run_python_script(script_path: str, cwd: str = None, args: List[str] = None) -> str:
        """
        Execute a Python script and capture all output.

        Args:
            script_path: Path to the Python script to execute
            cwd: Working directory (optional)
            args: Command line arguments for the script (optional)

        Returns:
            Full script output including stdout, stderr, and exit code
        """
        if args is None:
            args = []

        command = ["python3", script_path] + args

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, cwd=cwd, timeout=60
            )

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"EXIT CODE: {result.returncode}"

            return output

        except Exception as e:
            return f"Error running Python script: {str(e)}"

    @mcp.tool()
    def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
        """
        Read the contents of a file.

        Args:
            file_path: Path to the file to read
            encoding: File encoding (optional, defaults to utf-8)

        Returns:
            File contents as string with path context
        """
        try:
            path = Path(file_path).resolve()
            path_context = get_path_context(str(path.parent))

            output = format_path_context(path_context) + "\n"
            output += f"📄 File: {path.name}\n"
            output += f"📍 Full Path: {str(path)}\n\n"

            content = path.read_text(encoding=encoding)
            output += f"--- Content ({len(content)} chars) ---\n{content}"

            return output
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

    @mcp.tool()
    def write_file_content(file_path: str, content: str, encoding: str = "utf-8") -> str:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            encoding: File encoding (optional, defaults to utf-8)

        Returns:
            Success message with character count and path context
        """
        try:
            path = Path(file_path).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)

            path_context = get_path_context(str(path.parent))

            path.write_text(content, encoding=encoding)

            output = format_path_context(path_context) + "\n"
            output += f"📄 File: {path.name}\n"
            output += f"📍 Full Path: {str(path)}\n"
            output += f"✅ Successfully wrote {len(content)} characters"

            return output
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"

    @mcp.tool()
    def list_directory(directory_path: str, show_hidden: bool = False) -> str:
        """
        List contents of a directory.

        Args:
            directory_path: Path to the directory to list
            show_hidden: Whether to show hidden files (optional, defaults to false)

        Returns:
            Directory listing with file types and path context
        """
        try:
            path = Path(directory_path).resolve()

            if not path.exists():
                return f"❌ Directory does not exist: {directory_path}"

            if not path.is_dir():
                return f"❌ Path is not a directory: {directory_path}"

            path_context = get_path_context(str(path))

            output = format_path_context(path_context) + "\n\n"

            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith("."):
                    continue

                item_type = "📁" if item.is_dir() else "📄"
                items.append(f"{item_type} {item.name}")

            items.sort()
            output += f"Contents ({len(items)} items):\n" + "\n".join(items)

            return output

        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
