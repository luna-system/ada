#!/usr/bin/env python3
"""Manual test for MCP code completion integration.

This script tests the full stack:
1. Ada brain running (http://localhost:8000)
2. Code completion tool
3. MCP server integration

Run with Ada brain running in the background.
"""

import asyncio
import sys
from pathlib import Path

# Add ada-mcp to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ada-mcp" / "src"))

from ada_mcp.tools.complete_code import complete_code


async def test_simple_completion():
    """Test a simple Python completion."""
    print("🧪 Testing simple Python function completion...")
    
    code_before = """def greet(name):
    message = """
    
    code_after = """
    return message"""
    
    result = await complete_code(
        code_before=code_before,
        code_after=code_after,
        language="python",
        max_tokens=50,
    )
    
    print(f"\n✨ Result:")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Completion: {repr(result.content)}")
        print(f"  Tokens used: {result.metadata.get('tokens_used', 'N/A')}")
    else:
        print(f"  Error: {result.error}")
    
    return result


async def test_class_method_completion():
    """Test completing a class method."""
    print("\n🧪 Testing class method completion...")
    
    code_before = """class Calculator:
    def add(self, a, b):
        """
    
    code_after = """
    
    def subtract(self, a, b):
        return a - b"""
    
    result = await complete_code(
        code_before=code_before,
        code_after=code_after,
        language="python",
        max_tokens=30,
    )
    
    print(f"\n✨ Result:")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Completion: {repr(result.content)}")
    else:
        print(f"  Error: {result.error}")
    
    return result


async def test_import_completion():
    """Test completing import statements."""
    print("\n🧪 Testing import completion...")
    
    code_before = "from pathlib import "
    code_after = "\n\nclass MyClass:"
    
    result = await complete_code(
        code_before=code_before,
        code_after=code_after,
        language="python",
        max_tokens=20,
    )
    
    print(f"\n✨ Result:")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Completion: {repr(result.content)}")
    else:
        print(f"  Error: {result.error}")
    
    return result


async def main():
    """Run all tests."""
    print("🤖 Ada Code Completion - Manual Test Suite")
    print("=" * 60)
    print("\nℹ️  Make sure Ada brain is running at http://localhost:8000")
    print("   Start with: docker compose up -d brain chroma ollama")
    print()
    
    try:
        results = []
        results.append(await test_simple_completion())
        results.append(await test_class_method_completion())
        results.append(await test_import_completion())
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {sum(1 for r in results if r.success)}/{len(results)} tests passed")
        
        if all(r.success for r in results):
            print("✅ All tests passed! Code completion is working! 🎉")
            return 0
        else:
            print("❌ Some tests failed. Check Ada brain status.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure Ada brain is running and accessible.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
