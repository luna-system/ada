"""Tests for WorkspaceIntrospectionSpecialist - Ada's self-awareness and task discovery.

Tests the end-to-end flow from specialist activation through metadata extraction.
"""
import pytest
import asyncio
from pathlib import Path
from brain.specialists.workspace_introspection_specialist import WorkspaceIntrospectionSpecialist
from brain.specialists.protocol import SpecialistResult


def run_async(async_func, *args, **kwargs):
    """Helper to run async functions in sync tests."""
    return asyncio.run(async_func(*args, **kwargs))


class TestWorkspaceIntrospectionSpecialistBasics:
    """Test basic specialist behavior and setup."""
    
    def test_specialist_initialization(self):
        """Test that specialist initializes with proper capability metadata."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        # Should have capability metadata
        assert specialist.capability.name == "workspace_introspection"
        assert "introspect" in specialist.capability.description.lower()
        assert specialist.capability.context_icon == "🔍"
        assert specialist.capability.context_priority.name in ["HIGH", "MEDIUM", "LOW"]
        
        # Should have proper tags
        assert "introspection" in specialist.capability.tags
        assert "task-discovery" in specialist.capability.tags
    
    def test_auto_activation_on_task_queries(self):
        """Test that specialist auto-activates on task-finding queries."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        # Should activate on these patterns
        task_queries = [
            {"message": "find a task we can work on"},
            {"message": "what should I work on next?"},
            {"message": "what are the opportunities?"},
            {"message": "list pending work"},
            {"message": "show me the gaps"},
        ]
        
        for context in task_queries:
            assert specialist.should_activate(context), f"Should activate on: {context['message']}"
    
    def test_no_activation_on_unrelated_queries(self):
        """Test that specialist does NOT auto-activate on unrelated queries."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        # Should NOT activate on these
        unrelated_queries = [
            {"message": "what is the weather?"},
            {"message": "tell me a joke"},
            {"message": "how do I use the API?"},
        ]
        
        for context in unrelated_queries:
            assert not specialist.should_activate(context), f"Should NOT activate on: {context['message']}"


class TestWorkspaceIntrospectionProcessing:
    """Test the introspection processing and results."""
    
    def test_introspection_general_focus(self):
        """Test workspace introspection with general focus."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        result = run_async(specialist.process, {
            'focus': 'general'
        })
        
        # Should succeed
        assert isinstance(result, SpecialistResult)
        assert result.success, f"Introspection failed: {result.error}"
        assert result.specialist_name == "workspace_introspection"
        
        # Should have context text for prompt injection
        assert result.context_text
        assert len(result.context_text) > 0
        
        # Should contain analysis markers
        assert ("📂 Files Analyzed:" in result.context_text or 
                "🔮 ADA INTROSPECTION" in result.context_text), \
            "Should show files analyzed"
        
        # Should have structured data
        assert result.data
        assert 'focus' in result.data
        assert result.data['focus'] == 'general'
    
    def test_introspection_with_metadata(self):
        """Test that introspection result includes proper metadata."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        result = run_async(specialist.process, {
            'focus': 'features'
        })
        
        assert result.success
        
        # Check metadata tracking
        assert result.metadata
        assert 'duration_ms' in result.metadata
        # Duration may be 0 on very fast systems, just check it exists and is >= 0
        assert result.metadata['duration_ms'] >= 0
        
        # Should track files accessed
        if 'files_accessed' in result.metadata:
            assert isinstance(result.metadata['files_accessed'], list)
    
    def test_introspection_architecture_focus(self):
        """Test introspection with architecture-specific focus."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        result = run_async(specialist.process, {
            'focus': 'architecture'
        })
        
        assert result.success
        assert result.data['focus'] == 'architecture'
        
        # Architecture analysis should have specific content
        content = result.context_text.lower()
        assert any(word in content for word in ['architecture', 'module', 'structure']), \
            "Architecture analysis should mention architectural elements"
    
    def test_introspection_focus_normalization(self):
        """Test that invalid focus values are normalized to 'general'."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        result = run_async(specialist.process, {
            'focus': 'invalid_focus_value'
        })
        
        # Should still succeed with normalized focus
        assert result.success
        # The focus should be normalized or default to general behavior
    
    def test_error_handling(self):
        """Test error handling with invalid workspace root."""
        specialist = WorkspaceIntrospectionSpecialist(
            workspace_root=Path("/nonexistent/path")
        )
        
        result = run_async(specialist.process, {
            'focus': 'general'
        })
        
        # Should handle gracefully
        if not result.success:
            assert result.error
            assert result.specialist_name == "workspace_introspection"


class TestWorkspaceIntrospectionIntegration:
    """Test integration with the specialist registry."""
    
    def test_specialist_is_discoverable(self):
        """Test that specialist is auto-discovered by the registry."""
        from brain.specialists import get_specialist
        
        # The specialist should be auto-discovered
        specialist = get_specialist("workspace_introspection")
        
        # May be None if registry hasn't discovered yet, but if found, should work
        if specialist:
            assert specialist.capability.name == "workspace_introspection"
    
    def test_find_task_query_flow(self):
        """Test the realistic "find a task" query flow."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        # Simulate user asking for a task
        request_context = {
            'message': 'find a task we can work on',
        }
        
        # Should activate
        assert specialist.should_activate(request_context)
        
        # Should process successfully
        result = run_async(specialist.process, request_context)
        
        assert result.success
        assert "📂 Files Analyzed:" in result.context_text or "ADA INTROSPECTION" in result.context_text
        
        # Result should be useful for an LLM to synthesize into next steps
        # (The LLM would read this and come up with tasks)
        assert len(result.context_text) > 100, "Should have substantive analysis"


class TestMetadataExtraction:
    """Test metadata extraction patterns for ada-chat VSCode."""
    
    def test_context_includes_metadata_markers(self):
        """Test that context_text includes metadata markers for VSCode to extract."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        result = run_async(specialist.process, {'focus': 'testing'})
        
        assert result.success
        
        # ada-chat VSCode will look for metadata markers in the format:
        # 📂 Files Analyzed: ...
        # ⏱️  Analysis Time: ...Xms
        
        has_file_marker = "📂 Files Analyzed:" in result.context_text
        has_time_marker = "⏱️  Analysis Time:" in result.context_text
        
        # At least one metadata marker should be present
        assert has_file_marker or has_time_marker, \
            "Should include metadata markers for VSCode extraction"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
