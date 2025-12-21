"""Integration test for introspection tool with envelope metadata."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
from ada_mcp.tools.introspection import ada_introspect


@pytest.mark.asyncio
async def test_introspect_with_metadata():
    """Test that introspection tool populates metadata correctly."""
    # Find the ada root (go up from ada-mcp/tests)
    ada_root = Path(__file__).parent.parent.parent.parent / "ada-v1"
    
    if not (ada_root / ".ai").exists():
        # Use current directory as fallback
        ada_root = Path.cwd()
    
    # Run introspection
    result = await ada_introspect(focus="general", workspace_root=str(ada_root))
    
    # Verify structure
    assert result.success is True
    assert result.content  # Has output
    assert result.metadata is not None
    
    # Verify metadata was populated
    assert result.metadata.tool_name == "introspection"
    assert len(result.metadata.files_accessed) > 0
    assert len(result.metadata.actions_taken) > 0
    assert result.metadata.duration_ms is not None and result.metadata.duration_ms >= 0
    
    # Verify it's tracking what we expect
    assert "context.md" in result.metadata.files_accessed or "codebase-map.json" in result.metadata.files_accessed
    assert any("read" in action.lower() for action in result.metadata.actions_taken)


def test_introspect_metadata_structure():
    """Test metadata can be serialized for transmission."""
    # Run sync wrapper for structure test
    ada_root = Path(__file__).parent.parent.parent.parent / "ada-v1"
    if not (ada_root / ".ai").exists():
        ada_root = Path.cwd()
    
    # We can at least test the structure will work
    result = asyncio.run(ada_introspect(focus="general", workspace_root=str(ada_root)))
    
    # Should be serializable
    serialized = result.to_dict()
    
    assert "content" in serialized
    assert "success" in serialized
    assert "metadata" in serialized
    assert "files_accessed" in serialized["metadata"]
    assert "actions_taken" in serialized["metadata"]
    assert "duration_ms" in serialized["metadata"]


if __name__ == "__main__":
    asyncio.run(test_introspect_with_metadata())
    test_introspect_metadata_structure()
    print("✅ Introspection metadata tests passed!")
