"""Integration test: verify the full transparency flow end-to-end.

The flow:
1. User asks "introspect"
2. Python tool tracks files accessed
3. MCP server embeds metadata in response
4. VS Code regex extracts badges
5. User sees transparency
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
import re


async def test_full_transparency_flow():
    """Test that metadata flows from tool → server → client format."""
    from ada_mcp.tools.introspection import ada_introspect
    from ada_mcp.tool_definitions import handle_tool_call
    from unittest.mock import AsyncMock
    from ada_mcp.ada_client import AdaClient
    
    # Step 1: Run introspection tool
    ada_root = Path.cwd()
    result = await ada_introspect(focus="general", workspace_root=str(ada_root))
    
    assert result.success
    assert result.metadata.files_accessed
    print(f"✅ Step 1: Tool tracked {len(result.metadata.files_accessed)} files")
    
    # Step 2: Server embeds metadata in response
    mock_ada = AsyncMock(spec=AdaClient)
    response_list = await handle_tool_call(
        "ada_introspect",
        {"focus": "general"},
        mock_ada
    )
    
    response_text = response_list[0].text
    print(f"✅ Step 2: Server response ({len(response_text)} chars)")
    
    # Step 3: VS Code would extract with this regex
    # From: ada-vscode/src/formatters/ToolTransparencyFormatter.ts
    files_analyzed_regex = r"[📁📂]\s*Files Analyzed:\s*([^\n]+)"
    matches = re.findall(files_analyzed_regex, response_text)
    
    if matches:
        files_str = matches[0]
        files = [f.strip() for f in files_str.split(",")]
        print(f"✅ Step 3: Regex extracted {len(files)} files: {files}")
        
        # Step 4: VS Code would create badges
        badges_html = "\n".join([
            f'<span class="tool-file-badge">{f}</span>'
            for f in files
        ])
        print(f"✅ Step 4: Would render {len(files)} badge(s) in webview")
        print(f"\nFinal HTML (sample):\n{badges_html[:200]}...")
        
        return True
    else:
        print("❌ Step 3: Regex didn't match!")
        print(f"Response text:\n{response_text[:500]}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_full_transparency_flow())
    if success:
        print("\n🌟 Full transparency flow working!")
    else:
        print("\n⚠️  Pattern matching issue - check format")
