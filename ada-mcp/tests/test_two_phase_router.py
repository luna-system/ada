"""
Tests for Two-Phase Pattern Router

Phase 1: Tool Call (fast, direct)
- Query → Tool → Response (no LLM)
- Example: "introspect" → ada_introspect tool → transparency badges

Phase 2: Tool + Reasoning (thoughtful)
- Query → Tool → LLM Reasoning → Response
- Example: "introspect and suggest a TODO" → metadata → LLM thinks about it

The router decides automatically based on query intent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from ada_mcp.tools.two_phase_router import (
    QueryIntent,
    TwoPhaseRouter,
    should_use_tool,
    extract_tool_request,
)


def test_query_intent_classification():
    """Classify different query types."""
    # Tool-only queries
    assert should_use_tool("introspect") is True
    assert should_use_tool("analyze your architecture") is True
    assert should_use_tool("what files do you use") is True
    
    # Two-phase queries (tool + reasoning)
    assert should_use_tool("introspect and suggest a TODO") is True  # Needs reasoning
    assert should_use_tool("read context.md and explain") is True   # Needs explanation
    assert should_use_tool("find bugs using analysis") is True      # Needs thinking
    
    # Pure chat (no tool)
    assert should_use_tool("hello") is False
    assert should_use_tool("how are you") is False
    assert should_use_tool("tell me a story") is False


def test_extract_tool_from_query():
    """Extract tool name and reasoning request."""
    # Simple tool call
    tool, reason = extract_tool_request("introspect")
    assert tool == "introspection"
    assert reason is None
    
    # Tool + reasoning
    tool, reason = extract_tool_request("introspect and suggest an easy TODO")
    assert tool == "introspection"
    assert "suggest an easy" in reason.lower()
    
    tool, reason = extract_tool_request("analyze your architecture to find bottlenecks")
    assert tool == "analysis"
    assert "find" in reason.lower() or "bottleneck" in reason.lower()


def test_router_phase1_only():
    """Phase 1: Tool-only execution."""
    router = TwoPhaseRouter()
    
    # Introspection query
    phase = router.classify_query("introspect")
    
    assert phase == "tool_only"
    assert router.should_invoke_tool("introspect") is True
    assert router.should_invoke_llm("introspect") is False


def test_router_phase2_reasoning():
    """Phase 2: Tool + LLM reasoning."""
    router = TwoPhaseRouter()
    
    # Query that needs both tool and reasoning
    phase = router.classify_query("introspect and find the easiest TODO to tackle")
    
    assert phase == "tool_and_reasoning"
    assert router.should_invoke_tool(phase) is True
    assert router.should_invoke_llm(phase) is True


def test_router_pure_chat():
    """No tools needed - just chat."""
    router = TwoPhaseRouter()
    
    phase = router.classify_query("tell me a story about programming")
    
    assert phase == "chat_only"
    assert router.should_invoke_tool(phase) is False
    assert router.should_invoke_llm(phase) is True


def test_metadata_enables_routing():
    """Metadata from tool enables intelligent LLM routing."""
    # Simulate introspection result
    metadata = {
        "toolName": "introspection",
        "filesAccessed": ["context.md", "codebase-map.json", "TODO.md"],
        "actionsTaken": ["read_file", "parse", "analyze"],
        "durationMs": 142,
    }
    
    # Router can use metadata to decide what to do next
    router = TwoPhaseRouter()
    
    # If user asked "suggest a TODO", router sees metadata has TODO.md
    # It can inject that into the LLM's context
    should_inject = router.should_inject_metadata_to_llm(metadata, "suggest")
    assert should_inject is True
    
    # For tool-only queries, no LLM injection needed
    should_inject = router.should_inject_metadata_to_llm(metadata, "introspect")
    assert should_inject is False


def test_two_phase_flow():
    """Complete two-phase flow: tool → metadata → reasoning."""
    router = TwoPhaseRouter()
    
    query = "introspect and suggest the highest-impact task"
    phase = router.classify_query(query)
    
    # Phase 1: Determine if we need tool
    assert router.should_invoke_tool(phase) is True
    
    # Phase 2: Tool executes and produces metadata
    # (In real scenario, tool would run here)
    metadata = {
        "toolName": "introspection",
        "filesAccessed": ["TODO.md", "GOTCHAS.md"],
        "durationMs": 142,
    }
    
    # Phase 3: Determine if we inject metadata to LLM
    assert router.should_inject_metadata_to_llm(metadata, query) is True
    
    # Phase 4: Format prompt for LLM
    prompt_context = router.format_metadata_for_llm(metadata, query)
    assert "filesAccessed" in str(prompt_context) or "TODO.md" in str(prompt_context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
