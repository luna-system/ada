# .ai Directory - Machine-Readable Documentation

This directory contains structured metadata for AI code analysis and understanding.

## Purpose

Enhance AI model comprehension of the codebase through:
- High-level architecture maps
- Module dependency graphs
- Structured annotations in source code
- Plugin/extension registries

## Files

### `context.md`
Human-readable architecture overview optimized for LLM consumption:
- Service topology and data flow
- Key modules and their relationships
- Extension points and conventions
- Critical paths and circular dependencies

### `codebase-map.json`
Machine-readable module metadata:
- Module purposes and key functions
- Import relationships (imports/imported_by)
- Dependency clusters
- Data flow paths

### `specialist-registry.json`
Plugin system metadata:
- All specialist capabilities and activation patterns
- Input/output schemas
- Extension guide for adding new specialists
- Priority ordering rules

### `CONVENTIONS.md`
Documentation strategy and placement guidelines:
- Where to put different types of documentation
- Human-readable (Sphinx) vs machine-readable (.ai/)
- Style guides and naming conventions
- Examples and decision trees

### `TESTING.md`
Validation and testing guide:
- How to run documentation tests
- CI/CD integration
- Pre-commit hooks
- Maintenance procedures

### `GOTCHAS.md`
Common mistakes and anti-patterns:
- Things that look right but are wrong for THIS codebase
- Why standard practices don't apply here
- What to do instead with examples
- Detection patterns for AI assistants

## Usage by AI Models

AI assistants should:
1. Read `.ai/CONVENTIONS.md` first to understand documentation strategy
2. Read `.ai/context.md` for high-level architecture understanding
3. Use `codebase-map.json` to navigate module relationships
4. Reference `specialist-registry.json` when working with plugins
5. Follow `@ai-*` annotations in source files for detailed context
6. Consult `.ai/TESTING.md` for validation procedures

**Key Rule:** Human-readable docs go in `docs/*.rst` (Sphinx), machine-readable go in `.ai/*.{md,json}`

## Source Code Annotations

Look for structured comments in Python files:
```python
# @ai-indexable: core-functionality
# @ai-purpose: Brief description of module's role
# @ai-dependencies: External deps (packages, services)
# @ai-related: Related modules (paths)
# @ai-key-functions: Important functions/classes
# @ai-data-flow: How data moves through this module
```

## Maintenance

These files should be updated when:
- New modules/specialists are added
- Major architectural changes occur
- API contracts change significantly
- Extension patterns evolve

Current as of: 2025-12-16
