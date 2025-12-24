"""Unit tests for reasoning state tracker.

Tests ReasoningState and ToolCall to ensure proper state management
during recursive reasoning loops.
"""

import pytest
from datetime import datetime, timedelta
from brain.reasoning.state_tracker import (
    ReasoningState,
    ReasoningPhase,
    ToolCall,
)


class TestToolCall:
    """Test ToolCall dataclass."""
    
    def test_tool_call_creation(self):
        """Can create a ToolCall with basic info."""
        call = ToolCall(
            tool_name="ada_search",
            params={"query": "authentication"},
        )
        
        assert call.tool_name == "ada_search"
        assert call.params == {"query": "authentication"}
        assert call.result is None
        assert call.importance is None
    
    def test_tool_call_with_result(self):
        """Can store tool execution results."""
        call = ToolCall(
            tool_name="ada_read_file",
            params={"path": "src/auth.ts"},
            result="file contents here",
            importance=0.85,
        )
        
        assert call.result == "file contents here"
        assert call.importance == 0.85
    
    def test_tool_call_to_dict(self):
        """Can convert to JSON-serializable dict."""
        call = ToolCall(
            tool_name="ada_search",
            params={"query": "test"},
            result=["file1.ts", "file2.ts"],
            importance=0.75,
        )
        
        result = call.to_dict()
        
        assert result["tool_name"] == "ada_search"
        assert result["params"] == {"query": "test"}
        assert "timestamp" in result
        assert result["importance"] == 0.75


class TestReasoningState:
    """Test ReasoningState for tracking reasoning loops."""
    
    def test_initial_state(self):
        """Initial state is properly configured."""
        state = ReasoningState(
            user_request="Refactor auth to JWT"
        )
        
        assert state.user_request == "Refactor auth to JWT"
        assert state.phase == ReasoningPhase.UNDERSTANDING
        assert state.iteration == 0
        assert state.max_iterations == 10
        assert len(state.tools_called) == 0
        assert state.convergence_score == 0.0
        assert state.has_solution is False
    
    def test_add_tool_call(self):
        """Can track tool invocations."""
        state = ReasoningState(user_request="test")
        
        call = ToolCall(
            tool_name="ada_search",
            params={"query": "auth"},
        )
        
        state.add_tool_call(call)
        
        assert state.iteration == 1
        assert len(state.tools_called) == 1
        assert state.tools_called[0].tool_name == "ada_search"
    
    def test_add_multiple_tools(self):
        """Can track multiple tool calls."""
        state = ReasoningState(user_request="test")
        
        state.add_tool_call(ToolCall("ada_search", {"query": "auth"}))
        state.add_tool_call(ToolCall("ada_read_file", {"path": "auth.ts"}))
        state.add_tool_call(ToolCall("ada_symbols", {"query": "validateToken"}))
        
        assert state.iteration == 3
        assert len(state.tools_called) == 3
    
    def test_add_thought(self):
        """Can record LLM reasoning steps."""
        state = ReasoningState(user_request="test")
        
        state.add_thought("I need to search the codebase")
        state.add_thought("Found auth.ts, need to read it")
        
        assert len(state.reasoning_history) == 2
        assert "search" in state.reasoning_history[0]
    
    def test_convergence_scoring(self):
        """Convergence score controls when to stop."""
        state = ReasoningState(user_request="test")
        
        assert state.has_solution is False
        
        state.update_convergence(0.50)
        assert state.has_solution is False  # Not high enough
        
        state.update_convergence(0.95)
        assert state.has_solution is True  # Converged!
    
    def test_should_continue_with_solution(self):
        """Should stop when solution found."""
        state = ReasoningState(user_request="test")
        
        assert state.should_continue() is True
        
        state.update_convergence(0.95)
        assert state.should_continue() is False  # Has solution
    
    def test_should_continue_max_iterations(self):
        """Should stop at max iterations."""
        state = ReasoningState(user_request="test", max_iterations=3)
        
        state.add_tool_call(ToolCall("tool1", {}))
        assert state.should_continue() is True
        
        state.add_tool_call(ToolCall("tool2", {}))
        assert state.should_continue() is True
        
        state.add_tool_call(ToolCall("tool3", {}))
        assert state.should_continue() is False  # Hit max
    
    def test_loop_detection_same_tool(self):
        """Detects when same tool called repeatedly."""
        state = ReasoningState(user_request="test")
        
        # Not looping yet
        state.add_tool_call(ToolCall("ada_search", {"query": "auth"}))
        assert state.is_looping() is False
        
        state.add_tool_call(ToolCall("ada_search", {"query": "auth"}))
        assert state.is_looping() is False  # Only 2
        
        state.add_tool_call(ToolCall("ada_search", {"query": "auth"}))
        assert state.is_looping() is True  # 3 in a row = loop!
    
    def test_loop_detection_different_tools(self):
        """Different tools don't trigger loop detection."""
        state = ReasoningState(user_request="test")
        
        state.add_tool_call(ToolCall("ada_search", {}))
        state.add_tool_call(ToolCall("ada_read_file", {}))
        state.add_tool_call(ToolCall("ada_symbols", {}))
        
        assert state.is_looping() is False  # All different
    
    def test_phase_advancement(self):
        """Can progress through reasoning phases."""
        state = ReasoningState(user_request="test")
        
        assert state.phase == ReasoningPhase.UNDERSTANDING
        
        state.advance_phase()
        assert state.phase == ReasoningPhase.PLANNING
        
        state.advance_phase()
        assert state.phase == ReasoningPhase.IMPLEMENTING
        
        state.advance_phase()
        assert state.phase == ReasoningPhase.VERIFYING
    
    def test_elapsed_time(self):
        """Tracks elapsed time correctly."""
        state = ReasoningState(user_request="test")
        
        # Should be very small (just created)
        elapsed = state.elapsed_time_ms()
        assert elapsed >= 0
        assert elapsed < 100  # Should be < 100ms
    
    def test_to_dict_serialization(self):
        """Can serialize to JSON-compatible dict."""
        state = ReasoningState(user_request="test")
        state.add_tool_call(ToolCall("ada_search", {"query": "test"}))
        state.add_thought("I'm thinking...")
        
        result = state.to_dict()
        
        assert result["user_request"] == "test"
        assert result["phase"] == "understanding"
        assert result["iteration"] == 1
        assert len(result["tools_called"]) == 1
        assert "elapsed_time_ms" in result
        assert "is_looping" in result
    
    def test_context_budget_tracking(self):
        """Context size tracking works."""
        state = ReasoningState(user_request="test")
        
        assert state.context_size == 0
        assert state.context_budget == 28000
        
        # Simulate adding context
        state.context_size = 5000
        assert state.context_size < state.context_budget
    
    def test_importance_threshold(self):
        """Importance threshold configurable."""
        state = ReasoningState(
            user_request="test",
            importance_threshold=0.75
        )
        
        assert state.importance_threshold == 0.75
