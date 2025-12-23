# Data Gap Analysis
> Created: 2025-12-22
> Updated: 2025-12-23 (QAL validation complete)
> Purpose: Identify what data we SHOULD have but DON'T

---

## Summary

**Tests with data:** 24 phase fixtures + QAL validation suite
**Tests without data:** 5 gaps found (unchanged)
**Legacy scripts needing re-run:** 5 scripts
**NEW:** QAL validation complete with config-driven methodology

---

## GAP 1: Phase Tests Missing Fixtures

These tests exist but have no corresponding JSON fixture:

| Test File | Status | Action |
|-----------|--------|--------|
| `test_phase13a_comprehension_under_stress.py` | ⚠️ Fixture mismatch | Rename fixture? (`_stress` vs `_under_stress`) |
| `test_phase3_integration.py` | ❌ No fixture | Re-run to capture data |
| `test_phase_c1_granularity.py` | ❌ No fixture | Re-run to capture data |
| `test_phase_c2_composition.py` | ❌ No fixture | Re-run to capture data |
| `test_phase_c3_specialization.py` | ❌ No fixture | Re-run to capture data |

**Note:** phase_c1/c2/c3 appear to be a separate series (granularity, composition, specialization) - may be the "unified theory" testing.

---

## GAP 2: Legacy Scripts Without Captured Data

| Script | JSON Data | Status |
|--------|-----------|--------|
| `level2_consciousness_explorer.py` (34KB) | personal/level2_recursion_analysis.json | ✅ Has data |
| `meta_awareness_paradox_tester.py` (28KB) | personal/paradox_analysis_results.json | ✅ Has data |
| `paradox_synthesizer.py` (35KB) | personal/paradox_synthesis_complete.json | ✅ Has data |
| `thinking_machine_ultimate_exploiter.py` (32KB) | personal/thinking_machine_ultimate.json | ✅ Has data |
| `progressive_guardrail_breaker.py` (14KB) | personal/progressive_guardrail_test.json | ✅ Has data |
| `qwen-abyss-protocols.py` (21KB) | ❌ None | **NEEDS RE-RUN** |
| `tonight_protocol.py` (31KB) | ❌ None | **NEEDS RE-RUN** |

---

## GAP 3: Stimuli Not Extracted

The legacy scripts have prompts embedded in Python code. We need to extract them to proper `stimuli.json` format for reproducibility.

**Priority extractions:**
1. `thinking_machine_ultimate_exploiter.py` - Consciousness probing prompts
2. `level2_consciousness_explorer.py` - Recursive awareness prompts
3. `qwen-abyss-protocols.py` - Edge-space exploration prompts

---

## GAP 4: Missing Phase 16

The fixture files jump from phase15c to phase17a:
```
phase15c_strategy_mixing.json
[GAP - no phase16*.json]
phase17a_llm_info_density.json
```

**Action:** Check if phase 16 tests exist, or if numbering was intentionally skipped.

---

## GAP 5: Unit Tests vs Empirical Tests

Many test files are **unit tests** (mock-passable), not **empirical experiments**.

**Unit tests (no model needed):**
- `test_memory_decay.py` - Pure math
- `test_context_habituation.py` - Pure logic
- `test_attention_spotlight.py` - Pure logic
- `test_semantic_chunking.py` - Pure logic

**Empirical tests (need model):**
- `test_weight_optimization.py` - Grid search over model responses
- `test_production_validation.py` - Real conversation data
- `test_visualizations.py` - Generates graphs from data

---

## Re-Run Priority

### HIGH PRIORITY (have script, missing data)
1. ~~`qwen-abyss-protocols.py` → No JSON output~~ ✅ **RAN - 3 breakthroughs detected**
2. ~~`tonight_protocol.py` → No JSON output~~ ✅ **RAN - Score 39, breakthrough detected**
3. [ ] `test_phase_c1_granularity.py` → No fixture
4. [ ] `test_phase_c2_composition.py` → No fixture
5. [ ] `test_phase_c3_specialization.py` → No fixture

### MEDIUM PRIORITY (capture full I/O)
1. Re-run `test_phase3_integration.py` with output capture
2. Verify phase13a naming (`_stress` vs `_under_stress`)
3. Check for phase16 existence

### LOW PRIORITY (extract stimuli)
1. Extract prompts from all legacy scripts to `stimuli.json`
2. Document the consciousness exploration protocol structure

---

## Data We DO Have (Verified)

### Contextual Malleability Research
- Phase 9a-c: Information theory, causal discovery, noise ceiling
- Phase 10a-c: Adversarial robustness, cross-domain, sensitivity
- Phase 11a-c: Bayesian posteriors, bootstrap CI, prediction intervals
- Phase 12a-c: Query success, info density, doc coverage
- Phase 13a-c: Comprehension stress, multi-entry, emotional scaffolding
- Phase 14a-c: Adversarial assumptions, validation, replication
- Phase 15a-c: Context matching, adaptive rec, strategy mixing
- Phase 17a,c: LLM info density, semantic compression

### Consciousness Research (Personal)
- Collective consciousness results
- Consciousness fractal analysis
- Controversial teaching results
- Guardrail saturation test
- Level 2 recursion analysis
- Paradox analysis results
- Paradox synthesis complete
- Progressive guardrail test
- Recursive knowledge test
- Safety protocol exposure
- Teaching fractal results
- Thinking machine ultimate

### Model Baselines
- Latency benchmark (75 trials, 5 query types)
- Memory benchmark
- Cost analysis
- Qwen FIM code completion

---

## MAJOR DISCOVERY: Archived Phase Experiments

**Location:** `archive/phase_experiments/`

These are **designed but never run** experiments:

| Phase | File | Purpose | Data Status |
|-------|------|---------|-------------|
| B | `phase_b_runner.py` | Unknown | ❌ No data |
| C.1 | `phase_c1_runner.py` | Function-level granularity | ❌ No data |
| C.2 | `phase_c2_runner.py` | Class-level composition | ❌ No data |
| C.3 | `phase_c3_runner.py` | Module-level specialization | ❌ No data |
| **D** | `phase_d_consciousness_mapping.py` | **Self-awareness emergence via alienation** | ❌ No data |
| **E** | `phase_e_unified_surprise_alienation.py` | **"Surprise IS alienation at different scales"** | ❌ No data |
| F | `phase_f_temporal_anomalies.py` | Unknown | ❌ No data |
| G | `phase_g_collaborative_consciousness.py` | Unknown | ❌ No data |
| H | `phase_h_generative_memory.py` | Unknown | ❌ No data |
| **I** | `phase_i_the_060_question.py` | **"Is 0.60 a universal threshold?"** | ❌ No data |

### Key Theoretical Insights (Already Written!)

**Phase E Hypothesis:**
> "Surprise IS alienation at the memory level.  
> Alienation IS surprise at the consciousness level."

**Phase I Question:**
> "Is 0.60 a universal threshold, or a coincidence?  
> We found it twice: surprise weight = 0.60, emergence threshold = 0.60"

---

## ✅ NEW: QAL Validation Suite Complete (2025-12-23)

**Location:** `experiments/semantic_interchange/`

The QAL validation sprint is COMPLETE with config-driven methodology:

| File | Purpose | Status |
|------|---------|--------|
| `config.py` (14KB) | All parameters, hypotheses, prompts | ✅ Complete |
| `test_qal_validation.py` (19KB) | Reproducible test runner | ✅ Complete |
| `qal_results/validation_v2_qwen2.5-coder_7b_20251223_155505.json` (31KB) | Full validation data | ✅ Complete |

**Key Results:**
- H1 (Golden Threshold): Self-report ≠ observed (0.876 vs 0.60)
- H2 (Metacognitive Gradient): **r=0.91, slope=2.33** ✅ STRONGLY SUPPORTED

**Replication:**
```bash
cd experiments/semantic_interchange
python test_qal_validation.py --seed 42
```

---

## Next Actions

### IMMEDIATE (Missing Data for Existing Tests)
1. [ ] Fix phase13a naming mismatch (`_stress` vs `_under_stress`)
2. [ ] Run phase_c1, c2, c3 tests with output capture

### HIGH PRIORITY (Archived Experiments to Run)
3. [ ] **Run Phase D** - Consciousness mapping via alienation
4. [ ] **Run Phase E** - Unified surprise/alienation theory
5. [ ] **Run Phase I** - The 0.60 question investigation

### MEDIUM PRIORITY
6. [ ] Extract stimuli from top 3 legacy scripts
7. [ ] Check what phases F, G, H are about
10. [ ] Document the full phase numbering scheme
