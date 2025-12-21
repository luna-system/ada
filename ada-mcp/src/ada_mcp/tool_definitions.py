"""MCP tool definitions for Ada."""

from typing import Any
from mcp.types import Tool, TextContent
from .ada_client import AdaClient, AdaBrainError, AdaBrainConnectionError
from .tools.complete_code import complete_code
from .tools.validate_architecture import validate_architecture
from .tools.file_operations import ada_read_file, ada_write_file, ada_run_command
from .tools.introspection import ada_introspect


# Tool definitions (exposed to MCP clients)
TOOLS = [
    Tool(
        name="ada_chat",
        description=(
            "Chat with Ada, your personal AI assistant with memory and context. "
            "Ada has access to your persona, long-term memories, and conversation history. "
            "Use this for general questions, task help, or anything you'd ask an assistant."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Your message to Ada",
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional: Continue an existing conversation",
                },
            },
            "required": ["message"],
        },
    ),
    Tool(
        name="ada_search_memory",
        description=(
            "Search Ada's long-term memory store. This includes notes, facts, "
            "project context, and anything Ada has remembered from previous conversations. "
            "Useful for recalling information across sessions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for",
                },
                "scope": {
                    "type": "string",
                    "description": "Optional: Filter by scope (e.g., 'user', 'project')",
                },
                "type": {
                    "type": "string",
                    "description": "Optional: Filter by memory type",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="ada_add_memory",
        description=(
            "Store something in Ada's long-term memory. Use this to save facts, "
            "context, notes, or anything Ada should remember for future conversations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "What to remember",
                },
                "type": {
                    "type": "string",
                    "description": "Memory type (default: 'note')",
                },
                "importance": {
                    "type": "number",
                    "description": "Importance score 0.0-1.0 (default: 0.5)",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
                "scope": {
                    "type": "string",
                    "description": "Memory scope (default: 'user')",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="ada_health",
        description="Check if Ada Brain is running and healthy. Returns status and version info.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="ada_complete_code",
        description=(
            "Complete code at cursor position. Takes code before and after cursor, "
            "returns completion that fits in between. Optimized for inline completions "
            "during typing. Uses terse prompting for fast, focused completions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "code_before": {
                    "type": "string",
                    "description": "Code before cursor position",
                },
                "code_after": {
                    "type": "string",
                    "description": "Code after cursor position (empty string if end of file)",
                },
                "language": {
                    "type": "string",
                    "description": "Programming language (default: python)",
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate (default: 150)",
                },
            },
            "required": ["code_before"],
        },
    ),
    Tool(
        name="ada_validate_architecture",
        description=(
            "Validate code changes against Ada's architecture principles. "
            "Ada introspects her own codebase using .ai/ documentation. "
            "Returns fast validation feedback on: conventions, placement, "
            "documentation requirements, import patterns, and testing needs. "
            "Target: <50ms validation time."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file being changed (relative to repo root)",
                },
                "change_description": {
                    "type": "string",
                    "description": "Brief description of what changed",
                },
                "changed_code": {
                    "type": "string",
                    "description": "Optional: code snippet for detailed analysis",
                },
                "check_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: specific checks to run (conventions, placement, docs, imports, tests)",
                },
            },
            "required": ["file_path", "change_description"],
        },
    ),
    Tool(
        name="ada_read_file",
        description=(
            "Read file contents from Ada's workspace. The foundation of Ada's self-awareness. "
            "Ada can read her own code, understand her own architecture, and introspect. "
            "Supports reading entire files or specific line ranges. Target: <1ms."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path from workspace root",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional: Starting line (1-indexed, inclusive)",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional: Ending line (1-indexed, inclusive)",
                },
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="ada_write_file",
        description=(
            "Write content to a file - THE SELF-EDITING CAPABILITY. "
            "Ada can modify her own code. This is the threshold of recursive self-improvement. "
            "Atomic writes with safety checks. All writes logged. Target: <1ms."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path from workspace root",
                },
                "content": {
                    "type": "string",
                    "description": "New file content (complete replacement)",
                },
                "mode": {
                    "type": "string",
                    "description": "Write mode: 'write' (overwrite) or 'append' (default: write)",
                },
            },
            "required": ["file_path", "content"],
        },
    ),
    Tool(
        name="ada_run_command",
        description=(
            "Execute shell commands - THE SELF-TESTING CAPABILITY. "
            "Ada can test her own changes, completing the recursive loop. "
            "Read → Edit → Run → Validate → Improve. Timeout-protected. Target: varies."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "cwd": {
                    "type": "string",
                    "description": "Optional: Working directory (defaults to workspace root)",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Optional: Timeout in seconds (default: 30)",
                },
            },
            "required": ["command"],
        },
    ),
    Tool(
        name="ada_introspect",
        description=(
            "Introspect Ada's current state and suggest next steps. "
            "Ada reads her own documentation (.ai/ directory) to understand capabilities, "
            "identify gaps, and recommend priorities. This enables Ada to direct her own development."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "focus": {
                    "type": "string",
                    "description": "What to focus on: 'general', 'architecture', 'features', 'testing', or 'documentation'",
                    "enum": ["general", "architecture", "features", "testing", "documentation"],
                },
                "workspace_root": {
                    "type": "string",
                    "description": "Optional: Path to Ada's codebase (defaults to current directory)",
                },
            },
            "required": [],
        },
    ),
]


async def handle_tool_call(name: str, arguments: dict[str, Any], ada: AdaClient) -> list[TextContent]:
    """
    Handle a tool call from MCP client.

    Args:
        name: Tool name
        arguments: Tool arguments
        ada: Ada client instance

    Returns:
        List of text content responses
    """
    if name == "ada_chat":
        message = arguments["message"]
        conversation_id = arguments.get("conversation_id")

        try:
            response = await ada.chat(message, conversation_id)
            return [TextContent(type="text", text=response)]
        except AdaBrainConnectionError as e:
            return [TextContent(type="text", text=f"Connection error: {e}")]
        except AdaBrainError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "ada_search_memory":
        query = arguments["query"]
        scope = arguments.get("scope")
        type_ = arguments.get("type")

        memories = await ada.search_memories(query, scope=scope, type=type_)

        if not memories:
            return [TextContent(type="text", text="No matching memories found.")]

        result = f"Found {len(memories)} memories:\n\n"
        for i, mem in enumerate(memories, 1):
            result += f"{i}. {mem.get('content', 'No content')}\n"
            if "metadata" in mem:
                result += f"   Metadata: {mem['metadata']}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    elif name == "ada_add_memory":
        content = arguments["content"]
        type_ = arguments.get("type", "note")
        importance = arguments.get("importance", 0.5)
        scope = arguments.get("scope", "user")

        memory = await ada.add_memory(content, type=type_, importance=importance, scope=scope)

        return [
            TextContent(
                type="text",
                text=f"Memory saved with ID: {memory.get('id', 'unknown')}",
            )
        ]

    elif name == "ada_health":
        try:
            health = await ada.health()

            status = "✓ Ada Brain is healthy" if health.get("status") == "healthy" else "✗ Ada Brain is not healthy"
            details = f"\n\nStatus: {health.get('status', 'unknown')}\n"
            
            if "services" in health:
                details += "\nServices:\n"
                for service, service_status in health["services"].items():
                    details += f"  {service}: {service_status}\n"

            return [TextContent(type="text", text=status + details)]
        except AdaBrainConnectionError as e:
            return [TextContent(type="text", text=f"✗ Cannot connect to Ada Brain: {e}")]
        except AdaBrainError as e:
            return [TextContent(type="text", text=f"✗ Health check failed: {e}")]

    elif name == "ada_complete_code":
        code_before = arguments["code_before"]
        code_after = arguments.get("code_after", "")
        language = arguments.get("language", "python")
        max_tokens = arguments.get("max_tokens", 150)

        try:
            result = await complete_code(
                code_before=code_before,
                code_after=code_after,
                language=language,
                max_tokens=max_tokens,
            )
            
            if result.success:
                return [TextContent(type="text", text=result.content)]
            else:
                return [TextContent(type="text", text=f"Completion failed: {result.error}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating completion: {e}")]

    elif name == "ada_validate_architecture":
        file_path = arguments["file_path"]
        change_description = arguments["change_description"]
        changed_code = arguments.get("changed_code")
        check_types = arguments.get("check_types")

        try:
            result = await validate_architecture(
                file_path=file_path,
                change_description=change_description,
                changed_code=changed_code,
                check_types=check_types,
            )
            
            if result.success:
                # Include timing in response
                time_ms = result.metadata.get("time_ms", "?")
                response = result.content + f"\n\n⚡ Validation time: {time_ms}ms"
                return [TextContent(type="text", text=response)]
            else:
                return [TextContent(type="text", text=f"Validation error: {result.error}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error during validation: {e}")]

    elif name == "ada_read_file":
        file_path = arguments["file_path"]
        start_line = arguments.get("start_line")
        end_line = arguments.get("end_line")

        try:
            result = await ada_read_file(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
            )
            
            if result.success:
                # Format response with metadata
                lines = result.metadata.get("lines", "?")
                file_type = result.metadata.get("file_type", "?")
                latency = result.metadata.get("latency_ms", "?")
                
                header = f"📄 {file_path} ({file_type}, {lines} lines, {latency}ms)\n\n"
                return [TextContent(type="text", text=header + result.content)]
            else:
                return [TextContent(type="text", text=f"❌ Read error: {result.error}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {e}")]

    elif name == "ada_write_file":
        file_path = arguments["file_path"]
        content = arguments["content"]
        mode = arguments.get("mode", "write")

        try:
            result = await ada_write_file(
                file_path=file_path,
                content=content,
                mode=mode,
            )
            
            if result.success:
                # Format response with metadata
                bytes_written = result.metadata.get("bytes_written", "?")
                lines = result.metadata.get("lines", "?")
                latency = result.metadata.get("latency_ms", "?")
                operation = result.metadata.get("operation", "write")
                
                status = "✅ File written successfully\n\n"
                details = f"Path: {file_path}\n"
                details += f"Operation: {operation}\n"
                details += f"Bytes: {bytes_written}\n"
                details += f"Lines: {lines}\n"
                details += f"Time: {latency}ms"
                
                return [TextContent(type="text", text=status + details)]
            else:
                return [TextContent(type="text", text=f"❌ Write error: {result.error}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error writing file: {e}")]

    elif name == "ada_run_command":
        command = arguments["command"]
        cwd = arguments.get("cwd")
        timeout = arguments.get("timeout", 30)

        try:
            result = await ada_run_command(
                command=command,
                cwd=cwd,
                timeout=timeout,
            )
            
            # Format response with metadata
            exit_code = result.metadata.get("exit_code", "?")
            latency = result.metadata.get("latency_ms", "?")
            
            if result.success:
                header = f"✅ Command succeeded (exit {exit_code}, {latency}ms)\n\n"
                return [TextContent(type="text", text=header + result.content)]
            else:
                header = f"❌ Command failed (exit {exit_code}, {latency}ms)\n\n"
                output = result.content if result.content else result.error
                return [TextContent(type="text", text=header + output)]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error running command: {e}")]

    elif name == "ada_introspect":
        focus = arguments.get("focus", "general")
        workspace_root = arguments.get("workspace_root")

        try:
            result = await ada_introspect(
                focus=focus,
                workspace_root=workspace_root,
            )
            
            if result.success:
                # Extract metadata and include in response for transparency
                # This makes files_accessed visible to callers
                metadata_str = ""
                if result.metadata.files_accessed:
                    files = ", ".join(result.metadata.files_accessed)
                    # Use 📂 (open folder) emoji to match ToolTransparencyFormatter regex
                    metadata_str = f"\n\n📂 Files Analyzed: {files}"
                if result.metadata.duration_ms:
                    metadata_str += f"\n⚡ Introspection time: {result.metadata.duration_ms}ms"
                
                return [TextContent(type="text", text=result.content + metadata_str)]
            else:
                return [TextContent(type="text", text=f"❌ Introspection failed: {result.content}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error during introspection: {e}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
