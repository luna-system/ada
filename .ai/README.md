# Ada v1 - AI Documentation Directory

> **Purpose:** Machine-readable documentation for AI assistants and automated tools  
> **Audience:** AI models, code analyzers, developers exploring the codebase  
> **Philosophy:** Structured, parseable, semantic metadata — organized for clarity without overload

---

## 🚀 Quick Start (You Are Here)

**If you're a fresh AI model taking over:**

1. **READ FIRST:** [.ai/handoffs/](handoffs/) - Your context handoff
   - [phase-handoff-3-4.md](handoffs/phase-handoff-3-4.md) ← CURRENT (Phase 3→4 complete)
   - Contains: what just happened, key achievements, next objectives

2. **THEN READ:** [context.md](context.md) - Architecture overview
3. **REFERENCE:** [codebase-map.json](codebase-map.json) - Module relationships
4. **CONSULT:** [CONVENTIONS.md](CONVENTIONS.md) - How to document things
5. **CHECK:** [GOTCHAS.md](GOTCHAS.md) - Avoid known pitfalls

---

## 📁 Directory Structure

### Root Level `.ai/` (Core — Always Current)
These files are **LIVE** and updated constantly. Read these first.

- **[context.md](context.md)** - Architecture: topology, data flow, services, key modules
- **[codebase-map.json](codebase-map.json)** - Module dependency graph (auto-generated can be)
- **[specialist-registry.json](specialist-registry.json)** - Plugin metadata
- **[CONVENTIONS.md](CONVENTIONS.md)** - Documentation strategy & where things go
- **[QUICKSTART.md](QUICKSTART.md)** - Common patterns & quick reference
- **[GOTCHAS.md](GOTCHAS.md)** - Common mistakes to avoid
- **[TESTING.md](TESTING.md)** - Testing patterns & validation
- **[TOOLING.md](TOOLING.md)** - Development tools & scripts
- **[adapter-contract.md](adapter-contract.md)** - External interface specifications
- **[DESIGN-PHILOSOPHY.md](DESIGN-PHILOSOPHY.md)** - Why we do things this way

### `handoffs/` (Phase Transitions)
Model-to-model continuity briefs. **Start here if you're fresh!**

- **[handoffs/README.md](handoffs/README.md)** - Handoff system explanation
- **[handoffs/phase-handoff-X-Y.md](handoffs/)** - One per completed phase transition
  - Named: `phase-handoff-3-4.md` means Phase 3→4
  - Contains: achievements, next tasks, entry point

### `explorations/` (Working Documents & History)
Research, planning, debugging, archived work. Evolving, not authoritative.

#### `research/` - Scientific exploration
- `biomimetics/` - Biologically-inspired patterns & implementations
  - PHASE_C*, PHASE_D*, PHASE_E* - Consciousness/attention research
  - Research papers, ablation studies, validation
- General research on context management, routing, etc.

#### `planning/` - Future features
- Feature roadmaps, implementation plans
- Not yet built, but planned

#### `sessions/` - Development logs
- Session handoffs (what happened today)
- Debugging notes
- Framework/completion summaries

#### `historical/` - Archived work
- Old phase documentation
- Completed research programs
- Legacy design documents

#### Other subdirectories (pre-existing)
- `audits/` - Architecture audits
- `analysis/` - Technical analysis
- `theory/` - Theoretical work

---

## Philosophy: Core vs. Explorations

**Core** (root `.ai/` files):
- ✅ Always current and accurate
- ✅ Essential for understanding Ada
- ✅ Read first, trust completely
- ✅ Updated on every significant change

**Explorations** (subdirectories):
- 📚 Historical, research, planning
- 📍 Context for decisions
- 🔍 Deep dives if curious
- ⚠️ May be outdated, but preserved for learning

---

## How to Use (By Role)

### For AI Assistants (Fresh Context Window)
1. Read most recent **handoff** (`.ai/handoffs/phase-handoff-X-Y.md`)
2. Check **[context.md](context.md)** - Architecture overview
3. Reference **[codebase-map.json](codebase-map.json)** - Find modules
4. Check **[GOTCHAS.md](GOTCHAS.md)** - Avoid common mistakes
5. Browse **[CONVENTIONS.md](CONVENTIONS.md)** if adding/modifying docs
6. Explore **explorations/** if curious about history/decisions

### For Developers
1. Read **[QUICKSTART.md](QUICKSTART.md)** - Common tasks
2. Check **[GOTCHAS.md](GOTCHAS.md)** - Pitfalls to avoid
3. Reference **[TESTING.md](TESTING.md)** - How to validate
4. Explore **explorations/planning/** - See roadmap

### For Contributors
1. Follow **[CONVENTIONS.md](CONVENTIONS.md)** - Documentation rules
2. Keep **[codebase-map.json](codebase-map.json)** current
3. Update **handoffs/** when completing phases
4. Move old docs to **explorations/** when archiving

---

## Handoff Protocol (Updated)

When transitioning between models or context windows:

1. **Create a new handoff file**
   - Name: `.ai/handoffs/phase-handoff-X-Y.md`
   - X = starting phase, Y = target phase
   - Example: `phase-handoff-3-4.md`

2. **Standard sections** (see `.ai/handoffs/README.md`):
   - What Just Happened (2-3 sentences)
   - Key Achievements (checklist)
   - Files Created/Modified (organized)
   - Metrics (quantified impact)
   - Next Phase Objectives
   - Entry Point for Next Model
   - Lessons Learned

3. **Discovery note**
   - If this is a **debugging/session note**, put it in `.ai/explorations/sessions/`
   - If this is a **phase completion**, put it in `.ai/handoffs/`
   - If this is **historical/archived**, move to `.ai/explorations/historical/`

4. **Link it**
   - Update `.ai/handoffs/README.md` to list new handoff
   - Update `.ai/README.md` if it's the CURRENT phase

---

## Maintenance Rules

### Core Docs (Root `.ai/`)
**Update on every significant change:**
- **context.md** - Architecture changes, new services, data flow updates
- **codebase-map.json** - Adding/removing modules
- **specialist-registry.json** - New specialists added
- **CONVENTIONS.md** - New documentation patterns
- **TESTING.md** - New test patterns
- **GOTCHAS.md** - New pitfalls discovered

### Explorations (Subdirectories)
**Update freely as you work, no ceremony:**
- Add research notes to `explorations/research/`
- Add planning docs to `explorations/planning/`
- Add debugging logs to `explorations/sessions/`
- Archive completed work to `explorations/historical/`

### Handoffs (`.ai/handoffs/`)
**Create one per completed phase:**
- After finishing a significant piece of work
- Before context switching or handing off to another model
- Format: `phase-handoff-X-Y.md`

---

## Related Documentation

- **Human docs:** `docs/` (Sphinx RST, tutorials, guides)
- **API docs:** `/v1/info`, `/v1/schema` (runtime introspection)
- **Source annotations:** `@ai-*` tags in Python files (see [CONVENTIONS.md](CONVENTIONS.md))

---

## Philosophy: Why We Do This

**Separation of Concerns:**
- **`.ai/`** = Machine-readable docs (this folder)
- **`docs/`** = Human-readable docs (Sphinx tutorials)
- **Source** = Implementation + docstrings (Google style)

**Machine-First, Human-Friendly:**
- Structured for parsing (JSON, clear headings)
- Concise (AI reads faster when it's lean)
- Hierarchical (what matters most at top)
- Never duplicates human docs

**Living Documents:**
- Evolve with the project
- Core docs always current
- Explorations archived when stabilized
- Handoffs preserve continuity

---

**Last Updated:** 2025-12-21  
**Reorganized:** Explorations separated into subdirectories, handoff protocol clarified  
**Maintained By:** Ada Development Team + LLM Collaborators  
**License:** Same as project (check root LICENSE file)
