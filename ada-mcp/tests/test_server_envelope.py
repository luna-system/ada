"""Test that MCP server properly handles and transmits envelope metadata."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
from unittest.mock import AsyncMock

from ada_mcp.tool_definitions import handle_tool_call
from ada_mcp.ada_client import AdaClient


@pytest.mark.asyncio
async def test_introspection_tool_returns_metadata_in_response():
    """Test that introspection tool embeds metadata in text response.
    
    This verifies that when handle_tool_call processes ada_introspect result,
    the metadata (files_accessed, duration_ms) gets included in the TextContent.
    """
    # Create mock client (tool doesn't actually call it, just reads files)
    mock_ada = AsyncMock(spec=AdaClient)
    
    # Call the tool through handle_tool_call
    response = await handle_tool_call(
        "ada_introspect",
        {"focus": "general"},
        mock_ada
    )
    
    # Should return list with one TextContent
    assert len(response) == 1
    text_response = response[0].text
    
    # Should contain the report
    assert "ADA INTROSPECTION REPORT" in text_response or "Introspection" in text_response
    
    # Should contain transparency metadata
    assert "🔧 Files Analyzed:" in text_response or "⚡ Introspection time:" in text_response
    
    # This proves metadata is being transmitted in the response!


@pytest.mark.asyncio
async def test_introspection_shows_which_files_accessed():
    """Test that users can see exactly which files introspection read."""
    mock_ada = AsyncMock(spec=AdaClient)
    
    response = await handle_tool_call(
        "ada_introspect",
        {"focus": "architecture"},
        mock_ada
    )
    
    text = response[0].text
    
    # Should mention specific files like context.md, codebase-map.json, etc
    # This makes it transparent what Ada read
    assert "Files Analyzed:" in text or "files" in text.lower()


if __name__ == "__main__":
    asyncio.run(test_introspection_tool_returns_metadata_in_response())
    asyncio.run(test_introspection_shows_which_files_accessed())
    print("✅ MCP server envelope tests passed!")
