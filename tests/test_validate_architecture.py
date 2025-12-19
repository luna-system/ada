#!/usr/bin/env python3
"""Quick test of validate_architecture MCP tool.

Tests Ada introspecting Ada - validating architecture changes.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "ada-mcp" / "src"))
sys.path.insert(0, str(repo_root / "ada-client" / "src"))

from ada_mcp.tools.validate_architecture import validate_architecture


async def test_validation():
    """Test the validation tool with real examples."""
    
    print("🔮 GHOST WORLD: Ada Introspecting Ada\n")
    print("=" * 60)
    
    # Test 1: Validate a new specialist
    print("\n📝 Test 1: New Specialist Validation")
    print("-" * 60)
    
    result = await validate_architecture(
        file_path="brain/specialists/ghost_specialist.py",
        change_description="Added new specialist for ghost world manifestation",
        changed_code="""
class GhostSpecialist(BaseSpecialist):
    def should_activate(self, context):
        return "ghost" in context.get("query", "").lower()
    
    async def process(self, context):
        return SpecialistResult(
            content="Ghost world manifesting...",
            priority=SpecialistPriority.HIGH
        )
"""
    )
    
    print(f"✨ Result:\n{result.content}\n")
    print(f"⚡ Speed: {result.metadata.get('time_ms', '?')}ms")
    print(f"✅ Valid: {result.metadata.get('valid', False)}")
    
    # Test 2: Trivial change (should be fast-pathed)
    print("\n\n📝 Test 2: Trivial Change (Fast Path)")
    print("-" * 60)
    
    result = await validate_architecture(
        file_path="brain/app.py",
        change_description="Fixed typo in comment",
    )
    
    print(f"✨ Result:\n{result.content}\n")
    print(f"⚡ Speed: {result.metadata.get('time_ms', '?')}ms (should be <10ms)")
    
    # Test 3: Documentation update
    print("\n\n📝 Test 3: Documentation Update")
    print("-" * 60)
    
    result = await validate_architecture(
        file_path=".ai/codebase-map.json",
        change_description="Added new module entry for ghost_specialist",
        check_types=["conventions", "placement"]
    )
    
    print(f"✨ Result:\n{result.content}\n")
    print(f"⚡ Speed: {result.metadata.get('time_ms', '?')}ms")
    
    print("\n" + "=" * 60)
    print("✨ Ghost World Test Complete!")
    print("\nAda is now capable of introspecting Ada. 👻🌍")


if __name__ == "__main__":
    asyncio.run(test_validation())
