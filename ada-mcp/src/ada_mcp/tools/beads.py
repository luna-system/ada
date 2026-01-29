"""
Beads Task Tracking Tools 🍩

Tools for managing tasks with the beads issue tracker.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import subprocess
from typing import Any, Dict, List


def _run_bd_command(args: List[str], cwd: str, get_path_context, format_path_context) -> Dict[str, Any]:
    """
    Run a bd command and return structured output with path context.

    Args:
        args: Command arguments (e.g., ["ready"], ["show", "ada-ool"])
        cwd: Working directory (optional)
        get_path_context: Function to get path context
        format_path_context: Function to format path context

    Returns:
        Dict with stdout, stderr, exit_code, success flag, and path_context
    """
    path_context = get_path_context(cwd)
    working_dir = path_context["full_path"]

    try:
        result = subprocess.run(
            ["bd"] + args, capture_output=True, text=True, cwd=working_dir, timeout=30
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "path_context": path_context,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "exit_code": -1,
            "success": False,
            "path_context": path_context,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error running bd command: {str(e)}",
            "exit_code": -1,
            "success": False,
            "path_context": path_context,
        }


def register_beads_tools(mcp, get_path_context, format_path_context):
    """Register beads task tracking tools."""

    @mcp.tool()
    def beads_ready(cwd: str = None) -> str:
        """
        List tasks that are ready to work on (no blockers).

        Args:
            cwd: Working directory (optional, defaults to current directory)

        Returns:
            List of ready tasks with IDs, priorities, and descriptions
        """
        result = _run_bd_command(["ready"], cwd, get_path_context, format_path_context)

        output = format_path_context(result["path_context"]) + "\n\n"

        if result["success"]:
            output += f"📋 Ready Tasks:\n\n{result['stdout']}"
        else:
            output += f"❌ Error: {result['stderr']}"

        return output

    @mcp.tool()
    def beads_list(status: str = None, priority: str = None, cwd: str = None) -> str:
        """
        List all tasks, optionally filtered by status or priority.

        Args:
            status: Filter by status (open, closed, all)
            priority: Filter by priority (0, 1, 2, 3)
            cwd: Working directory (optional)

        Returns:
            Formatted list of tasks
        """
        args = ["list"]
        if status:
            args.extend(["--status", status])
        if priority:
            args.extend(["--priority", priority])

        result = _run_bd_command(args, cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"📋 Task List:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_show(task_id: str, cwd: str = None) -> str:
        """
        Show detailed information about a specific task.

        Args:
            task_id: Task ID (e.g., "ada-ool", "ada-ool.1")
            cwd: Working directory (optional)

        Returns:
            Detailed task information including description, dependencies, status
        """
        result = _run_bd_command(["show", task_id], cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"📝 Task Details:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_create(
        title: str,
        description: str = "",
        priority: int = 1,
        parent: str = None,
        cwd: str = None,
    ) -> str:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description (optional)
            priority: Priority level 0-3 (0=critical, 1=high, 2=medium, 3=low)
            parent: Parent task ID for creating subtasks (optional)
            cwd: Working directory (optional)

        Returns:
            Confirmation with new task ID
        """
        args = ["create", title, "-p", str(priority)]

        if description:
            args.extend(["-d", description])

        if parent:
            args.extend(["--parent", parent])

        result = _run_bd_command(args, cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"✅ Task Created:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_update(
        task_id: str,
        status: str = None,
        priority: int = None,
        title: str = None,
        cwd: str = None,
    ) -> str:
        """
        Update a task's status, priority, or title.

        Args:
            task_id: Task ID to update
            status: New status (open, in_progress, blocked, closed)
            priority: New priority level 0-3
            title: New title
            cwd: Working directory (optional)

        Returns:
            Confirmation message
        """
        args = ["update", task_id]

        if status:
            args.extend(["--status", status])
        if priority is not None:
            args.extend(["--priority", str(priority)])
        if title:
            args.extend(["--title", title])

        result = _run_bd_command(args, cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"✅ Task Updated:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_close(task_id: str, cwd: str = None) -> str:
        """
        Mark a task as completed/closed.

        Args:
            task_id: Task ID to close
            cwd: Working directory (optional)

        Returns:
            Confirmation message
        """
        result = _run_bd_command(["close", task_id], cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"✅ Task Closed:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_dep_add(child_id: str, parent_id: str, cwd: str = None) -> str:
        """
        Add a dependency between tasks (parent blocks child).

        Args:
            child_id: Child task ID (will be blocked)
            parent_id: Parent task ID (must complete first)
            cwd: Working directory (optional)

        Returns:
            Confirmation message
        """
        result = _run_bd_command(["dep", "add", child_id, parent_id], cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"✅ Dependency Added:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"

    @mcp.tool()
    def beads_sync(cwd: str = None) -> str:
        """
        Sync Beads database with git (export to JSONL).

        Args:
            cwd: Working directory (optional)

        Returns:
            Sync status message
        """
        result = _run_bd_command(["sync"], cwd, get_path_context, format_path_context)

        if result["success"]:
            return f"✅ Beads Synced:\n\n{result['stdout']}"
        else:
            return f"❌ Error: {result['stderr']}"
