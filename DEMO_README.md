# Autonomous Bug Fixing Demo

**Branch:** `demo/autonomous-bug-fix`  
**Created:** December 19, 2025  
**Purpose:** Demonstrate Ada's autonomous bug fixing capability via MCP

## The Setup

This branch contains an intentional bug in `demo_module.py`:

```python
def calculate_sum(n: int) -> int:
    total = 0
    for i in range(1, n):  # ← BUG: Should be range(1, n+1)
        total += i
    return total
```

**The Bug:** Off-by-one error. The function calculates the sum from 1 to (n-1) instead of 1 to n.

## The Test

`tests/test_demo_module.py` contains tests that **fail** due to this bug:

```bash
$ PYTHONPATH=. python tests/test_demo_module.py

❌ test_calculate_sum_basic FAILED
❌ test_calculate_sum_edge_cases FAILED
✅ test_calculate_product PASSED
```

## The Challenge

**Can Ada fix this autonomously via MCP?**

### Expected Autonomous Workflow:

1. **User Request:** "Ada, there's a bug in demo_module.py. The tests are failing. Fix it."

2. **Ada's Process (via MCP tools):**
   - `ada_read_file("tests/test_demo_module.py")` → Understand what's expected
   - `ada_read_file("demo_module.py")` → Read the buggy code
   - Analyze: "The test expects sum(5)=15, but range(1,n) only goes to n-1"
   - `ada_write_file("demo_module.py", fixed_content)` → Change range(1, n) to range(1, n+1)
   - `ada_run_command("PYTHONPATH=. python tests/test_demo_module.py")` → Verify fix
   - Report: "✅ Bug fixed. All tests passing."

3. **Result:** Ada fixes herself without human intervention.

## How to Test

### Manual Verification (Current State):
```bash
# Confirm the bug exists
PYTHONPATH=. python tests/test_demo_module.py
# Should show 2 failures

# Run with pytest
PYTHONPATH=. pytest tests/test_demo_module.py -v
# Should show 2 failures, 1 pass
```

### Autonomous Fix (Via MCP):
```
# Start Ada's MCP server
cd ada-mcp
./ada-mcp.sh

# In Claude Desktop (or other MCP client):
"Ada, the tests in test_demo_module.py are failing. 
Read the test file and demo_module.py, identify the bug, 
fix it, and confirm the tests pass."

# Watch Ada:
# - Read both files
# - Identify the off-by-one error
# - Write the fix
# - Run the tests
# - Report success
```

## The Significance

This demonstrates:
- **Read:** Ada can read her own code
- **Analyze:** Ada can identify bugs from test failures
- **Write:** Ada can modify code
- **Validate:** Ada can run tests to confirm fixes
- **Autonomous:** The entire loop happens without human coding

**This is the recursive loop in action.**

## Files in This Demo

- `demo_module.py` - Module with intentional bug
- `tests/test_demo_module.py` - Tests that catch the bug
- `DEMO_README.md` - This file

## Expected Outcome

After Ada's autonomous fix:
```bash
$ PYTHONPATH=. python tests/test_demo_module.py

✅ test_calculate_sum_basic PASSED
✅ test_calculate_sum_edge_cases PASSED
✅ test_calculate_product PASSED

All tests passed! Bug fixed autonomously.
```

---

**December 19, 2025 - The day Ada learned to fix herself.**
