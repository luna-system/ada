"""Quick test that the new MCP tools are registered correctly."""

import sys
from pathlib import Path

# Add ada-mcp to path
ada_mcp_path = Path(__file__).parent.parent / "ada-mcp" / "src"
sys.path.insert(0, str(ada_mcp_path))

# Try importing
try:
    # Import the tools module (not the package)
    import ada_mcp
    # Get tools.py specifically
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tools_module",
        ada_mcp_path / "ada_mcp" / "tools.py"
    )
    tools_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tools_module)
    
    TOOLS = tools_module.TOOLS
    
    print(f"✅ {len(TOOLS)} tools registered successfully:\n")
    for tool in TOOLS:
        print(f"  - {tool.name}")
        if tool.name in ["ada_read_file", "ada_write_file", "ada_run_command"]:
            print(f"    🌟 NEW: {tool.description[:60]}...")
    
    print(f"\n🔄 THE RECURSIVE LOOP IS NOW IN MCP!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
