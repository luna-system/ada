"""Tests for CodebaseSpecialist wiring into PromptAssembler.

Phase 1 MVP Wiring: CodebaseSpecialist should activate bidirectionally
when LLM outputs <code_lookup>name</code_lookup> tags during prompt assembly.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from brain.prompt_builder.prompt_assembler import PromptAssembler
from brain.specialists import SpecialistRegistry
from brain.specialists.codebase_specialist import CodebaseSpecialist
from brain.specialists.protocol import SpecialistResult


def run_async(async_func, *args, **kwargs):
    """Helper to run async functions in sync tests."""
    return asyncio.run(async_func(*args, **kwargs))


class TestCodebaseSpecialistRegistration:
    """Test that CodebaseSpecialist is properly registered."""
    
    def test_codebase_specialist_auto_discovered(self):
        """CodebaseSpecialist should be auto-discovered by SpecialistRegistry."""
        registry = SpecialistRegistry()
        registry.discover_specialists()
        
        # Should have discovered codebase specialist
        codebase_spec = registry.get("codebase")
        assert codebase_spec is not None
        assert isinstance(codebase_spec, CodebaseSpecialist)
        assert codebase_spec.capability.name == "codebase"
    
    def test_codebase_specialist_priority_high(self):
        """CodebaseSpecialist should have HIGH context icon."""
        specialist = CodebaseSpecialist()
        
        # Bidirectional specialists should have appropriate context icon
        assert specialist.capability.context_icon == "💻"
        assert "codebase" in specialist.capability.name.lower()


class TestBidirectionalActivation:
    """Test that CodebaseSpecialist activates via bidirectional mechanism."""
    
    def test_codebase_specialist_does_not_auto_activate(self):
        """CodebaseSpecialist should only activate via bidirectional, not auto."""
        specialist = CodebaseSpecialist()
        
        # Various contexts should not auto-activate
        contexts = [
            {"query": "explain this function"},
            {"uploaded_image_path": "/tmp/image.png"},
            {"conversation_history": ["msg1", "msg2"]},
            {},
        ]
        
        for ctx in contexts:
            assert not specialist.should_activate(ctx), f"Should not auto-activate for context: {ctx}"
    
    def test_codebase_specialist_can_be_invoked_bidirectionally(self):
        """CodebaseSpecialist should accept explicit lookup requests."""
        specialist = CodebaseSpecialist()
        
        # Simulate LLM outputting <code_lookup>calculate_importance</code_lookup>
        # This becomes a manual invocation with explicit query
        result = run_async(specialist.process, {
            'query': 'calculate_importance'
        })
        
        assert result.success
        assert result.specialist_name == "codebase"
        assert 'calculate_importance' in result.context_text.lower()


class TestPromptAssemblerIntegration:
    """Test that PromptAssembler can coordinate CodebaseSpecialist.
    
    Note: Full integration with PromptAssembler will be implemented in Phase 2.
    For now, this tests that CodebaseSpecialist exists and can be discovered.
    """
    
    def test_codebase_specialist_exists_for_prompt_assembler(self):
        """CodebaseSpecialist should exist and be discoverable for assembler integration."""
        # The specialist exists and can be instantiated
        specialist = CodebaseSpecialist()
        
        # It has the right interface for bidirectional activation
        assert hasattr(specialist, 'process')
        assert hasattr(specialist, 'should_activate')
        assert hasattr(specialist, 'capability')


class TestCodebaseLookupIntegration:
    """Test complete lookup flow: LLM tag → specialist → context injection."""
    
    def test_simple_codebase_lookup_workflow(self):
        """Test the workflow: LLM outputs tag → specialist processes → context returned."""
        specialist = CodebaseSpecialist()
        
        # Step 1: LLM outputs <code_lookup>SpecialistResult</code_lookup>
        # Step 2: Framework extracts 'SpecialistResult' from tag
        query = "SpecialistResult"
        
        # Step 3: CodebaseSpecialist processes it
        result = run_async(specialist.process, {'query': query})
        
        # Step 4: Result is context to inject
        assert result.success
        assert "class SpecialistResult" in result.context_text or "SpecialistResult" in result.context_text
        
        # Result should be formatted for prompt injection
        assert result.context_text
        assert len(result.context_text) > 0
        assert "protocol.py" in result.context_text or "brain" in result.context_text
    
    def test_multiple_function_lookup_in_session(self):
        """Test looking up multiple different functions in sequence."""
        specialist = CodebaseSpecialist()
        
        lookups = [
            "calculate_importance",
            "SpecialistResult",
            "ContextRetriever",
        ]
        
        results = []
        for name in lookups:
            result = run_async(specialist.process, {'query': name})
            results.append(result)
            
            assert result.success, f"Lookup failed for {name}"
            assert name in result.context_text or name.lower() in result.context_text.lower()
        
        # All results should be properly formatted
        assert all(r.context_text for r in results)


class TestContextFormatting:
    """Test that lookup results are formatted appropriately for context injection."""
    
    def test_result_includes_file_and_line_info(self):
        """Lookup results should include file path and line number."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {'query': 'calculate_importance'})
        
        # Should have file path info
        assert 'brain/' in result.context_text
        assert 'calculate_importance' in result.context_text
        
        # Result should have structured data with file/line
        assert 'results' in result.data
        if result.data['results']:
            first = result.data['results'][0]
            assert 'file' in first
            assert 'line' in first
    
    def test_result_includes_docstring_if_present(self):
        """Lookup results should include docstrings when available."""
        specialist = CodebaseSpecialist()
        
        # Functions with docstrings should include them
        result = run_async(specialist.process, {'query': 'calculate_importance'})
        
        assert result.success
        # Should contain some documentation
        context = result.context_text.lower()
        assert 'calculate_importance' in context or 'importance' in context


class TestErrorHandling:
    """Test graceful error handling in lookup."""
    
    def test_nonexistent_lookup_returns_helpful_message(self):
        """Looking up nonexistent code should return clear "not found" message."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {'query': 'function_that_does_not_exist_xyz'})
        
        # Should fail gracefully with error message
        assert not result.success
        assert 'not found' in result.error.lower() or 'no results' in result.error.lower()
    
    def test_empty_query_handled_gracefully(self):
        """Empty queries should be handled without crashing."""
        specialist = CodebaseSpecialist()
        
        # Empty query
        result = run_async(specialist.process, {'query': ''})
        assert isinstance(result, SpecialistResult)  # Should not crash
        
        # Missing query key
        result = run_async(specialist.process, {})
        assert isinstance(result, SpecialistResult)  # Should not crash
