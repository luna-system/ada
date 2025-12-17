"""MCP tool definitions for Ada."""

from typing import Any
from mcp.types import Tool, TextContent
from .ada_client import AdaClient, AdaBrainError, AdaBrainConnectionError


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

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
