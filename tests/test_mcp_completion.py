"""Test MCP server integration for code completion."""

import pytest

# Import from installed package
import ada_mcp.tools as mcp_tools_module


class TestMCPToolRegistration:
    """Test that completion tool is properly registered in MCP."""

    def test_completion_tool_registered(self):
        """Verify ada_complete_code is in TOOLS list."""
        TOOLS = mcp_tools_module.TOOLS
        tool_names = [tool.name for tool in TOOLS]
        assert "ada_complete_code" in tool_names, "Code completion tool not registered"

    def test_completion_tool_schema(self):
        """Verify tool schema is valid."""
        TOOLS = mcp_tools_module.TOOLS
        tool = next((t for t in TOOLS if t.name == "ada_complete_code"), None)
        assert tool is not None, "Tool not found"
        
        schema = tool.inputSchema
        assert schema["type"] == "object"
        assert "code_before" in schema["properties"]
        assert "code_after" in schema["properties"]
        assert "language" in schema["properties"]
        assert "max_tokens" in schema["properties"]
        assert schema["required"] == ["code_before"]

    def test_completion_tool_description(self):
        """Verify tool has helpful description."""
        TOOLS = mcp_tools_module.TOOLS
        tool = next((t for t in TOOLS if t.name == "ada_complete_code"), None)
        assert tool is not None
        assert "complete code" in tool.description.lower()
        assert "cursor" in tool.description.lower()


@pytest.mark.skip(reason="Requires running Ada brain service")
class TestMCPCompletionHandler:
    """Test the tool handler (requires Ada running)."""

    @pytest.mark.asyncio
    async def test_handler_basic_completion(self):
        """Test handler with basic completion request."""
        from ada_mcp.ada_client import AdaClient
        
        ada = AdaClient(base_url="http://localhost:8000")
        
        arguments = {
            "code_before": "def hello():\n    ",
            "code_after": "",
            "language": "python",
        }
        
        result = await mcp_tools_module.handle_tool_call("ada_complete_code", arguments, ada)
        assert len(result) > 0
        assert result[0].type == "text"
        assert len(result[0].text) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
