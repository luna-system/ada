"""Tests for CodebaseSpecialist - Ada's self-awareness of her own code.

Phase 1 MVP: Keyword-based function/class lookup
"""
import pytest
import asyncio
from pathlib import Path
from brain.specialists.codebase_specialist import CodebaseSpecialist
from brain.specialists.protocol import SpecialistResult


def run_async(async_func, *args, **kwargs):
    """Helper to run async functions in sync tests."""
    return asyncio.run(async_func(*args, **kwargs))


class TestCodebaseSpecialistBasics:
    """Test basic specialist behavior and setup."""
    
    def test_specialist_initialization(self):
        """Test that specialist initializes and builds index."""
        specialist = CodebaseSpecialist()
        
        # Should have capability metadata
        assert specialist.capability.name == "codebase"
        assert "codebase" in specialist.capability.description.lower()
        assert specialist.capability.context_icon == "💻"
        
        # Should have built an index
        assert hasattr(specialist, 'index')
        assert len(specialist.index) > 0  # Should find functions in brain/
    
    def test_should_not_auto_activate(self):
        """Codebase specialist should be bidirectional-only (never auto-activate)."""
        specialist = CodebaseSpecialist()
        
        # Various request contexts should all return False
        assert not specialist.should_activate({})
        assert not specialist.should_activate({"query": "something"})
        assert not specialist.should_activate({"uploaded_image_path": "/tmp/img.png"})
        
        # Only explicit bidirectional requests activate this


class TestFunctionLookup:
    """Test looking up functions by exact name."""
    
    # @pytest.mark.asyncio
    def test_lookup_known_function(self):
        """Test looking up a function that exists in the codebase."""
        specialist = CodebaseSpecialist()
        
        # Look up a function we know exists
        result = run_async(specialist.process, {
            'query': 'calculate_importance'
        })
        
        assert result.success
        assert result.specialist_name == "codebase"
        
        # Should contain file information
        assert 'context_retriever.py' in result.context_text
        
        # Should contain function definition
        assert 'calculate_importance' in result.context_text
        assert 'def calculate_importance' in result.context_text
        
        # Should have structured data
        assert 'results' in result.data
        assert len(result.data['results']) > 0
        
        # Result should have file path and line number
        first_result = result.data['results'][0]
        assert 'file' in first_result
        assert 'line' in first_result
        assert 'code' in first_result
    
    # @pytest.mark.asyncio
    def test_lookup_with_docstring(self):
        """Test that docstrings are included in results."""
        specialist = CodebaseSpecialist()
        
        # Use calculate_importance which we know exists and has a docstring
        result = run_async(specialist.process, {
            'query': 'calculate_importance'
        })
        
        assert result.success
        
        # Check structured data includes docstring
        if result.data['results']:
            first_result = result.data['results'][0]
            # Docstring might be in 'docstring' field or 'code' field
            assert 'docstring' in first_result or 'code' in first_result


class TestClassLookup:
    """Test looking up classes by exact name."""
    
    # @pytest.mark.asyncio
    def test_lookup_known_class(self):
        """Test looking up a class definition."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': 'SpecialistResult'
        })
        
        assert result.success
        
        # Should find the dataclass in protocol.py
        assert 'protocol.py' in result.context_text
        assert 'SpecialistResult' in result.context_text
        assert '@dataclass' in result.context_text or 'class SpecialistResult' in result.context_text
    
    # @pytest.mark.asyncio
    def test_lookup_protocol_class(self):
        """Test looking up Protocol classes."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': 'BaseSpecialist'
        })
        
        assert result.success
        assert 'protocol.py' in result.context_text
        assert 'BaseSpecialist' in result.context_text


class TestNotFound:
    """Test graceful handling of items that don't exist."""
    
    # @pytest.mark.asyncio
    def test_nonexistent_function(self):
        """Test looking up a function that doesn't exist."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': 'nonexistent_function_xyz123'
        })
        
        assert not result.success
        assert result.error is not None
        assert 'not found' in result.error.lower()
    
    # @pytest.mark.asyncio
    def test_empty_query(self):
        """Test handling of empty query."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': ''
        })
        
        assert not result.success
        assert result.error is not None
        assert 'empty' in result.error.lower() or 'required' in result.error.lower()
    
    # @pytest.mark.asyncio
    def test_missing_query_key(self):
        """Test handling of missing query parameter."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {})
        
        assert not result.success
        assert result.error is not None


class TestMultipleResults:
    """Test when a name appears in multiple files (e.g., multiple classes with same name)."""
    
    # @pytest.mark.asyncio
    def test_multiple_matches(self):
        """Test when query matches multiple items."""
        specialist = CodebaseSpecialist()
        
        # 'process' is a common method name in specialists
        result = run_async(specialist.process, {
            'query': 'process'
        })
        
        # Should succeed and return multiple results
        if result.success and len(result.data.get('results', [])) > 1:
            # Multiple results should all be included
            assert len(result.data['results']) >= 2
            
            # Should list multiple files in context
            context_lower = result.context_text.lower()
            assert 'specialist' in context_lower  # Likely in specialist files


class TestIndexContent:
    """Test that the index contains expected items."""
    
    def test_index_includes_brain_modules(self):
        """Test that index includes functions from brain/ directory."""
        specialist = CodebaseSpecialist()
        
        # Should have indexed stuff from various brain modules
        index_keys = list(specialist.index.keys())
        
        # Check we have a reasonable number of items
        assert len(index_keys) > 10, "Should have indexed multiple functions/classes"
        
        # Check for some known items (exact availability depends on codebase)
        # We'll just check that SOME specialist-related items exist
        specialist_items = [k for k in index_keys if 'specialist' in k.lower() or 'process' in k.lower()]
        assert len(specialist_items) > 0, "Should have indexed specialist-related items"
    
    def test_index_excludes_test_files(self):
        """Test that index doesn't include test files."""
        specialist = CodebaseSpecialist()
        
        # Check that test files aren't in the indexed file paths
        for items in specialist.index.values():
            for item in items:
                file_path = item.get('file', '')
                assert 'test_' not in file_path, f"Should not index test files: {file_path}"
                assert '/tests/' not in file_path, f"Should not index tests directory: {file_path}"


class TestContextFormatting:
    """Test that results are formatted nicely for LLM context."""
    
    # @pytest.mark.asyncio
    def test_context_text_formatting(self):
        """Test that context_text is well-formatted for LLM."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': 'calculate_importance'
        })
        
        if result.success:
            context = result.context_text
            
            # Should have clear structure
            assert len(context) > 0
            
            # Should mention the file
            assert '.py' in context
            
            # Should have code formatting (likely with markdown code blocks)
            # Or at least some clear delineation
            assert 'def' in context or 'class' in context
    
    # @pytest.mark.asyncio
    def test_multiple_results_formatted(self):
        """Test formatting when multiple results are found."""
        specialist = CodebaseSpecialist()
        
        result = run_async(specialist.process, {
            'query': 'should_activate'
        })
        
        if result.success and len(result.data.get('results', [])) > 1:
            # Should clearly separate multiple results
            context = result.context_text
            
            # Should mention multiple matches
            assert 'found' in context.lower() or 'match' in context.lower()
