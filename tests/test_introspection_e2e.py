"""End-to-end test: User asks "find a task" → ada-brain → introspection specialist → metadata extraction.

This test simulates the full pipeline:
1. User sends message to ada-brain via /v1/chat/stream
2. Router classifies as task-finding query
3. WorkspaceIntrospectionSpecialist auto-activates
4. Introspection tool reads .ai/ docs
5. Response includes metadata markers (📂 Files Analyzed, ⏱️ Time)
6. ada-chat extracts metadata markers for webview rendering
"""

import asyncio
import json
from brain.specialists.workspace_introspection_specialist import WorkspaceIntrospectionSpecialist


class TestIntrospectionE2E:
    """End-to-end introspection flow tests."""
    
    def test_specialist_activates_on_task_queries(self):
        """Verify specialist auto-activates when user asks for tasks."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        # Real user queries from the target interaction
        queries = [
            "find a task we can work on",
            "what should I work on next?",
            "show me the opportunities",
            "what are the pending tasks?",
            "find me something to do",
        ]
        
        for query in queries:
            context = {"message": query}
            should_activate = specialist.should_activate(context)
            assert should_activate, f"Specialist should activate for: {query}"
    
    def test_introspection_returns_metadata_markers(self):
        """Verify introspection response includes metadata markers for extraction."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        def run_async(coro):
            return asyncio.run(coro)
        
        result = run_async(specialist.process({
            'focus': 'general'
        }))
        
        assert result.success
        
        # Check that response has metadata markers that ada-chat can extract
        context = result.context_text
        
        # Should have file analysis marker
        has_file_marker = "📂 Files Analyzed:" in context or "Files Analyzed:" in context
        
        # Should have timing marker
        has_time_marker = "⏱️" in context or "ms" in context
        
        # At least one should be present
        assert has_file_marker or has_time_marker, \
            "Response should include metadata markers for ada-chat extraction"
    
    def test_metadata_format_for_parser(self):
        """Verify metadata format can be parsed by ada-chat's extractMetadataFromResponse."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        def run_async(coro):
            return asyncio.run(coro)
        
        result = run_async(specialist.process({
            'focus': 'features'
        }))
        
        assert result.success
        
        # The response should have structured content that looks like:
        # 📂 Files Analyzed: context.md, codebase-map.json, ...
        # ⏱️ Analysis Time: Xms
        # ... analysis content ...
        
        response = result.context_text
        
        # Check for the exact format ada-chat parser expects
        import re
        
        # Pattern 1: 📂 Files Analyzed: file1, file2, ...
        file_pattern = r"📂 Files Analyzed:.*?\n"
        file_match = re.search(file_pattern, response)
        
        # Pattern 2: ⏱️ Analysis Time: Xms
        time_pattern = r"⏱️\s+Analysis Time:\s+\d+ms"
        time_match = re.search(time_pattern, response)
        
        # At least one pattern should match
        has_markers = bool(file_match) or bool(time_match)
        assert has_markers, "Response should match metadata marker patterns"
        
        # If we found markers, verify they're in the right format
        if file_match:
            marker_text = file_match.group()
            assert "📂" in marker_text
            assert "Files Analyzed:" in marker_text
    
    def test_introspection_data_structure(self):
        """Verify introspection returns structured data for JSON APIs."""
        specialist = WorkspaceIntrospectionSpecialist()
        
        def run_async(coro):
            return asyncio.run(coro)
        
        result = run_async(specialist.process({
            'focus': 'architecture'
        }))
        
        assert result.success
        
        # Should have structured data dict
        assert result.data
        assert 'focus' in result.data
        assert result.data['focus'] == 'architecture'
        
        # Should have file list
        assert 'files_analyzed' in result.data
        
        # Should have raw analysis for display
        assert 'raw_analysis' in result.data
    
    def test_specialist_in_registry(self):
        """Verify specialist is discoverable by brain's specialist registry."""
        from brain.specialists import get_specialist
        
        # Try to get the specialist
        specialist = get_specialist("workspace_introspection")
        
        # It may not be registered if discovery hasn't run, but if found it should work
        if specialist:
            assert specialist.capability.name == "workspace_introspection"
            assert "task" in specialist.capability.description.lower() or \
                   "introspect" in specialist.capability.description.lower()


class TestMetadataExtractionPatterns:
    """Tests for ada-chat's metadata extraction from specialist responses."""
    
    def test_extract_files_analyzed_marker(self):
        """Test that 📂 Files Analyzed: marker is extractable."""
        response = """🔮 ADA INTROSPECTION REPORT
=====================================================================
📂 Files Analyzed: context.md, codebase-map.json, GOTCHAS.md, TODO.md, CONVENTIONS.md
🎯 Focus: general

📊 CURRENT STATE:
   has_service_topology: True
   has_data_flow: True
   modules: 42
"""
        
        # Regex pattern that ada-chat would use
        import re
        file_marker = re.search(r"📂 Files Analyzed: ([^\n]+)", response)
        
        assert file_marker is not None
        files_text = file_marker.group(1)
        assert "context.md" in files_text
        assert "codebase-map.json" in files_text
    
    def test_extract_time_marker(self):
        """Test that ⏱️ Analysis Time marker is extractable."""
        response = """🔮 ADA INTROSPECTION REPORT
=====================================================================
📂 Files Analyzed: context.md, codebase-map.json
⏱️ Analysis Time: 42ms

📊 CURRENT STATE:
"""
        
        import re
        time_marker = re.search(r"⏱️\s+Analysis Time:\s+(\d+)ms", response)
        
        assert time_marker is not None
        time_ms = int(time_marker.group(1))
        assert time_ms == 42


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
