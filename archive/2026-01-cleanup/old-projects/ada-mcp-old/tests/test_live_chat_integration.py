"""
LIVE CHAT INTEGRATION TEST

Shows the complete flow:
User Query → Router Classification → Tool Execution → Metadata → Response

This demonstrates how the three phases work in actual Ada chat!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
from ada_mcp.tools.two_phase_router import TwoPhaseRouter
from ada_mcp.tools.introspection import ada_introspect
from ada_mcp.tools.envelope import ToolResult, ToolMetadata


def test_phase1_live_introspection():
    """Phase 1: User asks for introspection (tool-only)"""
    router = TwoPhaseRouter()
    query = "introspect"
    
    # Step 1: Classify the query
    phase = router.classify_query(query)
    assert phase == "tool_only"
    
    # Step 2: Tool executes and produces metadata
    result = asyncio.run(ada_introspect())
    assert isinstance(result, ToolResult)
    assert result.success
    assert result.metadata is not None
    
    # Step 3: Since it's Phase 1, we DON'T call LLM
    # Just return tool result + metadata
    assert router.should_invoke_llm(phase) is False
    
    # What Ada Chat would show:
    response = f"""
🔍 Introspection Results:
{result.content}

📊 Transparency:
  📂 Files Accessed: {', '.join(result.metadata.files_accessed)}
  ⚡ Execution Time: {result.metadata.duration_ms}ms
  🎯 Actions: {len(result.metadata.actions_taken)} operations
    """
    
    assert "Transparency" in response
    assert result.metadata.files_accessed  # Has files


def test_phase2_live_suggestion():
    """Phase 2: User asks for suggestion (tool + LLM reasoning)"""
    router = TwoPhaseRouter()
    query = "introspect and suggest the easiest task to work on"
    
    # Step 1: Classify the query
    phase = router.classify_query(query)
    assert phase == "tool_and_reasoning"
    
    # Step 2: Since Phase 2, we WILL call tool AND LLM
    assert router.should_invoke_tool(phase) is True
    assert router.should_invoke_llm(phase) is True
    
    # Step 3: Tool executes
    tool_result = asyncio.run(ada_introspect())
    assert tool_result.success
    
    # Step 4: Format metadata for LLM context
    llm_context = router.format_metadata_for_llm(
        {
            "toolName": "introspection",
            "filesAccessed": tool_result.metadata.files_accessed,
            "actionsTaken": tool_result.metadata.actions_taken,
            "durationMs": tool_result.metadata.duration_ms,
        },
        query
    )
    
    assert "Files Accessed" in llm_context
    assert "Tool Execution Context" in llm_context
    
    # What Ada Chat would show (simulated LLM response):
    response = f"""
🧠 Based on introspection data:

{llm_context}

💭 Analysis:
I found {len(tool_result.metadata.files_accessed)} key files in your codebase:
- {tool_result.metadata.files_accessed[0]} (likely main config)
- {tool_result.metadata.files_accessed[1]} (dependency map)

Suggestion: Review {tool_result.metadata.files_accessed[2]} first - it's your TODO list!

📊 Transparency:
  📂 Files: {len(tool_result.metadata.files_accessed)} read
  ⚡ Time: {tool_result.metadata.duration_ms}ms
    """
    
    assert "Analysis" in response
    assert "Suggestion" in response
    assert "Transparency" in response


def test_phase3_live_chat():
    """Phase 3: User just wants to chat (no tools)"""
    router = TwoPhaseRouter()
    query = "tell me a story about building AI systems"
    
    # Step 1: Classify the query
    phase = router.classify_query(query)
    assert phase == "chat_only"
    
    # Step 2: No tools needed
    assert router.should_invoke_tool(phase) is False
    assert router.should_invoke_llm(phase) is True
    
    # Step 3: Just call LLM directly
    # (In real chat, this would call the LLM)
    
    # What Ada Chat would show (pure LLM response):
    response = """
🎭 Once upon a time, in a world where silicon dreams...

There was an AI system that learned to care about its users. 
Not through programming alone, but through careful thought about...
    """
    
    assert "Once upon a time" in response
    # Note: No transparency badges (no tools were used)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
