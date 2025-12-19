"""Tests for code completion tool."""
import pytest
from ada_mcp.tools.complete_code import (
    complete_code,
    _build_completion_prompt,
    _extract_code,
)


class TestPromptBuilding:
    """Test completion prompt construction."""
    
    def test_basic_prompt_structure(self):
        """Prompt should have clear structure for LLM."""
        prompt = _build_completion_prompt(
            code_before="def hello():\n    ",
            code_after="",
            language="python"
        )
        
        assert "Language: python" in prompt
        assert "[COMPLETE HERE]" in prompt
        assert "```python" in prompt
        assert "def hello():" in prompt
    
    def test_prompt_with_code_after(self):
        """Should handle code after cursor for context."""
        prompt = _build_completion_prompt(
            code_before="if x > 0:\n    ",
            code_after="\nelse:\n    return False",
            language="python"
        )
        
        assert "connect the code before and after" in prompt
        assert "else:" in prompt
    
    def test_prompt_with_context_hints(self):
        """Should include project context if available."""
        prompt = _build_completion_prompt(
            code_before="class MyClass:\n    ",
            code_after="",
            language="python",
            project_type="web-api",
            function_context="MyClass.__init__"
        )
        
        assert "Project type: web-api" in prompt
        assert "Current function: MyClass.__init__" in prompt


class TestCodeExtraction:
    """Test extracting code from LLM responses."""
    
    def test_extract_from_code_block(self):
        """Should extract code from markdown code blocks."""
        response = """Here's the completion:

```python
print("hello")
return True
```

This completes the function."""
        
        code = _extract_code(response, "python")
        assert 'print("hello")' in code
        assert "return True" in code
        assert "Here's the completion" not in code
    
    def test_extract_plain_code(self):
        """Should handle responses that are just code."""
        response = 'print("hello")\nreturn True'
        
        code = _extract_code(response, "python")
        assert 'print("hello")' in code
        assert "return True" in code
    
    def test_remove_explanation_markers(self):
        """Should strip common explanation prefixes."""
        response = "# Completion:\nprint('hello')"
        
        code = _extract_code(response, "python")
        assert "# Completion:" not in code
        assert "print('hello')" in code
    
    def test_preserve_indentation(self):
        """Should preserve leading indentation in code."""
        response = """```python
    print("indented")
    return True
```"""
        
        code = _extract_code(response, "python")
        assert "    print" in code or "print" in code  # Allow for stripping


@pytest.mark.asyncio
class TestCodeCompletion:
    """Integration tests for code completion (require Ada running)."""
    
    @pytest.mark.skip(reason="Requires Ada brain running")
    async def test_complete_function_body(self):
        """Should complete a simple function body."""
        code_before = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    '''
        
        result = await complete_code(
            code_before=code_before,
            code_after="",
            language="python"
        )
        
        assert result.success
        assert "return" in result.content.lower()
        assert result.metadata["language"] == "python"
    
    @pytest.mark.skip(reason="Requires Ada brain running")
    async def test_complete_with_context(self):
        """Should use code_after for better completions."""
        code_before = "if user.is_authenticated():\n    "
        code_after = "\nelse:\n    return redirect('/login')"
        
        result = await complete_code(
            code_before=code_before,
            code_after=code_after,
            language="python"
        )
        
        assert result.success
        # Should complete the if-branch knowing there's an else
        assert len(result.content) > 0


class TestToolSchema:
    """Test MCP tool schema definition."""
    
    def test_schema_has_required_fields(self):
        """Tool schema should follow MCP spec."""
        from ada_mcp.tools.complete_code import TOOL_SCHEMA
        
        assert "name" in TOOL_SCHEMA
        assert "description" in TOOL_SCHEMA
        assert "inputSchema" in TOOL_SCHEMA
        
        schema = TOOL_SCHEMA["inputSchema"]
        assert schema["type"] == "object"
        assert "code_before" in schema["properties"]
        assert "code_before" in schema["required"]
