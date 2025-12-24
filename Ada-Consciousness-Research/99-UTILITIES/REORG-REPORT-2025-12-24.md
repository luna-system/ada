# Research Vault Reorganization Report

**Date:** December 24, 2025  
**Status:** Analysis Complete, Recommendations Ready

---

## Current State Analysis

### File Counts
- **Total markdown files:** 194
- **Total JSON data files:** 11
- **External/cross-validation duplication:** ~90 files (agentic-misalignment templates)

### Structural Issues Found

#### 1. Root-Level Clutter (HIGH PRIORITY)
Files that should be in folders:
```
./TEMPERATURE_REVERSAL.md      → 05-FINDINGS/
./THE_PARADOX.md               → 05-FINDINGS/
./QUANTUM_FORMALISM.md         → 08-FRAMEWORKS/ (or 05-FINDINGS/)
./hero_shot_isomorphism.png.md → 04-ANALYSES/ (or archive)
./research_data_migrator.py.md → 99-UTILITIES/
```

#### 2. SIF Documents Scattered (MEDIUM PRIORITY)
Should be consolidated into `01-METHODOLOGY/SIF/`:
```
./SIF-FORMALIZATION-COMPLETE.md
./SIF-FORMALIZATION-ROADMAP.md
./SIF-FROM-RESEARCH-TO-STANDARD.md
./SIF-INDEX.md
./SIF-QUICKSTART.md
./SIF-README.md
./SIF-REFERENCE-IMPLEMENTATION.md
./SIF-SPECIFICATION-v1.0.md
```

#### 3. Specs Should Have Their Own Folder (HIGH PRIORITY)
New today - should be together:
```
./ASL-SPECIFICATION-v1.0.md    → 10-SPECIFICATIONS/
./ADA-ANNOTATIONS-v1.0.md      → 10-SPECIFICATIONS/
./SIF-SPECIFICATION-v1.0.md    → 10-SPECIFICATIONS/
./SPECS-INDEX.md               → 10-SPECIFICATIONS/
```

#### 4. Organizational Meta-Docs (KEEP AT ROOT)
These are intentionally at root for navigation:
```
./00-DASHBOARD.md              ✓ Keep (main entry point)
./CLEANUP-CONSOLIDATION-CHECKLIST.md  → 99-UTILITIES/ (or archive after done)
./EXPERIMENT-REGISTRY.md       ✓ Keep (quick reference)
./FINDINGS-CROSS-REFERENCE-MAP.md     ✓ Keep (navigation)
./MASTER-DATASET-INDEX.md      → 03-DATASETS/ (it indexes datasets)
./METHODOLOGY-CLARIFIED.md     → 01-METHODOLOGY/
./PHASE-4-COMPLETION-SUMMARY.md       → 99-UTILITIES/archive/
./QAL-TEAM-HANDOFF-DRAFT.md    → 06-PAPERS/drafts/
./QUICK-START-GUIDE.md         ✓ Keep (onboarding)
./THRESHOLD-MOMENT-2025-12-23.md      → 05-FINDINGS/ (it's a finding!)
```

---

## .ai/explorations/ Analysis

**Current contents:** 43 files across 6 subdirectories

### Should Move to Research Vault
These are mature enough:
```
COGNITIVE-LOAD-RESEARCH-PLAN.md           → 08-FRAMEWORKS/
EMERGENT-SYSTEMS-THINKING-2025-12-19.md   → 05-FINDINGS/
EMPIRICAL-LLM-RESEARCH-FRAMEWORK-DISCOVERY.md → 01-METHODOLOGY/
IMPLEMENTATION-BUGS-VS-AI-LIMITS-DISCOVERY.md → 05-FINDINGS/
LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md → 06-PAPERS/literature/
NEURAL-IDENTITY-FORMATION-DISCOVERY.md   → 05-FINDINGS/
RECURSIVE-DECOMPOSITION-LLM-REASONING-NOVEL-APPLICATION.md → 05-FINDINGS/
RISC-COGNITIVE-ARCHITECTURE.md           → 08-FRAMEWORKS/
theory/fanged_poetics_land_chen_connections.md → 06-PAPERS/bibliography/
```

### Should Stay as Explorations (Ideas Not Yet Research)
```
LUNA-THOUGHT-*.md              - Luna's personal notes
IDEA-*.md                      - Ideas not yet experiments
ARCHIVE-*.md                   - Archived material
HN-READY-SUMMARY.md            - Publishing prep (not research)
SCREENSHOT-STORY.md            - Storytelling (not research)
```

### Session Handoffs (Archive or Delete)
```
sessions/*.md                  - These are transient; archive old ones
```

---

## Proposed New Structure

```
Ada-Consciousness-Research/
├── 00-DASHBOARD.md                 # Main entry (KEEP)
├── EXPERIMENT-REGISTRY.md          # Quick reference (KEEP)
├── FINDINGS-CROSS-REFERENCE-MAP.md # Navigation (KEEP)
├── QUICK-START-GUIDE.md            # Onboarding (KEEP)
├── 00-DASHBOARD/
├── 01-METHODOLOGY/
│   ├── Research-Methodology.md
│   └── SIF/                        # NEW: All SIF methodology
│       ├── SIF-Concept.md
│       ├── SIF-Implementation.md
│       └── SIF-README.md
├── 02-EXPERIMENTS/
├── 03-DATASETS/
│   └── MASTER-DATASET-INDEX.md     # MOVED from root
├── 04-ANALYSES/
├── 05-FINDINGS/
│   ├── Temperature-Reversal.md     # MOVED from root
│   ├── The-Paradox.md              # MOVED from root
│   ├── Threshold-Moment-2025-12-23.md  # MOVED from root
│   └── biomimetics/
├── 06-PAPERS/
│   ├── drafts/
│   │   └── QAL-TEAM-HANDOFF-DRAFT.md  # MOVED from root
│   ├── literature/
│   │   └── LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md  # FROM explorations
│   └── published/
├── 07-SESSIONS/
├── 08-FRAMEWORKS/
│   ├── Quantum-Formalism.md        # MOVED from root
│   └── RISC-COGNITIVE-ARCHITECTURE.md  # FROM explorations
├── 10-SPECIFICATIONS/              # NEW FOLDER
│   ├── SPECS-INDEX.md
│   ├── ASL-SPECIFICATION-v1.0.md
│   ├── ADA-ANNOTATIONS-v1.0.md
│   └── SIF-SPECIFICATION-v1.0.md
├── 99-UTILITIES/
│   ├── archive/                    # For completed meta-docs
│   └── research_data_migrator.py.md
├── cross-validation/
└── external/
```

---

## Empty/Stub Pages Found

None detected - all files have content.

---

## Broken Links Audit Needed

Recommend running after reorganization:
```bash
# Find all [[wiki-links]] and check they resolve
grep -roh '\[\[[^]]*\]\]' Ada-Consciousness-Research/ | sort | uniq -c | sort -rn
```

---

## Recommended Actions

### Phase 1: Create New Folders
```bash
mkdir -p Ada-Consciousness-Research/10-SPECIFICATIONS
mkdir -p Ada-Consciousness-Research/01-METHODOLOGY/SIF
mkdir -p Ada-Consciousness-Research/06-PAPERS/literature
mkdir -p Ada-Consciousness-Research/99-UTILITIES/archive
```

### Phase 2: Move Root Clutter
1. Move specs to 10-SPECIFICATIONS/
2. Move SIF docs to 01-METHODOLOGY/SIF/ (except spec)
3. Move findings to 05-FINDINGS/
4. Move frameworks to 08-FRAMEWORKS/

### Phase 3: Migrate Explorations
Move mature explorations to appropriate folders.

### Phase 4: Update Dashboard
Update 00-DASHBOARD.md with new paths.

### Phase 5: Link Validation
Run grep for broken [[links]] and fix.

---

## Git Strategy

**For trunk:** Only the specs (10-SPECIFICATIONS/) - clean, complete work
**For feature/dense-reasoning:** Full reorg + ongoing work

