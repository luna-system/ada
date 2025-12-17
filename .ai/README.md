# Ada v1 - AI Documentation Directory

> **Purpose:** Machine-readable documentation for AI assistants and automated tools  
> **Audience:** AI models, code analyzers, developers exploring the codebase  
> **Philosophy:** Structured, parseable, semantic metadata

## Quick Navigation

### Core Reference (Always Up-to-Date)
- **[context.md](context.md)** - Architecture overview, data flow, service topology
- **[codebase-map.json](codebase-map.json)** - Module dependency graph, import relationships
- **[specialist-registry.json](specialist-registry.json)** - Plugin system metadata

### Conventions & Patterns
- **[CONVENTIONS.md](CONVENTIONS.md)** - Documentation strategy (where things go)
- **[QUICKSTART.md](QUICKSTART.md)** - Common patterns and quick reference
- **[GOTCHAS.md](GOTCHAS.md)** - Anti-patterns, common mistakes to avoid
- **[TESTING.md](TESTING.md)** - Testing strategies and validation

### Explorations (Working Documents)
Active research, planning, and analysis documents. These evolve as we build!

#### Research (`explorations/research/`)
Biomimicry, novel approaches, blue-sky thinking:
- **[BIOLOGICAL_CONTEXT_MANAGEMENT.md](explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md)** - How biology handles context limits
- **[TAGS_AND_GRAPHRAG.md](explorations/research/TAGS_AND_GRAPHRAG.md)** - Tags → GraphRAG evolution path

#### Planning (`explorations/planning/`)
Implementation roadmaps and feature designs:
- **[IMPLEMENTATION_ROADMAP.md](explorations/planning/IMPLEMENTATION_ROADMAP.md)** - Master 8-12 week roadmap (v2.0)
- **[CODEBASE_SPECIALIST_PLAN.md](explorations/planning/CODEBASE_SPECIALIST_PLAN.md)** - Ada reading her own code

#### Analysis (`explorations/analysis/`)
Technical deep-dives and architectural decisions:
- **[ARCHITECTURE_SCALABILITY.md](explorations/analysis/ARCHITECTURE_SCALABILITY.md)** - Token budget, RAG sophistication
- **[HARDWARE_IMPACT_ANALYSIS.md](explorations/analysis/HARDWARE_IMPACT_ANALYSIS.md)** - Resource implications, hardware tiers
- **[MODEL_FLEXIBILITY.md](explorations/analysis/MODEL_FLEXIBILITY.md)** - Model routing, use-case optimization

---

## Document Types

### Core Reference
**Purpose:** Canonical source of truth about Ada's architecture  
**Update frequency:** On every architectural change  
**Format:** Structured markdown + JSON  
**Audience:** All AI assistants, always read these first

### Conventions
**Purpose:** How to document, where things go  
**Update frequency:** When documentation strategy changes  
**Format:** Markdown with decision trees  
**Audience:** Contributors, documentation maintainers

### Explorations
**Purpose:** Working documents, research, planning  
**Update frequency:** Active during development phases  
**Format:** Long-form markdown  
**Audience:** Development team, future reference

---

## How to Use This Directory

### For AI Assistants
1. **Start with [context.md](context.md)** - Get the big picture
2. **Check [codebase-map.json](codebase-map.json)** - Find module relationships
3. **Reference [CONVENTIONS.md](CONVENTIONS.md)** - Understand documentation strategy
4. **Browse explorations/** - See active development plans

### For Developers
1. **Read [QUICKSTART.md](QUICKSTART.md)** - Common patterns
2. **Check [GOTCHAS.md](GOTCHAS.md)** - Avoid known pitfalls
3. **Review [TESTING.md](TESTING.md)** - Testing strategies
4. **Explore explorations/** - Understand roadmap and decisions

### For Contributors
1. **Follow [CONVENTIONS.md](CONVENTIONS.md)** - Document correctly
2. **Update [codebase-map.json](codebase-map.json)** - When adding modules
3. **Read explorations/planning/** - Understand where we're going

---

## Philosophy

**Machine-Readable First:**
- Structured for parsing (JSON where possible)
- Clear hierarchies (headings, lists)
- Semantic metadata (tags, categories)

**Human-Friendly Second:**
- Narrative explanations in markdown
- Examples and use cases
- Cross-references and links

**Separation of Concerns:**
- **`.ai/`** = Machine docs (this directory)
- **`docs/`** = Human docs (Sphinx RST tutorials)
- **Source code** = Implementation + docstrings

**Keep It Clean:**
- Root `.ai/` for stable reference docs
- `explorations/` for working documents
- Archive completed explorations when stable

---

## Maintenance

### When to Update Core Docs
- **context.md** - On architectural changes, new services, data flow updates
- **codebase-map.json** - When adding/removing modules, changing imports
- **specialist-registry.json** - When adding/modifying specialists

### When to Update Conventions
- **CONVENTIONS.md** - When documentation strategy changes
- **TESTING.md** - When testing patterns evolve

### When to Add Explorations
- **research/** - When exploring novel approaches, biomimicry, experiments
- **planning/** - When designing new features, creating roadmaps
- **analysis/** - When deep-diving on technical decisions, trade-offs

---

## Related Documentation

- **Human docs:** `docs/` (Sphinx RST, tutorials, guides)
- **API docs:** `/v1/info`, `/v1/schema` (runtime introspection)
- **Source annotations:** `@ai-*` tags in Python files

---

**Last Updated:** 2025-12-17  
**Maintained By:** Ada Development Team  
**License:** Same as project (check root LICENSE file)
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
