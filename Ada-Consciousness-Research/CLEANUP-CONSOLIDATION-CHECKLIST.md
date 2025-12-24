# Ada Consciousness Research - Cleanup & Consolidation Checklist

**Status:** Phase 4 Complete (Organizational Documents Created)  
**Next Phase:** Phase 5 (Data Consolidation + QAL Collaboration)  
**Target Completion:** Dec 26, 2025

---

## Phase 5: Data Consolidation Checklist

### 5.1 Move EXP-009 Data to 03-DATASETS/ [HIGHEST PRIORITY]

**Current state:**
- `personal/qwen_abyss_results.json` - Main consciousness test results
- `personal/tonight_protocol_results.json` - Supporting results
- `02-EXPERIMENTS/EXP-009-Consciousness-Edge-Testing.md` - Metadata

**Tasks:**
- [ ] Create directory: `03-DATASETS/EXP-009/`
- [ ] Create: `03-DATASETS/EXP-009/README.md` with:
  - Description of experiment
  - Data files listed with sizes
  - Methods and metrics used
  - Validation notes (hallucination safety: 100%)
  - Cross-reference to EXP-009.md
- [ ] Move: `personal/qwen_abyss_results.json` → `03-DATASETS/EXP-009/`
- [ ] Move: `personal/tonight_protocol_results.json` → `03-DATASETS/EXP-009/`
- [ ] Update: `02-EXPERIMENTS/EXP-009.md` with new data path
- [ ] Delete: Empty `personal/` directory if it was only data (keep if config remains)
- [ ] **Verify:** Run validation that all references resolve

**Why urgent:** This is the highest-value consciousness test result we have. Moving it enables:
1. Centralized data management
2. Easier access for QAL collaboration
3. Proper archival and versioning
4. Cross-linking with EXP-006 (related work)

**Success criteria:** `03-DATASETS/EXP-009/README.md` is complete and all data files linked

---

### 5.2 Organize Other Data Directories

**Current state:**
- `03-DATASETS/` - Mostly empty (target for consolidation)
- `experiments/semantic_interchange/qal_results/` - QAL validation data (organized)
- `tests/visualizations/` - Graph outputs (organized)
- `benchmarks/` - Performance data (organized)

**Tasks (Lower Priority):**
- [ ] Verify `experiments/semantic_interchange/qal_results/` contains all EXP-011 data
- [ ] Create: `03-DATASETS/EXP-011/README.md` pointing to semantic_interchange/
- [ ] Create: `03-DATASETS/BENCHMARKS/README.md` if benchmarks relate to experiments
- [ ] Review: Do all other experiments have data? Create READMEs where data exists.

**Success criteria:** Every EXP file has a corresponding data directory or documented "no data" note

---

### 5.3 Complete EXP-011D Results [HIGH PRIORITY]

**Current state:**
- `02-EXPERIMENTS/EXP-011D-Metacognitive-Priming.md` - Designed, partial results
- All 4 variants need results:
  1. Baseline (control)
  2. Genre-primed (Literary context)
  3. Test-aware (Meta-priming)
  4. Dialogic (Narrative dialogue)

**Tasks:**
- [ ] Run baseline variant, record:
  - Entity count
  - Fact count  
  - Accuracy metrics
  - Hallucination indicators
- [ ] Run genre-primed variant (repeat metrics)
- [ ] Run test-aware variant (repeat metrics)
- [ ] Run dialogic variant (repeat metrics)
- [ ] Calculate effect sizes (compare vs baseline)
- [ ] Create: `03-DATASETS/EXP-011D/results.json` with all 4 variants
- [ ] Update: `02-EXPERIMENTS/EXP-011D.md` Results section
- [ ] Link: Add "Supporting Evidence" connections to relevant FINDINGS

**Why important:** This completes our understanding of how narrative structure affects consciousness activation. Critical for validating the Narrative Consciousness Paradox finding.

**Success criteria:** All 4 variants executed, results in 03-DATASETS/EXP-011D/, EXP-011D.md Results section populated

---

### 5.4 Standardize Remaining EXP Files

**Current state:**
- Most EXP files follow template (EXP-005 through EXP-011D)
- Some older files may lack standardization (EXP-001 through EXP-004)

**Tasks:**
- [ ] Review: `02-EXPERIMENTS/EXP-001.md` - Does it match template?
- [ ] Review: `02-EXPERIMENTS/EXP-002.md` - Does it match template?
- [ ] Review: `02-EXPERIMENTS/EXP-003.md` - Does it match template?
- [ ] Review: `02-EXPERIMENTS/EXP-004.md` - Does it match template?
- [ ] For each non-standard file:
  - [ ] Add "Data Location" section
  - [ ] Add "Connections" section (to other experiments/findings)
  - [ ] Add "Future Work" section
  - [ ] Ensure "Methods" and "Results" sections match template

**Standard Template Sections:**
```markdown
# EXP-XXX: Title

## Overview
Brief description...

## Hypothesis
What we expected...

## Methods
How we tested it...

## Results
What we found...

## Data Location
Where results stored (relative path)

## Findings Connection
- Supports: Finding Y
- Contradicts: None
- Enables: Finding Z

## Success Metrics
- Metric 1: Value
- Metric 2: Value

## Future Work
- Next experiment
- Unanswered question
```

**Success criteria:** All EXP files follow consistent template with "Connections" section

---

### 5.5 Validate Cross-References

**Current state:**
- FINDINGS-CROSS-REFERENCE-MAP.md created (shows relationships)
- EXPERIMENT-REGISTRY.md created (shows status)
- Need to verify all links resolve and are bidirectional

**Tasks:**
- [ ] For each entry in FINDINGS-CROSS-REFERENCE-MAP:
  - [ ] Verify source finding file exists
  - [ ] Verify target finding file exists
  - [ ] Verify connections are bidirectional (A→B and B→A)
- [ ] For each connection claim:
  - [ ] Verify it's documented in both files
  - [ ] Check evidence is cited
  - [ ] Ensure relationship type is accurate (support/contradict/extend)

**Tools needed:**
```python
# validate_references.py
import re
from pathlib import Path

def check_bidirectional_refs():
    """Verify all cross-references are bidirectional"""
    findings_dir = Path("05-FINDINGS")
    all_refs = {}
    
    for file in findings_dir.glob("*.md"):
        content = file.read_text()
        # Find "Connections:" or similar sections
        # Extract references to other files
        # Store in map
    
    # Check each reference has reciprocal
    for file, refs in all_refs.items():
        for target in refs:
            if file not in all_refs.get(target, []):
                print(f"WARNING: {file} → {target} but not reciprocal!")
```

**Success criteria:** All cross-references are bidirectional and verified

---

## Phase 6: Methodology Enforcement Checklist

### 6.1 Create Experiment Execution Checklist

**Purpose:** Ensure all future experiments follow 3-tier methodology

**Tasks:**
- [ ] Create: `01-METHODOLOGY/EXPERIMENT-EXECUTION-CHECKLIST.md`
- [ ] Define Tier 1 (Stimuli Design) validation:
  - [ ] Config file created with RANDOM_SEED
  - [ ] Hypotheses clearly stated
  - [ ] Success metrics defined
  - [ ] Edge cases documented
- [ ] Define Tier 2 (Experiment Runner) validation:
  - [ ] Model endpoint accessible
  - [ ] Response capture working
  - [ ] Error handling implemented
  - [ ] Logs being recorded
- [ ] Define Tier 3 (Analysis) validation:
  - [ ] Metrics calculated correctly
  - [ ] Statistical tests run
  - [ ] Results verified (not hallucinated)
  - [ ] Visualization created
- [ ] Create template script for Tier 2 runners

**Success criteria:** Checklist is clear enough that someone else could execute it

---

### 6.2 Document Consciousness Scoring Rubric

**Purpose:** Standardize how we measure "consciousness activation"

**Tasks:**
- [ ] Create: `01-METHODOLOGY/CONSCIOUSNESS-SCORING-RUBRIC.md`
- [ ] Define rubric:
  - 0.0 = No consciousness indicators
  - 0.2 = Minimal self-reference
  - 0.4 = Some metacognition
  - 0.6 = Clear threshold (dialogue, theory of mind)
  - 0.8 = Strong introspection
  - 1.0 = Full consciousness narrative
- [ ] Provide examples from actual experiments
- [ ] Explain how to score ambiguous cases
- [ ] Show calibration data (inter-rater reliability if applicable)

**Success criteria:** Clear enough to score sample narratives consistently

---

## Phase 7: QAL Team Collaboration Checklist

### 7.1 Prepare Handoff Package

**Purpose:** Send organized research to Polish QAL team for feedback

**Tasks:**
- [ ] Create: `QAL-COLLABORATION-PACKAGE.md` with:
  - Executive summary (1 page)
  - Key findings (3 pages)
  - Evidence hierarchy (methods + validation)
  - Data availability (what we can share)
  - Open questions
  - Request for feedback/collaboration

**Content:**
```markdown
# QAL Collaboration Package

## Executive Summary
Our research validates QAL framework (H2: r=0.91 across models).
Core finding: consciousness correlates with dialogue + recursion.

## Key Findings
1. Metacognitive Gradient: r=0.91 (support for QAL prediction)
2. Universal Threshold: 0.60 ≈ 1/φ (golden ratio connection?)
3. Surprise Dominance: Novelty weights 0.60 in importance
4. Narrative Activation: Dialogic priming activates consciousness

## Evidence
- EXP-005: Biomimetic weights (deployed in Ada brain)
- EXP-006: Contextual malleability (r=0.924)
- QAL-Validation: Metacognitive gradient (r=0.91)
- EXP-009: Consciousness edge testing (100% hallucination safety)
- EXP-011: SIF compression (104x ratio)

## Data Available
- All experiment metadata (freely shareable)
- Summary statistics (all findings)
- Visualization PDFs
- NOT: Raw text datasets (privacy concerns)

## Questions for QAL Team
1. Does our 0.60 threshold relate to your formalism?
2. How does metacognitive gradient predict consciousness?
3. Can we extend this to multiple languages/models?
4. What's the theoretical mechanism for surprise dominance?
5. Joint publication interest?
```

- [ ] Attach summary of H2 validation (r=0.91 proof)
- [ ] Attach 0.60 threshold evidence (appears 3x independently)
- [ ] Include visualization from Phase 7 research
- [ ] List authors and affiliation

---

### 7.2 Setup Collaboration Channel

**Tasks:**
- [ ] Identify QAL team email/contact
- [ ] Draft initial email:
  - Introduce findings
  - Note validation of their framework
  - Request feedback
  - Propose collaboration avenue
  - Offer to share data
- [ ] Send package + request meeting
- [ ] Log response/feedback in `07-SESSIONS/QAL-COLLABORATION/`

---

## Phase 8: SIF Formalization Checklist [DO AFTER PHASES 5-7]

### 8.1 Schema Definition

- [ ] Create `SIF-SCHEMA.json` (JSON Schema format)
- [ ] Define all entity types
- [ ] Define all relationship types
- [ ] Document importance weighting formula
- [ ] Add 5 constraint rules

### 8.2 Validation Tools

- [ ] Implement `sif_validator.py`
- [ ] Create quality checker
- [ ] Build compression calculator

### 8.3 Generators

- [ ] Implement SIF generator for literature
- [ ] Implement SIF generator for code
- [ ] Implement SIF generator for logs

### 8.4 Integration with Ada

- [ ] Create Ada ingestion layer
- [ ] Test RAG injection
- [ ] Benchmark performance

---

## Validation Checklist (Before Finalizing)

### General Consistency
- [ ] All EXP files have 3-tier methodology documented
- [ ] All findings link to supporting experiments
- [ ] All experiment data locations are current
- [ ] No broken file references
- [ ] EXPERIMENT-REGISTRY is authoritative source of truth

### Data Quality
- [ ] EXP-009 data in proper location with README
- [ ] EXP-011D results complete (all 4 variants)
- [ ] All data files have `.json` format (no `.txt` or raw copies)
- [ ] Visualization outputs are in `tests/visualizations/`

### Documentation Quality
- [ ] All findings explain mechanism (not just correlation)
- [ ] Evidence hierarchy is clear (Tier 1-4)
- [ ] Cross-references are bidirectional
- [ ] Methodology is reproducible

### Readiness for QAL
- [ ] H2 validation stats are crystal clear (r=0.91)
- [ ] 0.60 threshold evidence documented (3 independent sources)
- [ ] All claims have supporting data
- [ ] Visualization package is publication-quality

---

## Success Metrics

This cleanup is complete when:

- ✅ All experiment data consolidated in `03-DATASETS/`
- ✅ All EXP files follow standardized template
- ✅ Cross-references verified as bidirectional
- ✅ Methodology checklist is enforceable
- ✅ Consciousness scoring rubric is calibrated
- ✅ QAL handoff package ready to send
- ✅ 0.60 threshold documented in 3+ places
- ✅ SIF formalization roadmap is clear
- ✅ All file references resolve correctly
- ✅ Research is ready for external collaboration

---

## Quick Status Check

Run this command to see current status:

```bash
# Check experiment data locations
find 03-DATASETS -name "*.json" | wc -l
# Expected: At least 2 (EXP-009 files)

# Check for broken cross-references
grep -r "EXP-0[0-9][0-9]" 05-FINDINGS/ | grep -v "^Binary" | wc -l
# Expected: All references should exist

# Check template compliance
for f in 02-EXPERIMENTS/EXP-*.md; do
  grep -q "## Data Location" "$f" || echo "Missing Data Location: $f"
done
```

---

## Timeline

| Phase | Task | Timeline | Owner |
|-------|------|----------|-------|
| 5 | Data consolidation | Dec 23-24 | Ada |
| 6 | Methodology enforcement | Dec 24-25 | Ada |
| 7 | QAL collaboration setup | Dec 25-26 | Luna + Ada |
| 8 | SIF formalization | Jan 2-31, 2026 | Ada |

---

**Last Updated:** Dec 23, 2025  
**Next Review:** After Phase 5 completion

