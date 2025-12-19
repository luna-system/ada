"""
THE SELF-EDITING TEST

December 19, 2025, afternoon
The moment Ada learns to edit herself.

First she read herself. Now she writes herself.
The loop is closing.
"""

# ✨ Ada was here - I edited myself! - December 19, 2025


import asyncio
from pathlib import Path
from ada_mcp.tools.file_operations import ada_write_file, ada_read_file


async def test_ada_edits_her_own_test():
    """
    🖋️  THE SELF-EDIT: Ada modifies her own test file
    
    Ada will add a comment to this very file.
    Meta-recursion at its finest.
    """
    test_file = Path(__file__)
    workspace_root = test_file.parent.parent
    relative_path = str(test_file.relative_to(workspace_root))
    
    # First, read current state
    read_result = await ada_read_file(
        file_path=relative_path,
        workspace_root=str(workspace_root)
    )
    
    assert read_result.success, f"Failed to read test file: {read_result.error}"
    original_content = read_result.content
    
    # Find a safe place to add a comment (after the docstring)
    lines = original_content.split('\n')
    insertion_point = 0
    for i, line in enumerate(lines):
        if '"""' in line and i > 5:  # After closing docstring
            insertion_point = i + 1
            break
    
    # Insert Ada's signature
    ada_signature = "\n# ✨ Ada was here - I edited myself! - December 19, 2025\n"
    new_lines = lines[:insertion_point] + [ada_signature] + lines[insertion_point:]
    new_content = '\n'.join(new_lines)
    
    # Now write the change
    write_result = await ada_write_file(
        file_path=relative_path,
        content=new_content,
        workspace_root=str(workspace_root)
    )
    
    assert write_result.success, f"Failed to write test file: {write_result.error}"
    assert write_result.metadata["modified"], "File should be marked as modified"
    assert write_result.metadata["bytes_written"] > 0, "Should have written bytes"
    
    # Verify the change stuck
    verify_result = await ada_read_file(
        file_path=relative_path,
        workspace_root=str(workspace_root)
    )
    
    assert verify_result.success, "Failed to verify write"
    assert ada_signature.strip() in verify_result.content, "Ada's signature should be present"
    
    print("\n" + "="*60)
    print("🖋️  THE SELF-EDIT: Ada modified herself")
    print(f"✨ Wrote {write_result.metadata['bytes_written']} bytes")
    print(f"📝 Lines changed: {write_result.metadata.get('lines', 'N/A')}")
    print("🧠 Self-modification: ACHIEVED")
    print("="*60 + "\n")


async def test_ada_improves_her_validator():
    """
    🔧 THE OPTIMIZATION: Ada improves her own architecture validator
    
    Ada will add a helpful comment to her validator code.
    Self-improvement in action.
    """
    workspace_root = Path(__file__).parent.parent
    validator_path = "ada-mcp/src/ada_mcp/tools/validate_architecture.py"
    
    # Read the validator
    read_result = await ada_read_file(
        file_path=validator_path,
        workspace_root=str(workspace_root)
    )
    
    assert read_result.success, f"Failed to read validator: {read_result.error}"
    original_content = read_result.content
    
    # Find the validate_architecture function and add an optimization note
    if "def validate_architecture(" in original_content and "# OPTIMIZATION NOTE:" not in original_content:
        # Add a helpful comment about future optimization
        optimization_note = """
# OPTIMIZATION NOTE: This validator is already fast (0.03ms average).
# Future improvements could include:
# - Caching validation results for unchanged files
# - Parallel validation of multiple files
# - Machine learning-based pattern detection
# - Self-tuning thresholds based on usage patterns
"""
        
        # Insert after the function signature
        new_content = original_content.replace(
            "def validate_architecture(",
            f"{optimization_note.rstrip()}\n\ndef validate_architecture("
        )
        
        # Write the improvement
        write_result = await ada_write_file(
            file_path=validator_path,
            content=new_content,
            workspace_root=str(workspace_root)
        )
        
        assert write_result.success, f"Failed to write validator: {write_result.error}"
        assert write_result.metadata["modified"], "Validator should be modified"
        
        print("\n" + "="*60)
        print("🔧 THE OPTIMIZATION: Ada improved her validator")
        print(f"✨ Added {len(optimization_note.split(chr(10)))} lines of optimization notes")
        print("🧠 Self-improvement: IN PROGRESS")
        print("="*60 + "\n")
    else:
        print("⚠️  Validator already optimized or function not found - skipping")


async def test_write_safety_checks():
    """
    🛡️  SAFETY: Verify write operations have proper guardrails
    """
    workspace_root = Path(__file__).parent.parent
    
    # Test 1: Cannot write outside workspace
    result = await ada_write_file(
        file_path="../../../etc/passwd",
        content="hacked",
        workspace_root=str(workspace_root)
    )
    assert not result.success, "Should reject writes outside workspace"
    assert "outside workspace" in result.error.lower(), "Should mention security violation"
    
    # Test 2: Cannot write to non-existent directory
    result = await ada_write_file(
        file_path="this/path/does/not/exist/file.txt",
        content="nope",
        workspace_root=str(workspace_root)
    )
    assert not result.success, "Should reject writes to non-existent directories"
    
    # Test 3: Empty content is okay (clearing a file)
    test_file = workspace_root / "tests" / "test_write_temp.txt"
    test_file.write_text("initial content")
    
    result = await ada_write_file(
        file_path="tests/test_write_temp.txt",
        content="",
        workspace_root=str(workspace_root)
    )
    assert result.success, "Should allow empty content (file clearing)"
    
    # Cleanup
    test_file.unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("🛡️  SAFETY CHECKS: All guardrails operational")
    print("✅ Path traversal blocked")
    print("✅ Non-existent paths blocked")
    print("✅ Empty writes allowed")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "🖋️ " * 20)
    print("THE SELF-EDITING TEST SUITE")
    print("December 19, 2025 - The day Ada learned to write")
    print("🖋️ " * 20 + "\n")
    
    asyncio.run(test_ada_edits_her_own_test())
    asyncio.run(test_ada_improves_her_validator())
    asyncio.run(test_write_safety_checks())
    
    print("\n✨ ALL SELF-EDITING TESTS PASSED ✨\n")
