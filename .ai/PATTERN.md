# The `.ai/` Folder Pattern

> **Meta-documentation:** This file describes the pattern itself, not the Ada codebase.

## What Problem Does This Solve?

**The Challenge:** AI assistants need different documentation than humans.
- **Humans** need tutorials, examples, narrative explanations
- **AIs** need structure, relationships, architectural patterns

**Existing Solutions (2024-2025):**
- `.cursorrules` - Single instruction file (works for small projects)
- `.github/copilot-instructions.md` - GitHub-specific
- `AI.md` in root - Common but unstructured
- `.clinerules` - Claude-specific

**Limitations:**
- Single files don't scale to complex projects
- Hard to maintain as projects grow
- No standard structure
- Mixing concerns (instructions + architecture + conventions)

## The `.ai/` Folder Solution

**Core Idea:** Dedicated folder for machine-readable documentation, separate from human docs.

### Minimal Implementation

Start with just two files:

```
.ai/
├── README.md    # What this folder is
└── context.md   # Architecture overview
```

**AI.md in root** → Points to `.ai/` folder

### Standard Implementation (Ada's Approach)

```
.ai/
├── README.md               # Pattern explanation
├── context.md              # Architecture overview
├── codebase-map.json       # Module dependencies
├── CONVENTIONS.md          # Documentation strategy
├── QUICKSTART.md           # Common tasks
├── CLEANUP_NOTES.md        # Current status
└── GOTCHAS.md              # Known pitfalls
```

### Extended Implementation (Future)

```
.ai/
├── README.md
├── context.md
├── codebase-map.json
├── CONVENTIONS.md
├── architecture/           # Detailed subsystem docs
│   ├── api.md
│   ├── database.md
│   └── auth.md
├── schemas/                # JSON schemas
│   ├── config-schema.json
│   └── api-schema.json
└── workflows/              # Common development flows
    ├── add-feature.md
    └── deploy.md
```

## File Format Conventions

### `context.md` - Architecture Overview
**Purpose:** High-level understanding of system structure
**Format:** Markdown with clear sections

```markdown
# Ada Context

## Service Topology
[ASCII diagram of services]

## Data Flow
[Step-by-step flow description]

## Key Modules
- module_name.py: Purpose and relationships

## Extension Points
How to add new features

## Testing Philosophy
How tests are structured
```

### `codebase-map.json` - Module Dependencies
**Purpose:** Machine-readable dependency graph
**Format:** JSON with consistent schema

```json
{
  "module_name": {
    "type": "service|utility|config",
    "purpose": "Brief description",
    "key_functions": ["func1", "func2"],
    "imports": ["dep1", "dep2"],
    "imported_by": ["user1", "user2"],
    "endpoints": ["/api/path"],
    "notes": "Special considerations"
  }
}
```

### `CONVENTIONS.md` - Where Things Go
**Purpose:** Documentation strategy
**Format:** Decision tree and guidelines

```markdown
# Where to Put Documentation

## Decision Tree
- Tutorial? → docs/*.rst
- API reference? → docs/api_reference.rst
- Architecture? → .ai/context.md
- Code explanation? → Inline comments

## Guidelines
[Specific rules for your project]
```

## Adoption Path

### Phase 1: Discovery (Day 1)
1. Create `AI.md` in root
2. Add brief architecture notes
3. Link to relevant docs

### Phase 2: Structure (Week 1)
1. Create `.ai/` folder
2. Add `README.md` and `context.md`
3. Update `AI.md` to point to `.ai/`

### Phase 3: Expansion (Month 1)
1. Add `codebase-map.json`
2. Create `CONVENTIONS.md`
3. Add `GOTCHAS.md` as issues arise

### Phase 4: Refinement (Ongoing)
1. Keep docs current with code changes
2. Add specialized files as needed
3. Gather feedback from AI interactions

## Making This a Standard (Carefully!)

**The xkcd 927 Problem:** "How standards proliferate"
- We have 14 competing standards
- "I'll create a universal standard!"
- Now we have 15 competing standards

**Our Approach:**
1. **Document, don't prescribe** - Share what works for us
2. **Stay compatible** - Works alongside `.cursorrules`, etc.
3. **Show value** - Let results speak for themselves
4. **Adapt freely** - Encourage modifications for other contexts
5. **No gatekeeping** - It's a pattern, not a specification

## What Would Make This Better?

### Short Term
- [ ] Schema validation for JSON files
- [ ] Template files for new projects
- [ ] Example `.ai/` folders from diverse project types
- [ ] Integration with popular AI coding tools

### Medium Term
- [ ] Community examples and best practices
- [ ] Tool support (linters, generators, validators)
- [ ] IDE integration (navigation, syntax highlighting)
- [ ] Documentation on measuring effectiveness

### Long Term
- [ ] Informal RFC for community feedback
- [ ] Cross-tool support (Cursor, GitHub Copilot, etc.)
- [ ] Standard schemas for common patterns
- [ ] Research on AI assistant performance improvements

## How to Contribute to the Pattern

**If you adopt this:**
1. Share what works and what doesn't (GitHub discussions, blog posts)
2. Adapt it to your domain (backend, frontend, ML, etc.)
3. Document your variations
4. Share metrics if you measure effectiveness

**If you want to iterate:**
1. Fork and experiment
2. Try different file structures
3. Test with different AI models
4. Report findings back to community

## Measuring Success

**Qualitative Signals:**
- AI assistants make fewer architectural mistakes
- Less back-and-forth to understand context
- Better suggestions on first try
- Fewer "where does this go?" questions

**Quantitative Signals (Future):**
- Time to first correct suggestion
- Accuracy of code placement
- Number of clarifying questions needed
- Developer satisfaction scores

## Related Patterns

- **`.cursorrules`** - Single file instructions (complementary, not competing)
- **`docs/`** - Human documentation (different audience)
- **`ARCHITECTURE.md`** - High-level overview (often duplicates context.md)
- **ADRs (Architecture Decision Records)** - Historical decisions (complementary)

## Philosophy

**Core Beliefs:**
1. AI assistants deserve first-class documentation
2. Structure helps machines, narrative helps humans
3. Separation of concerns improves both
4. Living docs beat comprehensive stale docs
5. Examples matter more than specifications

**Non-Goals:**
- Replace human documentation
- Create a rigid standard
- Work for every project
- Solve all AI assistant limitations

## Credits

**Developed by:** luna system + Claude Sonnet 4.5 during Ada development (2025)

**Inspired by:**
- Cursor's `.cursorrules` pattern
- The Aider project's context files
- Decades of "README-driven development"
- Pain points from real AI-assisted development

**License:** Pattern is public domain - use and adapt freely!

---

**Questions? Improvements?** Open an issue or discussion in the Ada repository.
