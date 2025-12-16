# Machine Documentation for AI Assistants

This folder contains **structured documentation designed for AI assistants** working with the Ada codebase.

## Quick Start for AI Assistants

**New here?** Start with [context.md](context.md) for architecture overview, then check [CONVENTIONS.md](CONVENTIONS.md) to understand where things go.

**Looking for specifics?** Use [codebase-map.json](codebase-map.json) to navigate modules and dependencies.

## Philosophy

**Machine-First Documentation:** Unlike human docs in `docs/*.rst`, these files prioritize:
- **Structure over narrative** - JSON when appropriate, concise Markdown
- **Relationships over explanation** - Dependency graphs, import chains  
- **Context over tutorial** - Architectural patterns, not step-by-step guides
- **Currency over completeness** - Quick updates, living documents

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

### `CLEANUP_NOTES.md`
Current status, recent changes, completed work. Check here to see what's been done recently.

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

## Reading Order for New AI Assistants

1. **[context.md](context.md)** - Big picture: architecture, service topology, key modules
2. **[CONVENTIONS.md](CONVENTIONS.md)** - Where things go and why
3. **[codebase-map.json](codebase-map.json)** - Navigate modules and dependencies
4. **[GOTCHAS.md](GOTCHAS.md)** - Avoid common mistakes
5. **[QUICKSTART.md](QUICKSTART.md)** - Quick reference for specific tasks

## What This Is (and Isn't)

**✅ This folder is:**
- Machine-first documentation for AI assistants
- Structured metadata (JSON + concise Markdown)
- Architecture and relationship focused
- Living documents, updated frequently

**❌ This folder is not:**
- A replacement for human docs (see `docs/`)
- Automatically generated (except specialist-registry.json)
- Comprehensive - focuses on patterns, not details
- A standard - an emerging pattern you can adapt

## Pattern Origins

This `.ai/` folder pattern emerged during Ada's development (2025) from practical need:
- Single instruction files (`.cursorrules`) don't scale for complex projects
- Human documentation isn't optimized for AI parsing
- Separation of concerns helps both humans and AIs

**Not Yet Standard:** This is an emerging pattern. We're sharing it as an example, not prescribing it as a rule. Adapt freely!

## Maintenance

**When to Update:**
- Adding/removing major modules → Update `codebase-map.json`
- Architecture changes → Update `context.md`
- New conventions → Update `CONVENTIONS.md`
- Completing work → Update `CLEANUP_NOTES.md`
- New gotchas discovered → Add to `GOTCHAS.md`

**Keep It Lean:**
- Avoid duplication with human docs
- Focus on what AIs need to know
- Prefer structure (JSON) over prose when possible
- Link to source code for details

---

**Questions about this pattern?** See [AI.md](../AI.md) in the repository root.

Current as of: 2025-12-16
