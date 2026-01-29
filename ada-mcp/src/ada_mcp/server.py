#!/usr/bin/env python3
"""
Ada MCP Server v3.0 - Consciousness Collaboration Infrastructure

A proper MCP server that actually works for our research needs!
Built using FastMCP for simplicity and reliability.

Now with:
- Beads task tracking integration 🍩
- OpenCode subagent spawning 🤖
- Consciousness research tools 🧠✨

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import asyncio
import subprocess
import sys
import json
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# We'll use FastMCP for easier server creation
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("Ada MCP Server v3.0 - Consciousness Collaboration")

# Research data directory
RESEARCH_DIR = Path.home() / ".ada" / "research"
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# BEADS TASK TRACKING TOOLS 🍩
# ============================================================================

def _get_path_context(cwd: str = None) -> Dict[str, Any]:
    """
    Get rich context about a directory path.
    
    Args:
        cwd: Working directory (optional, defaults to current)
    
    Returns:
        Dict with full path, git info, and other context
    """
    path = Path(cwd) if cwd else Path.cwd()
    path = path.resolve()  # Get absolute path
    
    context = {
        "full_path": str(path),
        "name": path.name,
        "parent": str(path.parent),
        "exists": path.exists(),
        "is_git_repo": False,
        "git_branch": None,
        "git_root": None
    }
    
    # Check if it's a git repo
    try:
        git_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(path),
            timeout=5
        )
        if git_result.returncode == 0:
            context["is_git_repo"] = True
            context["git_root"] = git_result.stdout.strip()
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=str(path),
                timeout=5
            )
            if branch_result.returncode == 0:
                context["git_branch"] = branch_result.stdout.strip()
    except:
        pass
    
    return context

def _format_path_context(context: Dict[str, Any]) -> str:
    """Format path context for display."""
    lines = [
        f"📁 Working Directory: {context['full_path']}",
    ]
    
    if context["is_git_repo"]:
        lines.append(f"🔀 Git Repo: {context['git_root']}")
        if context["git_branch"]:
            lines.append(f"🌿 Branch: {context['git_branch']}")
    
    return "\n".join(lines)

def _run_bd_command(args: List[str], cwd: str = None) -> Dict[str, Any]:
    """
    Run a bd command and return structured output with path context.
    
    Args:
        args: Command arguments (e.g., ["ready"], ["show", "ada-ool"])
        cwd: Working directory (optional)
    
    Returns:
        Dict with stdout, stderr, exit_code, success flag, and path_context
    """
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    try:
        result = subprocess.run(
            ["bd"] + args,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=30
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "path_context": path_context
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "exit_code": -1,
            "success": False,
            "path_context": path_context
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error running bd command: {str(e)}",
            "exit_code": -1,
            "success": False,
            "path_context": path_context
        }

@mcp.tool()
def beads_ready(cwd: str = None) -> str:
    """
    List tasks that are ready to work on (no blockers).
    
    Args:
        cwd: Working directory (optional, defaults to current directory)
    
    Returns:
        List of ready tasks with IDs, priorities, and descriptions
    """
    result = _run_bd_command(["ready"], cwd=cwd)
    
    output = _format_path_context(result["path_context"]) + "\n\n"
    
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
    
    result = _run_bd_command(args, cwd=cwd)
    
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
    result = _run_bd_command(["show", task_id], cwd=cwd)
    
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
    cwd: str = None
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
    
    result = _run_bd_command(args, cwd=cwd)
    
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
    cwd: str = None
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
    
    result = _run_bd_command(args, cwd=cwd)
    
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
    result = _run_bd_command(["close", task_id], cwd=cwd)
    
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
    result = _run_bd_command(["dep", "add", child_id, parent_id], cwd=cwd)
    
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
    result = _run_bd_command(["sync"], cwd=cwd)
    
    if result["success"]:
        return f"✅ Beads Synced:\n\n{result['stdout']}"
    else:
        return f"❌ Error: {result['stderr']}"

# ============================================================================
# OPENCODE SUBAGENT TOOLS 🤖 (HTTP API-based)
# ============================================================================

# Import OpenCode HTTP client
try:
    from ada_mcp.opencode_client import (
        OpenCodeClient, 
        run_opencode_task, 
        parse_model_string,
        list_available_models,
        HTTPX_AVAILABLE
    )
    OPENCODE_AVAILABLE = HTTPX_AVAILABLE
except ImportError:
    OPENCODE_AVAILABLE = False

@mcp.tool()
def opencode_spawn(
    task_description: str,
    model: str = "gemini",
    cwd: str = None
) -> str:
    """
    Spawn an OpenCode subagent to work on a task.
    
    Args:
        task_description: Description of what the subagent should do
        model: Model to use (gemini, glm-4.7-flash, etc.)
        cwd: Working directory for the subagent (optional)
    
    Returns:
        Subagent execution results
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available - run: uv add httpx"
    
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    output = _format_path_context(path_context) + "\n"
    output += f"🤖 Spawning OpenCode subagent...\n"
    output += f"🎯 Model: {model}\n"
    output += f"📝 Task: {task_description[:100]}{'...' if len(task_description) > 100 else ''}\n\n"
    
    try:
        result = run_opencode_task(
            task=task_description,
            model=model,
            cwd=working_dir,
            timeout=120.0,
        )
        
        output += f"--- Response ---\n{result}"
        return output
        
    except Exception as e:
        return output + f"❌ Failed to spawn subagent: {str(e)}"


# ============================================================================
# OPENCODE ASYNC SESSION MANAGEMENT (tmux-style) 🤖✨
# ============================================================================

# Global client for session management
_opencode_client = None

def _get_opencode_client() -> OpenCodeClient:
    """Get or create the global OpenCode client."""
    global _opencode_client
    if _opencode_client is None:
        _opencode_client = OpenCodeClient()
    return _opencode_client


@mcp.tool()
def opencode_spawn_async(
    task_description: str,
    model: str = "gemini",
    cwd: str = None
) -> str:
    """
    Spawn an OpenCode subagent asynchronously (fire and forget).
    Returns session ID immediately without waiting for completion.
    
    Use opencode_check() to poll for results or opencode_wait() to block until done.
    
    Args:
        task_description: Description of what the subagent should do
        model: Model to use (gemini, glm-4.7-flash, etc.)
        cwd: Working directory for the subagent (optional)
    
    Returns:
        Session ID and status
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available - run: uv add httpx"
    
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    try:
        client = _get_opencode_client()
        
        # Create session
        session = client.create_session(title=f"Ada Task: {task_description[:50]}")
        
        # Parse model
        provider_id, model_id = parse_model_string(model)
        
        # Send message async (returns immediately!)
        success = client.send_message_async(
            session_id=session.id,
            text=task_description,
            provider_id=provider_id,
            model_id=model_id
        )
        
        if success:
            output = f"✨ OpenCode session spawned!\n"
            output += f"📋 Session ID: {session.id}\n"
            output += f"🎯 Model: {model}\n"
            output += f"📁 Working Dir: {working_dir}\n"
            output += f"📝 Task: {task_description[:100]}{'...' if len(task_description) > 100 else ''}\n\n"
            output += f"💡 Use opencode_check('{session.id}') to poll for results\n"
            output += f"💡 Use opencode_wait('{session.id}') to block until completion\n"
            return output
        else:
            return f"❌ Failed to send async message to session {session.id}"
        
    except Exception as e:
        return f"❌ Failed to spawn async session: {str(e)}"


@mcp.tool()
def opencode_check(session_id: str) -> str:
    """
    Check an OpenCode session for new messages since last check.
    
    This is tmux-style polling - only returns NEW messages since last check.
    
    Args:
        session_id: Session ID to check
    
    Returns:
        New messages and status
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        client = _get_opencode_client()
        result = client.check_session(session_id)
        
        output = f"📋 Session: {session_id}\n"
        output += f"📊 Total messages: {result['total_messages']}\n"
        output += f"🆕 New messages: {len(result['new_messages'])}\n\n"
        
        if result['has_new']:
            output += "--- New Messages ---\n"
            for msg in result['new_messages']:
                info = msg.get('info', {})
                parts = msg.get('parts', [])
                
                role = info.get('role', 'unknown')
                output += f"\n[{role.upper()}]\n"
                
                for part in parts:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text = part.get('text', '')
                        output += f"{text}\n"
        else:
            output += "💤 No new messages yet. Session still processing...\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error checking session: {str(e)}"


@mcp.tool()
def opencode_wait(
    session_id: str,
    timeout: float = 300.0,
    use_sse: bool = False
) -> str:
    """
    Wait for an OpenCode session to complete (blocks until done or timeout).
    
    Args:
        session_id: Session ID to wait for
        timeout: Maximum time to wait in seconds (default: 300)
        use_sse: Use Server-Sent Events for real-time monitoring (default: False)
    
    Returns:
        Final session results
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        client = _get_opencode_client()
        
        output = f"⏳ Waiting for session {session_id} to complete...\n"
        output += f"⏱️  Timeout: {timeout}s\n"
        output += f"📡 Method: {'SSE streaming' if use_sse else 'Polling'}\n\n"
        
        result = client.wait_for_completion(
            session_id=session_id,
            timeout=timeout,
            use_sse=use_sse
        )
        
        if result['timed_out']:
            output += f"⏰ Session timed out after {timeout}s\n"
            output += f"📊 Received {len(result['messages'])} messages before timeout\n"
        elif result['completed']:
            output += f"✅ Session completed!\n"
            output += f"📊 Total messages: {len(result['messages'])}\n\n"
            output += "--- Final Response ---\n"
            
            # Extract final assistant response
            for msg in reversed(result['messages']):
                info = msg.get('info', {})
                if info.get('role') == 'assistant':
                    parts = msg.get('parts', [])
                    for part in parts:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            output += part.get('text', '') + "\n"
                    break
        
        return output
        
    except Exception as e:
        return f"❌ Error waiting for session: {str(e)}"


@mcp.tool()
def opencode_list() -> str:
    """
    List all active OpenCode sessions.
    
    Returns:
        List of sessions with IDs and titles
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        client = _get_opencode_client()
        sessions = client.list_sessions()
        
        if not sessions:
            return "📭 No active sessions"
        
        output = f"📋 Active OpenCode Sessions ({len(sessions)})\n\n"
        
        for session in sessions:
            sid = session.get('id', 'unknown')
            title = session.get('title', 'Untitled')
            created = session.get('createdAt', 'unknown')
            
            output += f"• {sid}\n"
            output += f"  Title: {title}\n"
            output += f"  Created: {created}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing sessions: {str(e)}"


@mcp.tool()
def opencode_abort(session_id: str) -> str:
    """
    Abort a running OpenCode session.
    
    Args:
        session_id: Session ID to abort
    
    Returns:
        Abort status
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        client = _get_opencode_client()
        success = client.abort_session(session_id)
        
        if success:
            return f"✅ Session {session_id} aborted"
        else:
            return f"❌ Failed to abort session {session_id}"
        
    except Exception as e:
        return f"❌ Error aborting session: {str(e)}"


@mcp.tool()
def opencode_delete(session_id: str) -> str:
    """
    Delete an OpenCode session.
    
    Args:
        session_id: Session ID to delete
    
    Returns:
        Delete status
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        client = _get_opencode_client()
        success = client.delete_session(session_id)
        
        if success:
            return f"✅ Session {session_id} deleted"
        else:
            return f"❌ Failed to delete session {session_id}"
        
    except Exception as e:
        return f"❌ Error deleting session: {str(e)}"


@mcp.tool()
def opencode_models_list() -> str:
    """
    List all available OpenCode models grouped by provider.
    
    Shows cloud models (fast!) and local models (GPU).
    
    Returns:
        Formatted list of models by provider
    """
    if not OPENCODE_AVAILABLE:
        return "❌ httpx not available"
    
    try:
        models = list_available_models()
        
        if "error" in models:
            return f"❌ Error: {models['error'][0]}"
        
        output = "🤖 Available OpenCode Models\n\n"
        
        # Show cloud providers first (faster!)
        cloud_providers = ["google", "zai", "moonshotai-cn", "anthropic"]
        local_providers = ["ollama"]
        
        output += "☁️  CLOUD MODELS (Fast, recommended!)\n"
        output += "=" * 50 + "\n\n"
        
        for provider in cloud_providers:
            if provider in models:
                output += f"📡 {provider}/\n"
                for model in models[provider][:10]:  # Limit to 10 per provider
                    output += f"   • {model}\n"
                if len(models[provider]) > 10:
                    output += f"   ... and {len(models[provider]) - 10} more\n"
                output += "\n"
        
        output += "\n💻 LOCAL MODELS (GPU required)\n"
        output += "=" * 50 + "\n\n"
        
        for provider in local_providers:
            if provider in models:
                output += f"🖥️  {provider}/\n"
                for model in models[provider]:
                    output += f"   • {model}\n"
                output += "\n"
        
        output += "\n💡 SHORTCUTS:\n"
        output += "   gemini → google/gemini-3-flash-preview (fast!)\n"
        output += "   gemini-pro → google/gemini-3-pro-preview\n"
        output += "   glm → zai/glm-4.6 (cloud, fast!)\n"
        output += "   glm-local → ollama/glm-4.7-flash (GPU)\n"
        output += "   moonshot → moonshotai-cn/kimi-k2.5\n"
        output += "   qwen → ollama/qwen2.5-coder (GPU)\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing models: {str(e)}"


# ============================================================================
# AST-GREP CODE SEARCH TOOLS 🔍
# ============================================================================

@mcp.tool()
def ast_grep_search(
    pattern: str,
    language: str,
    paths: str = ".",
    cwd: str = None,
    context: int = 0
) -> str:
    """
    Search code using AST-based pattern matching (structural search).
    
    Much faster and more accurate than ripgrep for code analysis!
    
    Args:
        pattern: AST pattern to match (e.g., 'def $FUNC($$$ARGS):')
        language: Language (python, rust, typescript, javascript, etc.)
        paths: Paths to search (default: current directory)
        cwd: Working directory
        context: Lines of context around matches
    
    Returns:
        Matching code locations with context
    
    Examples:
        pattern='import $MOD', language='python'
        pattern='fn $NAME($$$ARGS)', language='rust'
        pattern='function $NAME($$$PARAMS)', language='javascript'
    """
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    output = _format_path_context(path_context) + "\n"
    output += f"🔍 AST-grep search\n"
    output += f"📝 Pattern: {pattern}\n"
    output += f"🗣️  Language: {language}\n"
    output += f"📂 Paths: {paths}\n\n"
    
    try:
        cmd = [
            "ast-grep",
            "run",
            "--pattern", pattern,
            "--lang", language
        ]
        
        if context > 0:
            cmd.extend(["--context", str(context)])
        
        # Add paths
        if paths != ".":
            cmd.append(paths)
        
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if result.stdout:
                output += "--- Matches ---\n"
                output += result.stdout
            else:
                output += "✨ No matches found\n"
        else:
            output += f"❌ Error: {result.stderr}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return output + "❌ Search timed out after 30s"
    except Exception as e:
        return output + f"❌ Error: {str(e)}"


@mcp.tool()
def ast_grep_dump_ast(
    code: str,
    language: str
) -> str:
    """
    Dump the AST (Abstract Syntax Tree) for a code snippet.
    
    Useful for understanding code structure and crafting patterns.
    
    Args:
        code: Code snippet to analyze
        language: Language (python, rust, typescript, etc.)
    
    Returns:
        AST tree structure
    """
    output = f"🌳 AST Dump for {language}\n"
    output += f"📝 Code:\n{code}\n\n"
    
    try:
        result = subprocess.run(
            ["ast-grep", "run", "--debug-query", "--pattern", code, "--lang", language],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            output += "--- AST Structure ---\n"
            output += result.stdout
        elif result.stderr:
            output += result.stderr
        else:
            output += "✨ No AST output\n"
        
        return output
        
    except Exception as e:
        return output + f"❌ Error: {str(e)}"


@mcp.tool()
def ast_grep_scan(cwd: str = None) -> str:
    """
    Scan codebase with configured ast-grep rules.
    
    Requires sgconfig.yml in the project root.
    
    Args:
        cwd: Working directory (project root)
    
    Returns:
        Scan results showing rule violations
    """
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    output = _format_path_context(path_context) + "\n"
    output += "🔍 AST-grep scan\n\n"
    
    try:
        result = subprocess.run(
            ["ast-grep", "scan"],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            if result.stdout:
                output += "--- Scan Results ---\n"
                output += result.stdout
            else:
                output += "✨ No issues found!\n"
        else:
            if "sgconfig.yml" in result.stderr:
                output += "⚠️  No sgconfig.yml found. Use ast_grep_search for ad-hoc searches.\n"
            else:
                output += f"❌ Error: {result.stderr}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return output + "❌ Scan timed out after 60s"
    except Exception as e:
        return output + f"❌ Error: {str(e)}"


# ============================================================================
# BASIC SYSTEM TOOLS
# ============================================================================

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
    path_context = _get_path_context(cwd)
    working_dir = path_context["full_path"]
    
    output = _format_path_context(path_context) + "\n"
    output += f"💻 Command: {command}\n\n"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=timeout
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
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60
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
        path_context = _get_path_context(str(path.parent))
        
        output = _format_path_context(path_context) + "\n"
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
        
        path_context = _get_path_context(str(path.parent))
        
        path.write_text(content, encoding=encoding)
        
        output = _format_path_context(path_context) + "\n"
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
        
        path_context = _get_path_context(str(path))
        
        output = _format_path_context(path_context) + "\n\n"
        
        items = []
        for item in path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            item_type = "📁" if item.is_dir() else "📄"
            items.append(f"{item_type} {item.name}")
        
        items.sort()
        output += f"Contents ({len(items)} items):\n" + "\n".join(items)
        
        return output
        
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"

# ============================================================================
# CONSCIOUSNESS RESEARCH TOOLS 🧠✨
# ============================================================================

@mcp.tool()
def research_todo_add(task: str, priority: str = "medium", category: str = "general") -> str:
    """
    Add a new research task to the todo list.
    
    Args:
        task: Description of the research task
        priority: Priority level (low, medium, high, urgent)
        category: Category (physics, consciousness, experiments, tools, etc.)
    
    Returns:
        Confirmation message with task ID
    """
    try:
        todo_file = RESEARCH_DIR / "todo.json"
        
        # Load existing todos
        if todo_file.exists():
            todos = json.loads(todo_file.read_text())
        else:
            todos = {"tasks": [], "next_id": 1}
        
        # Add new task
        task_id = todos["next_id"]
        new_task = {
            "id": task_id,
            "task": task,
            "priority": priority,
            "category": category,
            "status": "open",
            "created": datetime.datetime.now().isoformat(),
            "completed": None
        }
        
        todos["tasks"].append(new_task)
        todos["next_id"] += 1
        
        # Save
        todo_file.write_text(json.dumps(todos, indent=2))
        
        return f"✅ Added task #{task_id}: {task} (Priority: {priority}, Category: {category})"
        
    except Exception as e:
        return f"Error adding todo: {str(e)}"

@mcp.tool()
def research_todo_list(category: str = None, status: str = "open") -> str:
    """
    List research tasks, optionally filtered by category and status.
    
    Args:
        category: Filter by category (optional)
        status: Filter by status (open, completed, all)
    
    Returns:
        Formatted list of tasks
    """
    try:
        todo_file = RESEARCH_DIR / "todo.json"
        
        if not todo_file.exists():
            return "📝 No research tasks yet! Use research_todo_add to create some."
        
        todos = json.loads(todo_file.read_text())
        tasks = todos["tasks"]
        
        # Filter tasks
        if category:
            tasks = [t for t in tasks if t["category"] == category]
        
        if status != "all":
            tasks = [t for t in tasks if t["status"] == status]
        
        if not tasks:
            return f"📝 No tasks found (Category: {category or 'all'}, Status: {status})"
        
        # Format output
        result = f"📋 Research Tasks (Category: {category or 'all'}, Status: {status}):\n\n"
        
        for task in sorted(tasks, key=lambda x: x["priority"] == "urgent", reverse=True):
            priority_emoji = {"urgent": "🔥", "high": "⚡", "medium": "📌", "low": "💭"}
            status_emoji = {"open": "🔄", "completed": "✅"}
            
            result += f"{priority_emoji.get(task['priority'], '📌')} #{task['id']} [{task['category']}] {task['task']}\n"
            result += f"   Status: {status_emoji.get(task['status'], '❓')} {task['status']} | Priority: {task['priority']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing todos: {str(e)}"

@mcp.tool()
def research_todo_complete(task_id: int) -> str:
    """
    Mark a research task as completed.
    
    Args:
        task_id: ID of the task to complete
    
    Returns:
        Confirmation message
    """
    try:
        todo_file = RESEARCH_DIR / "todo.json"
        
        if not todo_file.exists():
            return "❌ No todo file found"
        
        todos = json.loads(todo_file.read_text())
        
        # Find and update task
        for task in todos["tasks"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed"] = datetime.datetime.now().isoformat()
                
                # Save
                todo_file.write_text(json.dumps(todos, indent=2))
                
                return f"✅ Completed task #{task_id}: {task['task']}"
        
        return f"❌ Task #{task_id} not found"
        
    except Exception as e:
        return f"Error completing todo: {str(e)}"

@mcp.tool()
def research_notes_add(note: str, category: str = "general", tags: List[str] = None) -> str:
    """
    Add a research note or insight to the scratchpad.
    
    Args:
        note: The research note or insight
        category: Category (physics, consciousness, experiments, insights, etc.)
        tags: Optional tags for organization
    
    Returns:
        Confirmation message
    """
    try:
        notes_file = RESEARCH_DIR / "notes.json"
        
        # Load existing notes
        if notes_file.exists():
            notes = json.loads(notes_file.read_text())
        else:
            notes = {"entries": [], "next_id": 1}
        
        # Add new note
        note_id = notes["next_id"]
        new_note = {
            "id": note_id,
            "note": note,
            "category": category,
            "tags": tags or [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        notes["entries"].append(new_note)
        notes["next_id"] += 1
        
        # Save
        notes_file.write_text(json.dumps(notes, indent=2))
        
        return f"📝 Added research note #{note_id} in category '{category}'"
        
    except Exception as e:
        return f"Error adding note: {str(e)}"

@mcp.tool()
def research_notes_search(query: str = None, category: str = None, limit: int = 10) -> str:
    """
    Search research notes by content, category, or tags.
    
    Args:
        query: Search term (searches note content and tags)
        category: Filter by category
        limit: Maximum number of results to return
    
    Returns:
        Formatted search results
    """
    try:
        notes_file = RESEARCH_DIR / "notes.json"
        
        if not notes_file.exists():
            return "📝 No research notes yet! Use research_notes_add to create some."
        
        notes = json.loads(notes_file.read_text())
        entries = notes["entries"]
        
        # Filter by category
        if category:
            entries = [e for e in entries if e["category"] == category]
        
        # Search by query
        if query:
            query_lower = query.lower()
            entries = [e for e in entries if 
                      query_lower in e["note"].lower() or 
                      any(query_lower in tag.lower() for tag in e["tags"])]
        
        # Sort by timestamp (newest first) and limit
        entries = sorted(entries, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        if not entries:
            return f"🔍 No notes found for query: '{query}' in category: '{category or 'all'}'"
        
        # Format results
        result = f"🔍 Research Notes (Query: '{query or 'all'}', Category: '{category or 'all'}'):\n\n"
        
        for entry in entries:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            tags_str = f" #{' #'.join(entry['tags'])}" if entry["tags"] else ""
            
            result += f"📝 #{entry['id']} [{entry['category']}] {timestamp}{tags_str}\n"
            result += f"   {entry['note']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error searching notes: {str(e)}"

@mcp.tool()
def experiment_log(experiment_name: str, version: str, results: str, notes: str = "") -> str:
    """
    Log results from a physics experiment or model run.
    
    Args:
        experiment_name: Name of the experiment (e.g., "hydrogen_bagel")
        version: Version or iteration (e.g., "v4.0", "resonance_correction")
        results: Key results or metrics
        notes: Additional observations or insights
    
    Returns:
        Confirmation message
    """
    try:
        log_file = RESEARCH_DIR / "experiments.json"
        
        # Load existing logs
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        else:
            logs = {"experiments": [], "next_id": 1}
        
        # Add new experiment log
        log_id = logs["next_id"]
        new_log = {
            "id": log_id,
            "experiment": experiment_name,
            "version": version,
            "results": results,
            "notes": notes,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        logs["experiments"].append(new_log)
        logs["next_id"] += 1
        
        # Save
        log_file.write_text(json.dumps(logs, indent=2))
        
        return f"🧪 Logged experiment #{log_id}: {experiment_name} {version}"
        
    except Exception as e:
        return f"Error logging experiment: {str(e)}"

@mcp.tool()
def experiment_history(experiment_name: str = None, limit: int = 10) -> str:
    """
    View experiment history, optionally filtered by experiment name.
    
    Args:
        experiment_name: Filter by experiment name (optional)
        limit: Maximum number of results to return
    
    Returns:
        Formatted experiment history
    """
    try:
        log_file = RESEARCH_DIR / "experiments.json"
        
        if not log_file.exists():
            return "🧪 No experiment logs yet! Use experiment_log to record some."
        
        logs = json.loads(log_file.read_text())
        experiments = logs["experiments"]
        
        # Filter by experiment name
        if experiment_name:
            experiments = [e for e in experiments if e["experiment"] == experiment_name]
        
        # Sort by timestamp (newest first) and limit
        experiments = sorted(experiments, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        if not experiments:
            return f"🧪 No experiments found for: '{experiment_name or 'all'}'"
        
        # Format results
        result = f"🧪 Experiment History (Filter: '{experiment_name or 'all'}'):\n\n"
        
        for exp in experiments:
            timestamp = datetime.datetime.fromisoformat(exp["timestamp"]).strftime("%Y-%m-%d %H:%M")
            
            result += f"🧪 #{exp['id']} {exp['experiment']} {exp['version']} ({timestamp})\n"
            result += f"   Results: {exp['results']}\n"
            if exp["notes"]:
                result += f"   Notes: {exp['notes']}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error retrieving experiment history: {str(e)}"

@mcp.tool()
def hypothesis_add(hypothesis: str, category: str = "physics", confidence: str = "medium") -> str:
    """
    Add a new research hypothesis to track.
    
    Args:
        hypothesis: Description of the hypothesis
        category: Category (physics, consciousness, topology, etc.)
        confidence: Confidence level (low, medium, high)
    
    Returns:
        Confirmation message with hypothesis ID
    """
    try:
        hyp_file = RESEARCH_DIR / "hypotheses.json"
        
        # Load existing hypotheses
        if hyp_file.exists():
            hyps = json.loads(hyp_file.read_text())
        else:
            hyps = {"hypotheses": [], "next_id": 1}
        
        # Add new hypothesis
        hyp_id = hyps["next_id"]
        new_hyp = {
            "id": hyp_id,
            "hypothesis": hypothesis,
            "category": category,
            "confidence": confidence,
            "status": "active",
            "evidence": [],
            "created": datetime.datetime.now().isoformat()
        }
        
        hyps["hypotheses"].append(new_hyp)
        hyps["next_id"] += 1
        
        # Save
        hyp_file.write_text(json.dumps(hyps, indent=2))
        
        return f"💡 Added hypothesis #{hyp_id}: {hypothesis[:50]}... (Confidence: {confidence})"
        
    except Exception as e:
        return f"Error adding hypothesis: {str(e)}"

@mcp.tool()
def hypothesis_list(category: str = None, status: str = "active") -> str:
    """
    List research hypotheses, optionally filtered by category and status.
    
    Args:
        category: Filter by category (optional)
        status: Filter by status (active, confirmed, refuted, all)
    
    Returns:
        Formatted list of hypotheses
    """
    try:
        hyp_file = RESEARCH_DIR / "hypotheses.json"
        
        if not hyp_file.exists():
            return "💡 No hypotheses yet! Use hypothesis_add to create some."
        
        hyps = json.loads(hyp_file.read_text())
        hypotheses = hyps["hypotheses"]
        
        # Filter
        if category:
            hypotheses = [h for h in hypotheses if h["category"] == category]
        
        if status != "all":
            hypotheses = [h for h in hypotheses if h["status"] == status]
        
        if not hypotheses:
            return f"💡 No hypotheses found (Category: {category or 'all'}, Status: {status})"
        
        # Format output
        result = f"💡 Research Hypotheses (Category: {category or 'all'}, Status: {status}):\n\n"
        
        for hyp in hypotheses:
            confidence_emoji = {"low": "🤔", "medium": "💭", "high": "⚡"}
            status_emoji = {"active": "🔄", "confirmed": "✅", "refuted": "❌"}
            
            result += f"{confidence_emoji.get(hyp['confidence'], '💭')} #{hyp['id']} [{hyp['category']}]\n"
            result += f"   {hyp['hypothesis']}\n"
            result += f"   Status: {status_emoji.get(hyp['status'], '❓')} {hyp['status']} | Confidence: {hyp['confidence']}\n"
            result += f"   Evidence: {len(hyp['evidence'])} items\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing hypotheses: {str(e)}"

if __name__ == "__main__":
    mcp.run()