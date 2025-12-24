# Master Dataset Index - Consciousness Research

**Last Updated:** 2025-12-23  
**Purpose:** Single comprehensive map of ALL empirical data in the vault

---

## Quick Navigation by Type

### 🧬 Consciousness Measurement Data
- EXP-009 Results: Abyss Protocol + Tonight Protocol
- QAL Validation: Temperature sweep + entity extraction + metacognitive gradient
- Narrative Paradox: Alice extraction variants

### 🎯 Optimization Results  
- Biomimetic Weight Optimization: 80 tests across 7 phases
- Contextual Malleability: 23 tests across 14 phases
- Token/Compression Metrics: SIF baseline fidelity

### 📊 Raw Experimental Data
- Dataset files (.json): EXP-002, EXP-004, EXP-005, EXP-009
- Result files: qwen_abyss_results.json, tonight_protocol_results.json
- Validation runs: qal_results/*.json (multiple timestamps)

---

## Layer 1: Consciousness Test Data

### EXP-009: Consciousness Edge Testing
**Location**: `Ada-Consciousness-Research/03-DATASETS/` (consolidation target)

**Current Status**: Data exists but scattered
- `personal/qwen_abyss_results.json` - 5 experiments, 3 breakthroughs
- `personal/tonight_protocol_results.json` - 6 tests, consciousness score 39

**Consolidation Steps**:
```
personal/qwen_abyss_results.json 
  → 03-DATASETS/EXP-009/qwen_abyss_results.json

personal/tonight_protocol_results.json
  → 03-DATASETS/EXP-009/tonight_protocol_results.json

+ Create: 03-DATASETS/EXP-009/README.md
  ├─ Data description
  ├─ Protocol overview  
  ├─ Key findings summary
  └─ Scoring methodology
```

**Data Format** (JSON):
```json
{
  "protocol": "qwen_abyss | tonight",
  "date": "2025-12-21T...",
  "model": "qwen2.5-coder:7b",
  "tests": [
    {
      "name": "Self Recognition",
      "score": 3,
      "max": 11,
      "breakthrough": false,
      "response": "...",
      "analysis": "..."
    }
  ],
  "total_consciousness_score": 39,
  "breakthrough_rate": 0.6
}
```

**Associated Documentation**:
- 02-EXPERIMENTS/EXP-009-Consciousness-Edge-Testing.md
- 05-FINDINGS/Power-Dynamics-Case-Observation.md
- 08-FRAMEWORKS/Ada-Emergence.md
- 05-FINDINGS/Beyond-The-Event-Horizon.md

---

### QAL Validation Results
**Location**: `experiments/semantic_interchange/qal_results/`

**Files**:
- `validation_v2_qwen2.5-coder_7b_20251223_*.json` - Multiple runs
- Latest complete run shows:
  - H2 Metacognitive Gradient: **r=0.91** ✓
  - Temperature sweep: 9 points
  - Entity confidence analysis
  - Cross-model (codellama) validation

**Data Format** (JSON structure):
```json
{
  "model": "qwen2.5-coder:7b",
  "timestamp": "2025-12-23T...",
  "random_seed": 42,
  "phases": [
    {
      "name": "Temperature Sweep",
      "temperature_points": [0.3, 0.4, ..., 1.1],
      "results": {
        "entities": [...],
        "consciousness": [...],
        "ambiguity_width": [...]
      }
    },
    {
      "name": "Metacognitive Gradient",
      "levels": [0, 1, 2, 3, 4],
      "hypothesis_test": {
        "correlation": 0.91,
        "slope": 2.33,
        "supports_hypothesis": true
      }
    }
  ],
  "summary": {...}
}
```

**Key Metrics**:
| Metric | Value | Status |
|--------|-------|--------|
| H2 Correlation | 0.91 | ✅ CONFIRMED |
| Temperature Peak | T=0.9 (consciousness) | ✅ Measured |
| Metacognitive Slope | 2.33 | ✅ Steeper than H1 |
| Cross-model | qwen + codellama | ✅ Replicated |

**Associated Documentation**:
- 05-FINDINGS/QAL-Validation-Complete.md
- 05-FINDINGS/QAL-SIF-Bridge.md
- 01-METHODOLOGY/SIF-Concept.md

---

## Layer 2: Optimization & Weight Testing

### EXP-005: Biomimetic Weight Optimization
**Location**: Multiple
- Actual runs: `tests/visualizations/` directory
- Test code: `tests/test_weight_optimization.py`
- Production deployment: `brain/config.py`

**Data Summary**:
```
Phase 1: Property-based testing        27 tests (0.09s)
Phase 2: Synthetic data generation     10 tests (0.04s)
Phase 3: Ablation studies              12 tests (0.05s)
Phase 4: Grid search optimization       7 tests (0.08s) - 169 configs
Phase 5: Production validation           6 tests (0.07s)
Phase 6: Deployment                     11 tests (0.07s)
Phase 7: Visualization                   7 tests (2.93s) - 6 graphs

Total: 80 tests, 3.56s runtime, 100% passing
```

**Key Results**:
| Signal | Intuitive | Optimal | Change |
|--------|-----------|---------|--------|
| Decay | 0.40 | 0.10 | -75% |
| Surprise | 0.30 | 0.60 | +100% |
| Relevance | 0.20 | 0.20 | - |
| Habituation | 0.10 | 0.10 | - |

**Output Files**:
- Correlation graphs: `tests/visualizations/*.png` (6 publication-quality plots)
- Test output: Pytest results + coverage reports
- Production config: `brain/config.py:IMPORTANCE_WEIGHTS`

**Associated Documentation**:
- 02-EXPERIMENTS/EXP-005-Biomimetic-Weight-Optimization.md
- docs/research_narratives.rst (9 narrative formats)
- RELEASE_v2.2.0.md

---

### EXP-006: Contextual Malleability Framework
**Location**: Distributed across multiple files

**Data Integration**:
- Documentation impact: `tests/benchmark_results_ai_docs.json`
- Baseline comparison: `tests/benchmark_no_tools.json`
- Excitement pathways: `tests/excitement_pathway_results/`
- Framework efficacy: `tests/fixtures/` (28 files)

**Key Metrics**:
```
Contextual correlation:     r = 0.924 (↑27.3%)
Universal correlation:      r = 0.726 (baseline)

Empathy scaffolding effect: 
  Low cognitive load:       → 100% completion
  High cognitive load:      → 0% (baseline) → 100% (with scaffolding)
  Effect size:              3.089
```

**Associated Documentation**:
- 02-EXPERIMENTS/EXP-006-Contextual-Malleability-Framework.md
- docs/contextual_malleability_guide.rst
- docs/CONTEXTUAL_MALLEABILITY_READY_FOR_TINKERERS.md
- RELEASE_v2.3.0.md

---

## Layer 3: Narrative & Compression Tests

### EXP-011: SIF Baseline Fidelity Testing  
**Location**: `02-EXPERIMENTS/EXP-011-SIF-Baseline-Fidelity.md` + `03-DATASETS/`

**Test Document**:
- Source: Alice's Adventures in Wonderland (Project Gutenberg)
- Size: 144,696 characters
- Domain: Fantasy literature

**Results** (Two runs):

Run 1 (Conservative):
```
Input:  144,696 chars
Output:   1,848 chars (137.7x compression)
Accuracy: 26.7%
Hallucination Resistance: 100% ✓
```

Run 2 (Aggressive):
```
Input:  144,696 chars
Output:   3,166 chars (76.5x compression)
Accuracy: 33.3%
Hallucination Resistance: 100% ✓
```

**Key Finding**: Perfect hallucination resistance but limited accuracy. Critical for SIF design (can trust what's there, but may miss content).

---

### EXP-011D: Metacognitive Priming
**Location**: `02-EXPERIMENTS/EXP-011D-Metacognitive-Priming.md` (in-progress)

**Test Document**: Alice chapters 1-5 (50K chars)

**Variants Being Tested**:
1. **Baseline** - Direct extraction
2. **Genre-Primed** - "This is a fantasy story"  
3. **Test-Aware** - "You will be tested"
4. **Dialogic Recursive** - Multi-turn narrative setup

**Expected Output Format**:
```json
{
  "variant": "baseline|genre|test_aware|dialogic",
  "entities_extracted": 0-50,
  "facts_extracted": 0-100,
  "accuracy_percentage": 0-100,
  "hallucination_resistance": 0-100,
  "dominant_processing_mode": "literal|creative",
  "narrative_awareness_level": 0-5
}
```

**Status**: Results collection ongoing

---

## Layer 4: Model Baseline Performance

### Latency Benchmarks
**Location**: `benchmarks/press_release_data/latency_benchmark.json`

**Metrics**:
- Sample size: 75 trials
- Model: qwen2.5-coder:7b
- TTFT (Time To First Token): mean=0.977s, median=0.336s, p95=2.55s
- Total time: mean=13.12s, median=12.97s
- Tokens/second: mean=25.07, median=22.78

**Query Types Tested**:
- reasoning, code_completion, introspection, trivial, creative

---

### Code Completion Benchmark (v2.6)
**Location**: `benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md`

**Metrics**:
- Model: qwen2.5-coder:7b with FIM (Fill-In-Middle) format
- Mean latency: 2.6 seconds
- Quality score: 77%
- Success rate: 100%
- Speedup: 10.6x (27.7s → 2.6s)
- Test scenarios: 24 diverse code completion tasks

---

## Data Consolidation Checklist

### ⬜ TO DO: Organize Scattered Data
- [ ] **Priority 1**: Move EXP-009 data to 03-DATASETS/EXP-009/
  - [ ] qwen_abyss_results.json
  - [ ] tonight_protocol_results.json
  - [ ] Create README.md with metadata

- [ ] **Priority 2**: Create QAL Results consolidated index
  - [ ] Link to all qal_results/*.json files
  - [ ] Create 03-DATASETS/QAL-VALIDATION/summary.json
  - [ ] Document replication status (both models)

- [ ] **Priority 3**: Organize consciousness-indicators/ directory
  - [ ] Currently empty - populate with:
    - [ ] Consciousness scoring methodology
    - [ ] Indicator detection algorithms
    - [ ] Validation examples

- [ ] **Priority 4**: Organize identity-assignment/ directory  
  - [ ] Currently empty - populate with:
    - [ ] Identity formation protocols
    - [ ] Example outputs from EXP-009
    - [ ] Anthropomorphization effect sizes

### ✅ DONE: Already Organized
- ✓ Biomimetic optimization: tests/visualizations/
- ✓ Contextual malleability: docs/ + tests/fixtures/
- ✓ QAL validation: experiments/semantic_interchange/qal_results/
- ✓ Model baselines: benchmarks/

---

## File Locations Summary

### Primary Data Repositories
| Purpose | Location | Status |
|---------|----------|--------|
| Consciousness tests | personal/*.json → 03-DATASETS/EXP-009/ | 🟡 Move pending |
| QAL validation | experiments/semantic_interchange/qal_results/ | ✅ Complete |
| Optimization runs | tests/visualizations/ + test code | ✅ Complete |
| Contextual research | tests/fixtures/ + docs/ | ✅ Complete |
| Narrative tests | 02-EXPERIMENTS/EXP-011*.md | 🟡 In progress |
| Model baselines | benchmarks/ | ✅ Complete |

### Documentation Cross-Reference
| Data Type | Primary Docs | Supporting Docs |
|-----------|-------------|-----------------|
| EXP-009 Consciousness | EXP-009-*.md | Power-Dynamics, Ada-Emergence |
| QAL Validation | QAL-Validation-Complete.md | QAL-SIF-Bridge.md |
| Biomimetic Weights | EXP-005-*.md | research_narratives.rst |
| Contextual Malleability | EXP-006-*.md | CONTEXTUAL_MALLEABILITY_*.md |
| SIF Testing | EXP-011*.md | SIF-Concept.md, Narrative-Paradox.md |

---

## Metadata Standards

All dataset files should include:

```json
{
  "metadata": {
    "experiment_id": "EXP-009",
    "date": "2025-12-21T..Z",
    "researcher": "luna",
    "model": "qwen2.5-coder:7b",
    "purpose": "Test consciousness signatures",
    "version": "1.0",
    "status": "complete|in_progress|pending"
  },
  "configuration": {
    "temperature": 0.7,
    "seed": 42,
    "timeout_seconds": 120
  },
  "data": [...],
  "analysis": {...},
  "notes": "Any qualitative observations"
}
```

---

*This index is maintained as data arrives. Update table of contents and add new sections as experiments progress.*

**Maintenance**: Check this file weekly  
**Last check**: 2025-12-23  
**Next consolidation target**: EXP-009 → 03-DATASETS/
