#!/usr/bin/env python3
"""Example: Ada reading her own documentation via MCP resources."""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ada_mcp.resources import RESOURCES, read_resource


async def main():
    """Demonstrate Ada introspecting her own documentation."""
    
    print("🤖 Ada MCP Resources Example\n")
    print("=" * 60)
    print("\n📚 Available Documentation Resources:\n")
    
    # List all resources
    for i, resource in enumerate(RESOURCES, 1):
        annotations = resource.model_dump().get("annotations", {})
        priority = annotations.get("priority", 0)
        
        print(f"{i}. {resource.name}")
        print(f"   URI: {resource.uri}")
        print(f"   Priority: {priority:.1f} | Type: {resource.mimeType}")
        print(f"   {resource.description}")
        print()
    
    # Example: Read architecture context
    print("=" * 60)
    print("\n📖 Example: Reading Architecture Context\n")
    
    contents = await read_resource("ada://docs/context")
    context_text = contents[0].text
    
    # Show first 500 characters
    preview = context_text[:500]
    print(preview)
    print(f"\n... ({len(context_text)} characters total)")
    
    # Example: Read codebase map
    print("\n" + "=" * 60)
    print("\n🗺️  Example: Reading Codebase Map\n")
    
    contents = await read_resource("ada://docs/codebase-map")
    codebase_map = json.loads(contents[0].text)
    
    print(f"Project: {codebase_map.get('project', 'unknown')}")
    print(f"Version: {codebase_map.get('version', 'unknown')}")
    print(f"Modules: {len(codebase_map.get('modules', {}))}")
    print("\nSample modules:")
    
    for module_name in list(codebase_map.get('modules', {}).keys())[:3]:
        module = codebase_map['modules'][module_name]
        print(f"  - {module_name}: {module.get('purpose', 'no description')}")
    
    # Use case explanation
    print("\n" + "=" * 60)
    print("\n💡 Use Case: Ada Self-Introspection\n")
    print("""
When Ada needs to understand her own architecture:

1. MCP client requests: resources/list
   → Ada responds with all documentation resources

2. MCP client requests: resources/read ada://docs/context
   → Ada returns her architecture overview

3. MCP client (or Ada herself) can now:
   - Understand module relationships
   - Locate relevant code for a task
   - Reference specialist capabilities
   - Follow conventions and patterns

This bypasses the need to parse HTML or navigate file systems.
The same protocol that connects Ada to your editor also gives
her access to her own structured documentation.
    """)
    
    print("=" * 60)
    print("\n✨ Resources provide structured, machine-readable access")
    print("   to Ada's documentation without HTML parsing overhead.\n")


if __name__ == "__main__":
    asyncio.run(main())
