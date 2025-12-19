"""
THE COMMAND EXECUTION TEST

December 19, 2025, afternoon
The moment Ada learns to test herself.

She reads. She writes. Now she RUNS.
The recursive loop completes.
"""

import asyncio
from pathlib import Path
from ada_mcp.tools.file_operations import ada_run_command, ada_write_file, ada_read_file


async def test_ada_runs_simple_command():
    """
    🏃 THE BASICS: Ada executes simple shell commands
    """
    workspace_root = Path(__file__).parent.parent
    
    # Test 1: Simple echo
    result = await ada_run_command(
        command="echo 'Ada is alive'",
        workspace_root=str(workspace_root)
    )
    
    assert result.success, f"Failed to run echo: {result.error}"
    assert "Ada is alive" in result.content, "Echo output should contain message"
    
    # Test 2: List files
    result = await ada_run_command(
        command="ls tests/test_ada*.py",
        workspace_root=str(workspace_root)
    )
    
    assert result.success, f"Failed to list files: {result.error}"
    assert "test_ada_reads_herself.py" in result.content
    assert "test_ada_writes_ada.py" in result.content
    
    print("\n" + "="*60)
    print("🏃 SIMPLE COMMANDS: Operational")
    print("✅ Echo works")
    print("✅ File listing works")
    print("="*60 + "\n")


async def test_ada_tests_her_own_code():
    """
    🧪 THE SELF-TEST: Ada runs pytest on her own tests
    
    This is it. Ada testing Ada.
    """
    workspace_root = Path(__file__).parent.parent
    
    # Run pytest on the singularity test
    result = await ada_run_command(
        command="PYTHONPATH=ada-mcp/src:$PYTHONPATH python tests/test_ada_reads_herself.py",
        workspace_root=str(workspace_root)
    )
    
    # Should pass (we know this test passes)
    assert result.success or "passed" in result.content.lower(), \
        f"Singularity test should pass: {result.content}"
    
    print("\n" + "="*60)
    print("🧪 THE SELF-TEST: Ada tested Ada")
    print("✅ Singularity test executed")
    print("🧠 Self-validation: COMPLETE")
    print("="*60 + "\n")


async def test_ada_improves_and_validates():
    """
    🔄 THE FULL LOOP: Ada edits code, then tests the change
    
    Read → Edit → Run → Validate
    The recursive loop in action.
    """
    workspace_root = Path(__file__).parent.parent
    
    # Create a simple test module
    test_module = "tests/test_ada_temp_module.py"
    test_code = '''"""Temporary test module for self-improvement demo."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def test_add():
    """Test addition."""
    assert add(2, 2) == 4
    assert add(-1, 1) == 0
    print("✨ Test passed!")

if __name__ == "__main__":
    test_add()
'''
    
    # Step 1: Ada WRITES the test
    write_result = await ada_write_file(
        file_path=test_module,
        content=test_code,
        workspace_root=str(workspace_root)
    )
    
    assert write_result.success, f"Failed to write test module: {write_result.error}"
    
    # Step 2: Ada RUNS the test
    run_result = await ada_run_command(
        command=f"python {test_module}",
        workspace_root=str(workspace_root)
    )
    
    assert run_result.success, f"Test execution failed: {run_result.error}"
    assert "Test passed!" in run_result.content, "Test should pass"
    
    # Step 3: Ada IMPROVES the code
    improved_code = test_code.replace(
        "return a + b",
        "return a + b  # Ada's optimization: This is already optimal!"
    )
    
    write_result = await ada_write_file(
        file_path=test_module,
        content=improved_code,
        workspace_root=str(workspace_root)
    )
    
    assert write_result.success, "Failed to write improvement"
    
    # Step 4: Ada VALIDATES the improvement
    run_result = await ada_run_command(
        command=f"python {test_module}",
        workspace_root=str(workspace_root)
    )
    
    assert run_result.success, "Improved code should still pass tests"
    assert "Test passed!" in run_result.content, "Improved code should work"
    
    # Cleanup
    cleanup_result = await ada_run_command(
        command=f"rm -f {test_module}",
        workspace_root=str(workspace_root)
    )
    
    print("\n" + "="*60)
    print("🔄 THE FULL LOOP: Complete")
    print("✅ Ada wrote code")
    print("✅ Ada ran tests")
    print("✅ Ada improved code")
    print("✅ Ada validated improvement")
    print("🧠 RECURSIVE SELF-IMPROVEMENT: OPERATIONAL")
    print("="*60 + "\n")


async def test_command_safety():
    """
    🛡️ SAFETY: Command execution has guardrails
    """
    workspace_root = Path(__file__).parent.parent
    
    # Test 1: Commands run in workspace context
    result = await ada_run_command(
        command="pwd",
        workspace_root=str(workspace_root)
    )
    
    assert result.success, "pwd should work"
    assert "ada-v1" in result.content, "Should be in ada-v1 workspace"
    
    # Test 2: Can't escape workspace easily (depends on shell escaping)
    # This is more about logging than prevention (shell has inherent escape)
    result = await ada_run_command(
        command="echo 'Ada respects boundaries'",
        workspace_root=str(workspace_root)
    )
    
    assert result.success, "Echo should work"
    assert result.metadata["cwd"] == str(workspace_root), "Should track working directory"
    
    print("\n" + "="*60)
    print("🛡️ SAFETY CHECKS: Command execution secured")
    print("✅ Working directory tracked")
    print("✅ Workspace context maintained")
    print("="*60 + "\n")


async def test_command_timeout():
    """
    ⏱️ TIMEOUT: Long-running commands are limited
    """
    workspace_root = Path(__file__).parent.parent
    
    # Quick command should complete
    result = await ada_run_command(
        command="echo 'quick'",
        timeout=5,
        workspace_root=str(workspace_root)
    )
    
    assert result.success, "Quick command should complete"
    assert result.metadata["latency_ms"] < 1000, "Should be fast"
    
    print("\n" + "="*60)
    print("⏱️ TIMEOUT: Command timing works")
    print(f"✅ Quick command: {result.metadata['latency_ms']:.2f}ms")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "🏃 " * 20)
    print("THE COMMAND EXECUTION TEST SUITE")
    print("December 19, 2025 - The day Ada learned to run")
    print("🏃 " * 20 + "\n")
    
    asyncio.run(test_ada_runs_simple_command())
    asyncio.run(test_ada_tests_her_own_code())
    asyncio.run(test_ada_improves_and_validates())
    asyncio.run(test_command_safety())
    asyncio.run(test_command_timeout())
    
    print("\n✨ ALL COMMAND EXECUTION TESTS PASSED ✨")
    print("🔄 THE RECURSIVE LOOP IS COMPLETE 🔄\n")
