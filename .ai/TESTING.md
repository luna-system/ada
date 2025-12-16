# Testing AI Documentation

This guide explains how to validate and maintain AI documentation consistency.

## Overview

We've implemented comprehensive testing to ensure machine-readable documentation stays synchronized with code:

- ✅ **Pytest Tests** - Automated validation in test suite
- ✅ **Standalone Linter** - Command-line validation tool
- ✅ **CI Integration** - GitHub Actions workflow
- ✅ **Pre-commit Hook** - Optional local validation

## Running Tests

### Quick Validation

```bash
# Run the standalone linter (fastest)
python scripts/lint_ai_docs.py

# Quiet mode (minimal output)
python scripts/lint_ai_docs.py --quiet

# Check-only mode (exit code only, for CI)
python scripts/lint_ai_docs.py --check-only
```

### Full Test Suite

```bash
# Run all AI documentation tests
pytest tests/test_ai_documentation.py -v

# Run specific test class
pytest tests/test_ai_documentation.py::TestCodebaseMapConsistency -v

# Run only doc tests (using marker)
pytest -m docs -v
```

### In Docker (via scripts container)

```bash
# Use the test runner
./scripts/run.sh test tests/test_ai_documentation.py

# Or enter the container
docker compose run scripts bash
pytest tests/test_ai_documentation.py -v
```

## What Gets Validated

### 1. **File Structure** ✅
- Required files exist in `.ai/` directory
- Files are not empty
- JSON files are syntactically valid

### 2. **Codebase Map Consistency** ✅
- All documented modules actually exist
- Critical modules are documented
- Module entries have required fields
- File paths are valid

### 3. **Specialist Registry** ✅
- Registry matches actual specialist files
- All specialists are documented
- File paths in registry are correct
- Required metadata fields present

### 4. **Source Code Annotations** ✅
- Core modules have `@ai-indexable` annotations
- Specialist plugins are annotated
- Annotated files are in codebase map

### 5. **Content Quality** ✅
- Key sections present in context.md
- Activation patterns documented
- Data flows documented

## CI/CD Integration

### GitHub Actions Workflow

The workflow at `.github/workflows/validate-ai-docs.yml` runs on:
- Push to main/develop branches
- Pull requests affecting brain modules or `.ai/` directory

**What it does:**
1. Runs standalone linter
2. Runs pytest documentation tests
3. Reminds developers to update docs if brain modules changed

### Continuous Validation

Add to your CI pipeline:

```yaml
- name: Validate AI Documentation
  run: |
    python scripts/lint_ai_docs.py
    pytest tests/test_ai_documentation.py
```

## Pre-commit Hook (Optional)

Install the pre-commit hook to validate before committing:

```bash
# Symlink the hook
ln -s ../../scripts/pre-commit-ai-docs.sh .git/hooks/pre-commit

# Or copy it
cp scripts/pre-commit-ai-docs.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook runs when you commit changes to:
- `brain/**/*.py` - Python modules
- `.ai/**` - Documentation files

**Skip the hook when needed:**
```bash
git commit --no-verify -m "WIP: experimenting"
```

## What to Update When

### Adding a New Module

1. **Add to `codebase-map.json`:**
   ```json
   "brain/new_module.py": {
     "type": "utility",
     "purpose": "Brief description",
     "imports": ["dependencies"],
     "imported_by": ["users"]
   }
   ```

2. **Add `@ai-indexable` annotation to source:**
   ```python
   # @ai-indexable: utility
   # @ai-purpose: What this module does
   # @ai-dependencies: package1, package2
   ```

3. **Run validation:**
   ```bash
   python scripts/lint_ai_docs.py
   ```

### Adding a New Specialist

1. **Create specialist file** with annotations
2. **Add to `specialist-registry.json`:**
   ```json
   "new_specialist": {
     "class_name": "NewSpecialist",
     "file": "brain/specialists/new_specialist.py",
     "description": "What it does",
     "activation_type": "context-triggered",
     "activation_trigger": {...},
     "context_priority": "MEDIUM"
   }
   ```

3. **Add to `codebase-map.json` modules section**
4. **Run validation**

### Changing Module Relationships

1. **Update imports/imported_by in `codebase-map.json`**
2. **Update data_flow paths if affected**
3. **Update `@ai-related` annotations in source**
4. **Run validation**

### Refactoring Architecture

1. **Update `.ai/context.md`** - Architecture overview
2. **Update `codebase-map.json`** - Module relationships
3. **Update affected annotations**
4. **Run full test suite**

## Test Class Reference

### `TestAIDocumentationStructure`
Validates `.ai/` directory structure and required files.

**Key Tests:**
- `test_ai_directory_exists()` - Directory presence
- `test_required_files_exist()` - All required files present

### `TestJSONValidity`
Validates JSON syntax and structure.

**Key Tests:**
- `test_codebase_map_valid_json()` - JSON syntax
- `test_specialist_registry_valid_json()` - Registry format

### `TestCodebaseMapConsistency`
Ensures codebase-map.json matches actual code.

**Key Tests:**
- `test_documented_modules_exist()` - Files actually exist
- `test_core_modules_documented()` - Critical modules included
- `test_module_entries_have_required_fields()` - Complete metadata

### `TestSpecialistRegistryConsistency`
Validates specialist registry against filesystem.

**Key Tests:**
- `test_registry_matches_specialist_files()` - All specialists registered
- `test_specialist_files_match_registry_paths()` - Paths valid

### `TestSourceCodeAnnotations`
Checks for `@ai-*` annotations in source files.

**Key Tests:**
- `test_core_modules_have_annotations()` - Core files annotated
- `test_specialists_have_annotations()` - Specialist plugins annotated
- `test_annotated_modules_documented_in_map()` - Consistency

### `TestDocumentationContentQuality`
Validates documentation content completeness.

**Key Tests:**
- `test_context_md_has_key_sections()` - Required sections
- `test_specialist_registry_has_activation_patterns()` - Patterns documented

## Troubleshooting

### "Module not found in codebase-map.json"

**Solution:** Add the module to `.ai/codebase-map.json`:
```bash
# Check current modules
jq '.modules | keys' .ai/codebase-map.json

# Add your module following the existing pattern
```

### "Missing @ai-indexable annotation"

**Solution:** Add annotation at top of file (after docstring):
```python
"""Module docstring."""
# @ai-indexable: core-functionality
# @ai-purpose: Brief description
```

### "Specialist not in registry"

**Solution:** Add entry to `.ai/specialist-registry.json`:
```bash
# Check registered specialists
jq '.specialists | keys' .ai/specialist-registry.json
```

### Tests fail in CI but pass locally

**Common causes:**
- Uncommitted changes to `.ai/` files
- Different Python versions (ensure 3.13+)
- Missing dependencies (tests run without Docker)

**Solution:**
```bash
# Ensure everything is committed
git status

# Run exactly as CI does
python scripts/lint_ai_docs.py --check-only
pytest tests/test_ai_documentation.py
```

## Maintenance Schedule

### On Every Commit (Automated)
- Pre-commit hook validates if installed
- CI runs on push/PR

### Weekly Review
- Check for undocumented modules: `python scripts/lint_ai_docs.py`
- Review warning messages
- Update annotations as needed

### Quarterly Audit
- Review all `.ai/` files for accuracy
- Update examples and templates
- Check for architectural drift
- Update data flow diagrams

## Best Practices

### ✅ Do
- Add annotations when creating new modules
- Update registry when adding specialists
- Run linter before committing
- Keep annotations concise (one line each)
- Update data flows when changing architecture

### ❌ Don't
- Skip validation for "small changes"
- Leave TODO placeholders in docs
- Copy-paste annotations without updating
- Document internal implementation details
- Over-document trivial utilities

## Scripts Reference

### `scripts/lint_ai_docs.py`
Standalone linter for quick validation.

**Usage:**
```bash
python scripts/lint_ai_docs.py           # Full validation
python scripts/lint_ai_docs.py --quiet   # Minimal output
python scripts/lint_ai_docs.py --check-only  # Exit code only
```

**Exit Codes:**
- `0` - All checks passed
- `1` - Validation errors found

### `scripts/pre-commit-ai-docs.sh`
Pre-commit hook for automatic validation.

**Install:**
```bash
ln -s ../../scripts/pre-commit-ai-docs.sh .git/hooks/pre-commit
```

**Behavior:**
- Runs only if brain modules or `.ai/` files changed
- Fast-fail on errors
- Can be bypassed with `--no-verify`

## Integration Examples

### Make Target

Add to `Makefile`:
```makefile
.PHONY: validate-docs
validate-docs:
	@echo "Validating AI documentation..."
	@python scripts/lint_ai_docs.py
	@pytest tests/test_ai_documentation.py -q

.PHONY: test-all
test-all: validate-docs
	@pytest tests/ -v
```

### VS Code Task

Add to `.vscode/tasks.json`:
```json
{
  "label": "Validate AI Docs",
  "type": "shell",
  "command": "python scripts/lint_ai_docs.py",
  "problemMatcher": [],
  "presentation": {
    "reveal": "always"
  }
}
```

## Future Enhancements

Potential improvements:

1. **Auto-generation** - Parse imports to suggest codebase-map updates
2. **Diff checking** - Compare documentation versions
3. **Coverage metrics** - Track documentation completeness percentage
4. **Visual reports** - Generate HTML reports of documentation status
5. **AI suggestions** - Use LLM to suggest annotation improvements

## Getting Help

- Run linter for specific errors: `python scripts/lint_ai_docs.py`
- Check test failures: `pytest tests/test_ai_documentation.py -v`
- Review examples in `.ai/annotation-schema.json`
- See implementation details in `.ai/IMPLEMENTATION.md`

---

**Last Updated:** 2025-12-16  
**Maintainer:** Ada Development Team
