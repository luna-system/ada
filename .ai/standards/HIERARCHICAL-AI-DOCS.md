# Ada Documentation Standard: Hierarchical `.ai/` Folders

**Version:** 1.0  
**Date:** December 21, 2025  
**Status:** Active Standard

## Problem Statement

When AI assistants (Copilot, Claude, etc.) are scoped to a subdirectory, they cannot see parent documentation. A monorepo or multi-package ecosystem needs documentation at multiple levels.

## Solution: Hierarchical `.ai/` with Inheritance

Every package gets its own `.ai/` folder that:
1. **Provides local context** - Package-specific architecture, current work
2. **Points to parent** - Relative paths to ecosystem docs
3. **Excerpts key context** - Critical info that shouldn't require navigation

## Standard Structure

### Ecosystem Root (e.g., `ada-v1/`)

```
.ai/
├── context.md              # Full architecture overview
├── codebase-map.json       # Module dependency graph
├── CONVENTIONS.md          # Documentation standards
├── TESTING.md              # Testing patterns
├── GOTCHAS.md              # Common pitfalls
├── QUICKSTART.md           # Quick reference
└── packages/               # Optional: summaries for each package
    ├── ada-chat.md
    └── brain.md
```

### Package Level (e.g., `ada-vscode/packages/ada-chat/`)

```
.ai/
├── CONTEXT.md              # Package-specific context (REQUIRED)
├── PARENT.md               # Pointer to parent + key excerpts (REQUIRED)
├── HANDOFF.md              # Current work state (OPTIONAL)
└── [package-specific].md   # Any other package docs
```

## Required Files

### CONTEXT.md (Package-Specific)

Must include:
- **Purpose** - What this package does
- **Architecture** - Package-level design
- **Key Files** - Map of important files
- **Dependencies** - What it needs
- **Development** - How to run/test
- **Parent Reference** - Link to ecosystem docs

Template:
```markdown
# [Package Name] - Context

**Package:** `package-name`
**Type:** [Library|Service|Extension|CLI]
**Parent Ecosystem:** [Link to parent .ai/context.md]

## Purpose
[One paragraph description]

## Architecture
[Diagram or description]

## Key Files
| File | Purpose |
|------|---------|

## Development
[How to build/run/test]

## Parent Ecosystem Reference
- Architecture: `../../../.ai/context.md`
- Conventions: `../../../.ai/CONVENTIONS.md`
```

### PARENT.md (Ecosystem Pointer)

Must include:
- **Quick pointers** - Table of parent doc locations
- **Key excerpts** - Critical context that AI needs without navigating
- **When to read parent** - Guidance on what's where

Template:
```markdown
# Parent Ecosystem Reference

**This package is part of [Ecosystem Name].**

## Quick Pointers
| Need | Location |
|------|----------|
| Full architecture | `../../../.ai/context.md` |
| Conventions | `../../../.ai/CONVENTIONS.md` |

## Key Ecosystem Context (Excerpted)
[Critical info the AI needs immediately]

## When to Read Parent Docs
[Guidance on navigation]
```

## Benefits

1. **Scoped AI works** - Copilot in subdirectory has full context
2. **No duplication** - Parent docs are referenced, not copied
3. **Key info excerpted** - Critical context is immediately available
4. **Consistent navigation** - Same pattern everywhere

## Anti-Patterns

❌ **Don't duplicate** - Don't copy parent docs wholesale  
❌ **Don't orphan** - Every package needs PARENT.md  
❌ **Don't over-excerpt** - Only include critical info, link the rest  
❌ **Don't forget HANDOFF** - Active work state should be in package .ai/

## Example: Ada Ecosystem

```
ada-v1/                              # Ecosystem root
├── .ai/
│   ├── context.md                  # Full Ada architecture
│   ├── codebase-map.json
│   ├── ADA-CHAT-ARCHITECTURE.md    # Cross-cutting design
│   └── CONVENTIONS.md
│
├── brain/                           # Core service
│   └── .ai/
│       ├── CONTEXT.md              # Brain-specific
│       └── PARENT.md               # Points to root
│
├── ada-vscode/packages/ada-chat/    # VS Code extension
│   └── .ai/
│       ├── CONTEXT.md              # Extension-specific
│       ├── PARENT.md               # Points to root
│       └── HANDOFF.md              # Current debug state
│
└── ada-mcp/                         # MCP server
    └── .ai/
        ├── CONTEXT.md
        └── PARENT.md
```

## Adoption

When creating a new package:
1. Create `.ai/` folder
2. Write `CONTEXT.md` using template
3. Write `PARENT.md` with relative paths
4. If active work, add `HANDOFF.md`

When AI is scoped to package:
1. AI reads local `.ai/CONTEXT.md` first
2. AI can follow `PARENT.md` links for deeper context
3. `HANDOFF.md` provides immediate work state

## GitHub Organization Standard

When Ada moves to `github.com/ada-ai/`:
- Each repo gets its own `.ai/`
- Cross-repo references use GitHub URLs
- Organization-level docs at `ada-ai/.github/.ai/`

---

*This standard was developed during Ada v3.0 development when we discovered that scoping Copilot to `ada-chat/` broke access to ecosystem documentation.*
