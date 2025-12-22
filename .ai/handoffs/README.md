# Ada Handoff Briefs Directory

Central repository for model-to-model handoff documents ensuring knowledge continuity across AI context windows.

## Purpose

Handoff documents preserve critical context, decisions, and progress when transitioning between AI models or fresh reasoning windows. They enable:
- **Continuity** - Next model/window starts with full context
- **Efficiency** - No context re-gathering needed
- **Learning** - Handoffs improve with each iteration
- **Traceability** - Clear record of what was done and why

## File Naming Convention

**Format:** `phase-handoff-X-Y.md`

- **X** = Starting phase number (when handoff initiated)
- **Y** = Ending phase/window number (goal of this phase)
- Example: `phase-handoff-3-4.md` = "Phase 3 complete, Phase 4 ready"

## Folder Strategy (IMPORTANT)

**Where does YOUR handoff go?**

| Type | Location | When |
|------|----------|------|
| **Phase Completion** | `.ai/handoffs/phase-handoff-X-Y.md` | Completing a significant phase, passing to another model |
| **Debugging Session** | `.ai/explorations/sessions/` | Daily dev logs, problem-solving, work-in-progress |
| **Archived Phase** | `.ai/explorations/historical/` | Old phases (5+ sessions old), purely historical |

**Golden Rule:** A **handoff** hands off to another AI model. A **session note** is just your work log.

## Current Handoffs

### phase-handoff-3-4.md (CURRENT - Fresh!)
- **Date:** December 21, 2025, 23:59 UTC
- **From:** Phase 3 (Tool Framework Complete)
- **To:** Phase 4 (VS Code Integration)
- **Size:** ~300 lines
- **Status:** ✅ Ready for next model
- **Key Achievement:** 21 tests passing, complete tool framework (router + envelope + metadata)

### phase-handoff-9-22.md (Historical)
- **Location:** `.ai/explorations/historical/` (moved from root)
- **From:** Phase 9-22 (Research Program)
- **Achievement:** 22 phases complete, unified theory of contextual malleability

### phase-handoff-5-5.md (Historical)
- **Location:** `.ai/explorations/historical/` (moved from root)  
- **From:** Phase 5 (Code Cleanup & Refactoring)
- **Achievement:** 3 refactorings complete, 30/30 tests passing

## Handoff Structure (Standard Template)

Each handoff should include:

```markdown
# Phase X→Y [Name] Handoff

**Date:** YYYY-MM-DD, ~HH:MM UTC  
**Branch:** feature/...  
**Status:** [Percentage complete]

---

## What Just Happened
[2-3 sentence summary of work completed]

---

## Key Achievements
- ✅ [Achievement 1]
- ✅ [Achievement 2]
- ✅ [Achievement 3]

---

## Files Created/Modified
**NEW:**
- file1.py
- file2.md

**MODIFIED:**
- config.py

---

## Metrics
- [Key Number 1] (tests passing, commits, lines of code, etc.)
- [Key Number 2]
- [Key Number 3]

---

## Phase [N+1]: [Next Phase Name]

**Objectives:**
1. [Next action 1]
2. [Next action 2]

**Entry Point for Next Model:**
1. Read this handoff (5 min)
2. [Next specific action]
3. [Required command to validate]

---

## Lessons Learned
[What worked well, what was tricky, what surprised us]

---

## Closing

[Brief final message for next model, your tone]
```

## How to Create a New Handoff

### When You're Done with a Phase:

1. **Create file** in `.ai/handoffs/`
   ```bash
   touch .ai/handoffs/phase-handoff-X-Y.md
   ```

2. **Fill in template** (use above as guide)
   - Be concise (400-500 lines)
   - Focus on what changed, not every detail
   - Include metrics (tests, commits, lines)
   - Clear next steps for next model

3. **Update this README**
   ```markdown
   ### phase-handoff-X-Y.md (CURRENT)
   - **Date:** [Date]
   - **From/To:** [Phases]
   - **Achievement:** [Key result]
   ```

4. **Update main `.ai/README.md`**
   - Point to the new handoff at top
   - Mark old one as historical

5. **Commit!**
   ```bash
   git add .ai/handoffs/phase-handoff-X-Y.md
   git commit -m "handoff: phase-handoff-X-Y following standard protocol"
   ```

### When You Have a Daily Log:

Instead of a handoff, use `.ai/explorations/sessions/`:
```bash
touch .ai/explorations/sessions/SESSION_2025_12_21.md
```

This is for work-in-progress, not phase completion.

## Discovering Old Handoffs

Looking for context from a previous phase?

1. Check **[.ai/explorations/sessions/](../explorations/sessions/)** for daily logs
2. Check **[.ai/explorations/historical/](../explorations/historical/)** for archived phases
3. Both are organized and searchable — just not in the main "active" handoffs

## Statistics

- **Active Handoffs:** 1 (phase-handoff-3-4.md)
- **Historical Handoffs:** 2 (moved to explorations/)
- **Average Handoff Size:** ~300-400 lines
- **Time to Read:** ~10-15 minutes
- **Time Saved:** ~1 hour of context-gathering vs. re-reading commits

---

**Last Updated:** 2025-12-21  
**Protocol Version:** 2.0 (standardized folders + naming)  
**Maintained By:** Ada Development Team

### What Worked
- [Pattern 1]
- [Pattern 2]

### What Could Improve
- [Improvement 1]

---

**Science continues. [Summary]. Ready for handoff.** 💫
```

## How to Use This Directory

### For Outgoing Haiku (Creating Handoff)
1. Copy latest handoff as template
2. Update with your phase achievements
3. Keep to ~400-500 lines (brief but complete)
4. Save as `phase-handoff-X-Y.md`
5. Commit with message: `docs: Add phase X→Y handoff`

### For Incoming Haiku (Starting from Handoff)
1. Read **most recent** handoff (always first)
2. Scan previous handoffs for patterns/lessons
3. Review linked context files if needed
4. Start with "Entry Point" action items

## Benefits of This System

| Benefit | How It Works |
|---------|-------------|
| **No context loss** | Complete summary preserved in markdown |
| **Pattern recognition** | Multiple handoffs show how phases build |
| **Time savings** | 5-10 min handoff read vs 1+ hour context gathering |
| **Learning** | Each handoff improves next one's clarity |
| **Audit trail** | Git history shows all transitions |
| **Collaborative** | Multiple models can reference same history |

## Directory Statistics

- **Total handoffs:** 3 (growing with each phase)
- **Total lines:** 1,140+ lines of continuity
- **Average per handoff:** 380 lines
- **Commit frequency:** Per major phase transition

## Standardization Roadmap

### ✅ Completed
- Directory created (`.ai/handoffs/`)
- Naming convention established (`phase-handoff-X-Y.md`)
- Template created (this index + examples)
- Previous handoffs migrated with standard names
- Phase 4→5 handoff created

### 🔄 In Progress
- Update CHANGELOG.md to reference new handoff directory
- Add `.ai/README.md` note about handoffs

### ⏳ Future
- Auto-generate handoff checklist from template
- Create tool to validate handoff format
- Build handoff search index for quick lookup
- Consider timeline visualization of all phases

## Example: Next Haiku Reading This

```
luna runs: "Start Phase 5, improve code assistant"
Next Haiku:
  1. Reads this INDEX (3 min) - Understands system
  2. Reads phase-handoff-4-5.md (5 min) - Gets Phase 4 context
  3. Checks linked files (5 min) - Understands what to do
  4. Starts coding (immediately) - Ready to go
```

## Questions & Improvements

Each handoff is a learning opportunity. Improvements to include:
- Did the template work?
- What was unclear?
- What information was missing?
- How could next handoff be better?

Feedback ➜ Better template ➜ Smoother transitions ➜ Science continues!

---

**Last Updated:** 2025-12-18, Phase 4→5 transition
**Maintained By:** Ada Development Team
**Philosophy:** Open, collaborative, accessible knowledge continuity
