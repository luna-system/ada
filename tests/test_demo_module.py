"""
Tests for demo_module - These tests will FAIL because of the bug.

Ada should:
1. Read this test file
2. See what's expected
3. Read demo_module.py
4. Identify the bug (off-by-one error)
5. Fix it (change range(1, n) to range(1, n+1))
6. Run the tests to verify
7. Confirm the fix worked
"""

import pytest
from demo_module import calculate_sum, calculate_product


def test_calculate_sum_basic():
    """Test basic sum calculations."""
    assert calculate_sum(1) == 1, "Sum of 1 should be 1"
    assert calculate_sum(5) == 15, "Sum 1-5 should be 15 (1+2+3+4+5)"
    assert calculate_sum(10) == 55, "Sum 1-10 should be 55"


def test_calculate_sum_edge_cases():
    """Test edge cases."""
    assert calculate_sum(0) == 0, "Sum of 0 should be 0"
    assert calculate_sum(1) == 1, "Sum of 1 should be 1"
    assert calculate_sum(100) == 5050, "Sum 1-100 should be 5050"


def test_calculate_product():
    """Test factorial calculation (this should pass - no bug here)."""
    assert calculate_product(0) == 1, "0! should be 1"
    assert calculate_product(1) == 1, "1! should be 1"
    assert calculate_product(5) == 120, "5! should be 120"
    assert calculate_product(10) == 3628800, "10! should be 3628800"


if __name__ == "__main__":
    print("Running tests manually...\n")
    
    try:
        test_calculate_sum_basic()
        print("✅ test_calculate_sum_basic PASSED")
    except AssertionError as e:
        print(f"❌ test_calculate_sum_basic FAILED: {e}")
    
    try:
        test_calculate_sum_edge_cases()
        print("✅ test_calculate_sum_edge_cases PASSED")
    except AssertionError as e:
        print(f"❌ test_calculate_sum_edge_cases FAILED: {e}")
    
    try:
        test_calculate_product()
        print("✅ test_calculate_product PASSED")
    except AssertionError as e:
        print(f"❌ test_calculate_product FAILED: {e}")
    
    print("\n" + "="*60)
    print("Expected: 2 tests fail (sum), 1 test passes (product)")
    print("="*60)
