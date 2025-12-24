"""Unit tests for tool request parser.

Tests parsing TOOL_REQUEST[...] patterns from LLM output.
"""

import pytest
from brain.reasoning.tool_parser import ToolRequestParser, ToolRequest


class TestToolRequestParser:
    """Test parsing TOOL_REQUEST[...] from LLM output."""
    
    def test_parse_single_request(self):
        """Can parse a single tool request."""
        parser = ToolRequestParser()
        
        text = 'I need to search. TOOL_REQUEST[ada_search:{"query":"authentication"}]'
        requests = parser.parse(text)
        
        assert len(requests) == 1
        assert requests[0].tool_name == "ada_search"
        assert requests[0].params == {"query": "authentication"}
    
    def test_parse_multiple_requests(self):
        """Can parse multiple tool requests in one output."""
        parser = ToolRequestParser()
        
        text = '''
        First I'll search: TOOL_REQUEST[ada_search:{"query":"auth"}]
        Then read the file: TOOL_REQUEST[ada_read_file:{"path":"auth.ts"}]
        '''
        
        requests = parser.parse(text)
        
        assert len(requests) == 2
        assert requests[0].tool_name == "ada_search"
        assert requests[1].tool_name == "ada_read_file"
        assert requests[1].params == {"path": "auth.ts"}
    
    def test_parse_with_complex_params(self):
        """Can parse tool requests with complex parameters."""
        parser = ToolRequestParser()
        
        text = 'TOOL_REQUEST[ada_search:{"query":"test","scope":"src/","limit":10}]'
        requests = parser.parse(text)
        
        assert len(requests) == 1
        assert requests[0].params["query"] == "test"
        assert requests[0].params["scope"] == "src/"
        assert requests[0].params["limit"] == 10
    
    def test_parse_no_requests(self):
        """Returns empty list when no requests found."""
        parser = ToolRequestParser()
        
        text = "Just some regular text with no tool requests."
        requests = parser.parse(text)
        
        assert len(requests) == 0
    
    def test_has_tool_requests_detection(self):
        """Quick check for presence of tool requests."""
        parser = ToolRequestParser()
        
        assert parser.has_tool_requests("TOOL_REQUEST[ada_search:{}]") is True
        assert parser.has_tool_requests("No requests here") is False
    
    def test_remove_tool_requests(self):
        """Can clean tool requests from text."""
        parser = ToolRequestParser()
        
        text = 'Before TOOL_REQUEST[ada_search:{"q":"test"}] after'
        cleaned = parser.remove_tool_requests(text)
        
        assert "TOOL_REQUEST" not in cleaned
        assert "Before" in cleaned
        assert "after" in cleaned
    
    def test_validate_against_available_tools(self):
        """Only accepts requests for available tools."""
        parser = ToolRequestParser(available_tools=["ada_search", "ada_read_file"])
        
        text = '''
        TOOL_REQUEST[ada_search:{"query":"test"}]
        TOOL_REQUEST[unknown_tool:{"param":"value"}]
        '''
        
        requests = parser.parse(text)
        
        # Should only parse ada_search (unknown_tool rejected)
        assert len(requests) == 1
        assert requests[0].tool_name == "ada_search"
    
    def test_invalid_json_params(self):
        """Handles invalid JSON gracefully."""
        parser = ToolRequestParser()
        
        # Malformed JSON
        text = 'TOOL_REQUEST[ada_search:{query:"test"}]'  # Missing quotes
        requests = parser.parse(text)
        
        # Should skip invalid requests
        assert len(requests) == 0
    
    def test_preserve_raw_text(self):
        """Preserves original request text."""
        parser = ToolRequestParser()
        
        text = 'TOOL_REQUEST[ada_search:{"query":"test"}]'
        requests = parser.parse(text)
        
        assert requests[0].raw_text == 'TOOL_REQUEST[ada_search:{"query":"test"}]'
    
    def test_tool_name_format(self):
        """Tool names must be lowercase with underscores."""
        parser = ToolRequestParser()
        
        # Valid format
        valid = 'TOOL_REQUEST[ada_search:{}]'
        assert len(parser.parse(valid)) == 1
        
        # Invalid formats (won't match pattern)
        invalid1 = 'TOOL_REQUEST[Ada-Search:{}]'  # Caps and dashes
        invalid2 = 'TOOL_REQUEST[adaSearch:{}]'   # camelCase
        
        assert len(parser.parse(invalid1)) == 0
        assert len(parser.parse(invalid2)) == 0
    
    def test_multiline_requests(self):
        """Can parse requests across multiple lines."""
        parser = ToolRequestParser()
        
        text = '''
        Let me search:
        TOOL_REQUEST[ada_search:{
            "query": "authentication",
            "scope": "src/"
        }]
        '''
        
        requests = parser.parse(text)
        
        assert len(requests) == 1
        assert requests[0].params["query"] == "authentication"
    
    def test_parse_with_surrounding_text(self):
        """Correctly extracts requests from verbose output."""
        parser = ToolRequestParser()
        
        text = '''
        I understand the problem. First, I need to search for authentication
        code in the codebase to understand the current implementation.
        
        TOOL_REQUEST[ada_search:{"query":"authentication middleware"}]
        
        This will help me find the relevant files and understand how
        authentication is currently handled.
        '''
        
        requests = parser.parse(text)
        
        assert len(requests) == 1
        assert requests[0].tool_name == "ada_search"
        assert "authentication middleware" in requests[0].params["query"]
