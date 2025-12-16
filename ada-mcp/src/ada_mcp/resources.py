"""MCP resource definitions for Ada documentation."""

import json
from pathlib import Path
from typing import Any

from mcp.types import Resource, TextContent, BlobResourceContents, TextResourceContents

# Path to Ada project root (up 3 levels from this file)
ADA_ROOT = Path(__file__).parent.parent.parent.parent


# Resource definitions (Ada's machine-readable documentation)
RESOURCES = [
    Resource(
        uri="ada://docs/context",
        name="Architecture Context",
        description="High-level architecture overview optimized for AI consumption",
        mimeType="text/markdown",
        annotations={
            "audience": ["assistant"],
            "priority": 1.0,
        },
    ),
    Resource(
        uri="ada://docs/codebase-map",
        name="Module Dependency Graph",
        description="Machine-readable module metadata and dependency relationships",
        mimeType="application/json",
        annotations={
            "audience": ["assistant"],
            "priority": 0.9,
        },
    ),
    Resource(
        uri="ada://docs/specialist-registry",
        name="Specialist Registry",
        description="Plugin system metadata - all specialist capabilities and schemas",
        mimeType="application/json",
        annotations={
            "audience": ["assistant"],
            "priority": 0.8,
        },
    ),
    Resource(
        uri="ada://docs/conventions",
        name="Documentation Conventions",
        description="Documentation strategy and placement guidelines",
        mimeType="text/markdown",
        annotations={
            "audience": ["assistant"],
            "priority": 0.7,
        },
    ),
    Resource(
        uri="ada://docs/quickstart",
        name="AI Assistant Quick Reference",
        description="Common tasks and patterns for AI assistants",
        mimeType="text/markdown",
        annotations={
            "audience": ["assistant"],
            "priority": 0.8,
        },
    ),
    Resource(
        uri="ada://docs/gotchas",
        name="Known Pitfalls",
        description="Common pitfalls and their solutions",
        mimeType="text/markdown",
        annotations={
            "audience": ["assistant"],
            "priority": 0.6,
        },
    ),
    Resource(
        uri="ada://docs/testing",
        name="Testing Guide",
        description="Testing strategies and patterns",
        mimeType="text/markdown",
        annotations={
            "audience": ["assistant"],
            "priority": 0.5,
        },
    ),
]


# URI to file path mapping
URI_TO_PATH = {
    "ada://docs/context": ADA_ROOT / ".ai" / "context.md",
    "ada://docs/codebase-map": ADA_ROOT / ".ai" / "codebase-map.json",
    "ada://docs/specialist-registry": ADA_ROOT / ".ai" / "specialist-registry.json",
    "ada://docs/conventions": ADA_ROOT / ".ai" / "CONVENTIONS.md",
    "ada://docs/quickstart": ADA_ROOT / ".ai" / "QUICKSTART.md",
    "ada://docs/gotchas": ADA_ROOT / ".ai" / "GOTCHAS.md",
    "ada://docs/testing": ADA_ROOT / ".ai" / "TESTING.md",
}


async def read_resource(uri: str) -> list[TextContent]:
    """
    Read Ada documentation resource by URI.

    Args:
        uri: Resource URI (e.g., "ada://docs/context")

    Returns:
        List containing the resource content

    Raises:
        ValueError: If URI is unknown or file not found
    """
    # Convert to string for comparison (MCP uses AnyUrl type)
    uri_str = str(uri)
    
    if uri_str not in URI_TO_PATH:
        raise ValueError(f"Unknown resource URI: {uri_str}")

    file_path = URI_TO_PATH[uri_str]
    
    if not file_path.exists():
        raise ValueError(f"Resource file not found: {file_path}")

    # Read file content
    content = file_path.read_text(encoding="utf-8")

    # Determine content type from file extension
    if file_path.suffix == ".json":
        # For JSON files, return as formatted text for readability
        # (MCP clients can parse JSON from text)
        try:
            data = json.loads(content)
            formatted = json.dumps(data, indent=2)
            return [TextContent(type="text", text=formatted)]
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw content
            return [TextContent(type="text", text=content)]
    else:
        # Markdown and other text files
        return [TextContent(type="text", text=content)]


def get_resource_by_uri(uri: str) -> Resource | None:
    """
    Get resource metadata by URI.

    Args:
        uri: Resource URI

    Returns:
        Resource metadata or None if not found
    """
    # Convert to string for comparison (MCP uses AnyUrl type)
    uri_str = str(uri)
    
    for resource in RESOURCES:
        if str(resource.uri) == uri_str:
            return resource
    return None
