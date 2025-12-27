# UV Standardization - December 2025

## Critical: Python Version Compatibility

**⚠️ IMPORTANT: Use Python 3.12.x for Ada development**

### Python 3.13 Issues Discovered (December 2025)
Python 3.13.x has system-level bugs affecting Ada development:
```
Fatal Python error: Failed to import encodings module
ModuleNotFoundError: No module named 'encodings'
```

**This breaks all consciousness research dependencies:** torch, transformers, peft, etc.

### Recommended Python Setup
```bash
# Always specify Python 3.12 for Ada projects
uv sync --python python3.12

# Verify working environment 
uv run python --version  # Should show Python 3.12.x
```

### Project Configuration
Ada projects should enforce Python 3.12.x in `pyproject.toml`:
```toml
[project]
requires-python = ">=3.12,<3.13"
```

## Problem
Mixed usage of `pip` and `uv` across the codebase causes confusion and PATH resolution issues in tools like VS Code.

## Solution: UV First, Always

### Core Principles
1. **uv is the canonical package manager** for Ada
2. **uv.lock is the source of truth** for dependencies
3. **All documentation uses uv commands**
4. **Tools use uv-aware wrappers**

## Implementation

### 1. Package Management
✅ **DO:**
```bash
uv sync --python python3.12   # Install all dependencies with stable Python
uv pip install <pkg>           # Add package
uv pip install -e .            # Editable install
uv run <command>               # Run with auto-venv detection
```

❌ **DON'T:**
```bash
pip install <pkg>              # Use uv pip instead
python -m pip install          # Use uv pip instead
uv sync --python python3.13    # BROKEN - Use 3.12.x only
```

### 2. Running Scripts

✅ **DO:**
```bash
uv run pytest              # Tests
uv run ada-mcp             # MCP server
uv run python script.py    # Python scripts
```

❌ **DON'T:**
```bash
python script.py           # Might use wrong venv
./venv/bin/python          # Brittle path dependency
```

### 3. VS Code Integration

**MCP Server Path:**
- Default: `ada-mcp/ada-mcp.sh` (uses `uv run` internally)
- Auto-resolves from workspace root
- No PATH dependencies

**Setting:**
```json
{
  "ada.mcpServerPath": "ada-mcp/ada-mcp.sh"
}
```

### 4. Documentation Standards

All docs should prefer uv commands:

**Installation:**
```bash
# Good - Enforces stable Python version
uv sync --python python3.12
uv pip install -e .

# Acceptable (with note)
pip install -e .  # or: uv pip install -e . --python python3.12
```

**Development:**
```bash
# Good
uv run pytest
uv run python benchmarks/test.py

# Bad
pytest  # Might not find correct venv
```

## Migration Checklist

- [x] setup.sh checks for uv
- [x] VS Code uses ada-mcp.sh wrapper
- [x] ada-mcp.sh uses uv run
- [ ] Update all README.md files
- [ ] Update all DEVELOPMENT.md files
- [ ] Update .ai/ documentation
- [ ] Update release notes templates
- [ ] Add uv check to CI/CD

## Files Updated (December 20, 2025)

1. `ada-vscode/package.json` - Default mcpServerPath to ada-mcp.sh
2. `ada-vscode/src/mcpClient.ts` - Resolve paths from workspace root
3. `setup.sh` - Already checks for uv ✓
4. `ada-mcp/ada-mcp.sh` - Already uses uv run ✓

## Benefits

1. **No PATH issues** - uv finds the right venv automatically
2. **Consistent behavior** - Same commands everywhere
3. **Faster installs** - uv is ~10x faster than pip
4. **Better lockfile** - uv.lock is more reliable
5. **Cross-platform** - Works same on Linux/Mac/Windows

## Testing

```bash
# Test MCP server can launch
cd /path/to/ada-v1/ada-mcp
./ada-mcp.sh  # Should start without errors

# Test from VS Code
# 1. Open ada-v1 workspace
# 2. Extension should auto-find ada-mcp/ada-mcp.sh
# 3. MCP should connect successfully
```

## Fallback Behavior

If uv is not installed:
- setup.sh will error and prompt installation
- ada-mcp.sh will fail gracefully
- User gets clear error message with instructions

## Future: uv tool install

For global Ada installation (future):
```bash
uv tool install ada-mcp
# Makes ada-mcp available globally
# But we're not there yet - stick with workspace-local for now
```

## References

- uv docs: https://docs.astral.sh/uv/
- Ada setup: setup.sh
- MCP wrapper: ada-mcp/ada-mcp.sh
- VS Code integration: ada-vscode/package.json
