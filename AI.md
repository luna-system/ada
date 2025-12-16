# AI Assistant Documentation

> **For AI assistants working with this codebase:** This project uses a structured `.ai/` folder for machine-readable documentation. Start there!

## Quick Links

- **[.ai/context.md](.ai/context.md)** - Architecture overview, service topology, key modules
- **[.ai/codebase-map.json](.ai/codebase-map.json)** - Complete module dependency graph
- **[.ai/CONVENTIONS.md](.ai/CONVENTIONS.md)** - Documentation strategy and where things live
- **[.ai/QUICKSTART.md](.ai/QUICKSTART.md)** - Quick reference for common tasks

## What's in `.ai/`?

The `.ai/` folder contains **machine-readable documentation** designed for AI assistants:

```
.ai/
├── context.md              # High-level architecture and patterns
├── codebase-map.json       # Module dependencies and relationships
├── CONVENTIONS.md          # Documentation strategy
├── CLEANUP_NOTES.md        # Current status and recent changes
├── specialist-registry.json # Plugin metadata (auto-generated)
├── QUICKSTART.md           # Common tasks quick reference
├── GOTCHAS.md              # Known pitfalls and solutions
├── TESTING.md              # Testing patterns
└── README.md               # This structure explained
```

## Philosophy

**Separation of Concerns:**
- `docs/*.rst` → Human documentation (Sphinx/ReadTheDocs)
- `.ai/*.{md,json}` → Machine documentation (AI assistants)
- Inline comments → Code-level documentation

**Why this matters:**
- Humans need narrative, examples, tutorials
- AIs need structure, dependencies, conventions
- Both deserve first-class documentation

## For Project Maintainers

If you're considering adopting this pattern:

1. **Start minimal:** Just `AI.md` (this file) + `.ai/context.md`
2. **Add structure:** Create `.ai/codebase-map.json` for complex projects
3. **Keep current:** Update `.ai/` docs when architecture changes
4. **Make it discoverable:** Link from README or CONTRIBUTING

**This is not a standard (yet).** It's a pattern that works for us. Adapt it to your needs!

---

**Attribution:** This pattern developed collaboratively by luna system and Claude Sonnet 4.5 during Ada's development (2025).
