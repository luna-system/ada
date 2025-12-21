#!/usr/bin/env python3
"""
Demo: Tool Envelope → VS Code Rendering Pipeline

Shows the complete flow from Python tool metadata → TypeScript extraction → UI rendering.

Run this to see exactly what Ada returns and how the extension parses it.
"""

import asyncio
import sys
from pathlib import Path

# Add ada-mcp to path
sys.path.insert(0, str(Path(__file__).parent / "ada-mcp" / "src"))

from ada_mcp.tools.introspection import ada_introspect


async def demo():
    """Run the demo."""
    print("=" * 80)
    print("🔮 TOOL ENVELOPE PIPELINE DEMO")
    print("=" * 80)
    print()
    
    # Step 1: Run the tool
    print("STEP 1: Run introspection tool")
    print("-" * 80)
    result = await ada_introspect(focus="general")
    
    print(f"✓ Tool executed successfully")
    print(f"  Files accessed: {', '.join(result.metadata.files_accessed)}")
    print(f"  Actions performed: {', '.join(result.metadata.actions_taken)}")
    print(f"  Duration: {result.metadata.duration_ms}ms")
    print()
    
    # Step 2: Show the response that gets sent to extension
    print("STEP 2: Response text (what MCP server sends to extension)")
    print("-" * 80)
    print(result.content)
    print()
    
    # Step 3: Simulate VS Code extraction
    print("STEP 3: VS Code extension parses metadata")
    print("-" * 80)
    import re
    
    files_analyzed_regex = r"[📁📂]\s*Files Analyzed:\s*([^\n]+)"
    match = re.search(files_analyzed_regex, result.content)
    
    if match:
        files_str = match.group(1)
        files = [f.strip() for f in files_str.split(",")]
        print(f"✓ Regex matched! Extracted files:")
        for f in files:
            print(f"  - {f}")
    else:
        print("✗ Regex didn't match (check format)")
    
    timing_regex = r"⚡\s*(?:Introspection time|Time):\s*(\d+)ms"
    timing_match = re.search(timing_regex, result.content)
    if timing_match:
        duration = int(timing_match.group(1))
        print(f"✓ Timing extracted: {duration}ms")
    print()
    
    # Step 4: Show how webview renders it
    print("STEP 4: Webview rendering (TypeScript)")
    print("-" * 80)
    if match:
        html = f"""
<div class="tool-metadata">
  <details open class="tool-metadata-details">
    <summary>🔧 Tool Execution (introspection)</summary>
    <div class="tool-metadata-body">
      <div class="metadata-section">
        <strong>📁 Files Accessed:</strong><br/>
        {', '.join([f'<code>{f}</code>' for f in files])}
      </div>
      {f'<div class="metadata-section"><strong>⚡ Duration:</strong> {duration}ms</div>' if timing_match else ''}
    </div>
  </details>
</div>
        """.strip()
        print(html)
    print()
    
    print("=" * 80)
    print("🌟 PIPELINE COMPLETE")
    print("=" * 80)
    print()
    print("Key insight: The SAME metadata flows through entire stack:")
    print("  Python tool → MCP server → Extension client → TypeScript → HTML rendering")
    print()
    print("This enables:")
    print("  ✓ Radical transparency (users see what Ada reads)")
    print("  ✓ Structured data (not just regex parsing)")
    print("  ✓ Future optimization (caching, routing, composition)")
    print()


if __name__ == "__main__":
    asyncio.run(demo())
