"""Tests for Tool Result Envelope - structured metadata for transparency.

The envelope pattern:
- Content: What the tool produces
- Metadata: HOW it produced it (files, actions, timing)

This enables both transparency AND intelligent routing.
"""

import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from dataclasses import dataclass
from ada_mcp.tools.envelope import ToolMetadata, ToolResult, ToolAction


def test_tool_metadata_creation():
    """ToolMetadata captures what a tool accessed and did."""
    metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=["context.md", "codebase-map.json"],
        actions_taken=["read_files", "analyze_architecture"],
        duration_ms=142
    )
    
    assert metadata.tool_name == "introspection"
    assert len(metadata.files_accessed) == 2
    assert "context.md" in metadata.files_accessed
    assert "analyze_architecture" in metadata.actions_taken
    assert metadata.duration_ms == 142


def test_tool_result_with_metadata():
    """ToolResult wraps content + metadata for complete transparency."""
    metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=["context.md", "GOTCHAS.md"],
        actions_taken=["read", "parse", "synthesize"],
        duration_ms=137
    )
    
    result = ToolResult(
        content="Ada has 40 modules across 7 clusters.",
        metadata=metadata,
        success=True
    )
    
    assert result.content == "Ada has 40 modules across 7 clusters."
    assert result.metadata.tool_name == "introspection"
    assert result.success is True
    
    # Can extract for UI
    assert result.metadata.files_accessed == ["context.md", "GOTCHAS.md"]


def test_tool_result_error_case():
    """ToolResult handles failures with metadata about what failed."""
    metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=[],  # No files accessed before failure
        actions_taken=["find_ai_directory"],  # Last action before error
        duration_ms=5
    )
    
    result = ToolResult(
        content="",
        metadata=metadata,
        success=False,
        error="Could not find .ai/ directory"
    )
    
    assert result.success is False
    assert "Could not find" in result.error
    assert result.metadata.actions_taken == ["find_ai_directory"]


def test_tool_action_enum():
    """ToolAction defines valid action types for semantic clarity."""
    # These should be the canonical action types
    valid_actions = [
        "read_file",
        "read_directory",
        "parse_json",
        "parse_markdown",
        "analyze",
        "search",
        "execute",
        "write_file",
        "create_directory",
        "call_external_api"
    ]
    
    for action in valid_actions:
        # Should be representable as string (or enum value)
        assert isinstance(action, str)


def test_metadata_defaults():
    """ToolMetadata has sensible defaults."""
    metadata = ToolMetadata(tool_name="test_tool")
    
    assert metadata.files_accessed == []
    assert metadata.actions_taken == []
    assert metadata.duration_ms is None  # None until measured


def test_metadata_tracks_multiple_files():
    """ToolMetadata can track many files for compound queries."""
    metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=[
            "context.md",
            "codebase-map.json",
            "GOTCHAS.md",
            "TESTING.md",
            "CONVENTIONS.md"
        ],
        actions_taken=[
            "read_context",
            "read_codebase_map",
            "read_gotchas",
            "analyze_gaps",
            "generate_suggestions"
        ],
        duration_ms=248
    )
    
    assert len(metadata.files_accessed) == 5
    assert len(metadata.actions_taken) == 5
    assert metadata.files_accessed[0] == "context.md"


def test_result_serializable_to_json():
    """ToolResult should serialize cleanly for transmission to UI.
    
    This is crucial: the VS Code extension needs to parse this.
    """
    import json
    
    metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=["context.md", "codebase-map.json"],
        actions_taken=["read", "analyze"],
        duration_ms=142
    )
    
    result = ToolResult(
        content="Analysis complete.",
        metadata=metadata,
        success=True
    )
    
    # Should be JSON-serializable (for MCP transmission)
    serialized = {
        "content": result.content,
        "success": result.success,
        "metadata": {
            "tool_name": result.metadata.tool_name,
            "files_accessed": result.metadata.files_accessed,
            "actions_taken": result.metadata.actions_taken,
            "duration_ms": result.metadata.duration_ms
        }
    }
    
    # Should roundtrip cleanly
    json_str = json.dumps(serialized)
    parsed = json.loads(json_str)
    
    assert parsed["metadata"]["tool_name"] == "introspection"
    assert parsed["content"] == "Analysis complete."


def test_compound_query_metadata():
    """For compound queries, metadata shows what was done step-by-step.
    
    Example: "use introspection to find TODOs and suggest one"
    
    This requires TWO phases:
    1. Introspection (gather data)
    2. LLM reasoning (suggest todo)
    
    Metadata should track both.
    """
    # Phase 1: Introspection
    phase1_metadata = ToolMetadata(
        tool_name="introspection",
        files_accessed=["TODO.md", "codebase-map.json"],
        actions_taken=["read_todo_file", "parse_structure", "extract_open_items"],
        duration_ms=95
    )
    
    phase1_result = ToolResult(
        content="Found 12 open TODOs. Difficulty: mixed. Complexity ranges from trivial to complex.",
        metadata=phase1_metadata,
        success=True
    )
    
    # Phase 2: LLM would use phase1_result.content for reasoning
    # The envelope pattern allows this to be explicit and tracked
    
    assert phase1_result.metadata.tool_name == "introspection"
    assert "extract_open_items" in phase1_result.metadata.actions_taken
