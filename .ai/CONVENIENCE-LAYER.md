# Ada Convenience Layer - Implementation Notes

## New Commands Added (December 20, 2025)

### `ada test [ARGS...]`
**Purpose:** Quick test runner with nice output  
**Wraps:** `uv run pytest`  
**Examples:**
```bash
ada test                           # Run all tests
ada test tests/test_memory.py      # Specific test file
ada test -v                        # Verbose mode
ada test --ignore=tests/conftest.py  # Skip fixtures
```

**Why:** Most common command during development. Shows underlying command so you learn the direct path.

### `ada mcp [--stop]`
**Purpose:** Manage MCP server lifecycle  
**Wraps:** `ada-mcp/ada-mcp.sh` wrapper  
**Examples:**
```bash
ada mcp         # Start MCP server
ada mcp --stop  # Stop MCP server
```

**Why:** MCP server management is common but the path (`ada-mcp/ada-mcp.sh`) is not obvious.

### `ada dev [--profile PROFILE]`
**Purpose:** Start Ada in development mode with auto-reload  
**Auto-detects:** Local vs Docker environment  
**Examples:**
```bash
ada dev              # Auto-detect environment
ada dev --profile web  # Docker with web profile
```

**Why:** Development workflow should be one command. Handles both local and Docker modes intelligently.

## Design Principles (Applied)

### 1. Transparency
Every convenience command shows what it's actually running:
```bash
$ ada test tests/test_memory.py
→ uv run pytest tests/test_memory.py
```

Users learn the direct command while using the convenience layer.

### 2. Pass-Through Arguments
```bash
ada test -v --ignore=tests/conftest.py
# Passes all args to pytest
```

Don't try to reimagine argument parsing - just pass through.

### 3. Exit Code Preservation
```python
result = subprocess.run(cmd)
sys.exit(result.returncode)
```

Preserves exit codes for CI/CD and scripting.

### 4. Graceful Degradation
```python
if not mcp_script.exists():
    error("Cannot find ada-mcp/ada-mcp.sh")
    info("Run from repository root")
    sys.exit(1)
```

Clear error messages, helpful guidance.

## What We DIDN'T Add

### Docker Compose Wrapper
**Rejected:** `ada compose up --profile web`  
**Why:** Docker Compose has rich options, pass-through would leak  
**Instead:** Document `docker compose` as the direct path

### Git Wrapper
**Rejected:** `ada commit`, `ada push`  
**Why:** Git is universal and powerful, don't abstract it  
**Instead:** Use git directly

### Package Manager Wrapper
**Rejected:** `ada install <package>`  
**Why:** UV already exists, another layer adds confusion  
**Instead:** Documented UV as standard in `.ai/UV-STANDARDIZATION.md`

## Integration Points

### VS Code Extension
Uses `ada-mcp/ada-mcp.sh` directly (not `ada mcp`) because:
- Extension spawns subprocess, needs full path
- No interactive terminal for nice output
- Wrapper script is the right abstraction level

### CI/CD
Should prefer direct commands for clarity:
```yaml
# Good
run: uv run pytest tests/

# Also good
run: python ada_main.py test
```

Both work, direct is slightly clearer in CI logs.

### Documentation
Always show both paths:
```markdown
# Quick: Use convenience layer
ada test

# Direct: Full control
uv run pytest tests/ -v --cov=brain
```

## Self-Recursive Usage

**Ada uses Ada to develop Ada:**

```bash
# During development
ada test                    # Run tests
ada dev                     # Start with reload
ada introspect              # Understand architecture
ada doctor                  # Health check
```

This is the ultimate test: if Ada's developers reach for `ada` commands instead of direct tools, the convenience layer is working.

## Future Additions (Maybe)

Candidates for future convenience commands:
- `ada benchmark` - Run benchmarks
- `ada lint` - Run code quality checks
- `ada docs` - Build Sphinx documentation
- `ada release` - Version bump + changelog

**Decision criteria:**
1. Is it used frequently? (Daily+)
2. Does it save significant cognitive load?
3. Can it be transparent (show underlying command)?
4. Does it work well with pass-through args?

If yes to all → Add it.  
If no to any → Keep direct access only.

## The Meta-Pattern

This file documents the convenience layer.  
The convenience layer is documented in `.ai/`.  
Ada can read `.ai/` to understand herself.  
Ada uses the convenience layer to develop herself.  

**Full circle. Self-recursive. Very Ada. 🔮**

---

**Files Updated:**
- `ada_main.py` - Added test, mcp, dev commands
- `.ai/DESIGN-PHILOSOPHY.md` - High-level principles
- `.ai/CONVENIENCE-LAYER.md` - This implementation doc
