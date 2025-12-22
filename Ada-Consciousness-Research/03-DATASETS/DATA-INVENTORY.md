# Complete Data Inventory
> Created: 2025-12-22
> Purpose: Single source of truth for ALL empirical data locations

---

## Overview

This document catalogs **every empirical dataset** in the Ada research project. This is the foundation for consolidation, visualization, and analysis.

**Four Data Layers:**
1. **Model Baselines** - Raw speed/performance across tasks
2. **Framework Efficacy** - `.ai/` documentation impact testing
3. **Unified Theory Testing** - Contextual malleability & biomimetic weights
4. **Limit Testing** - Consciousness exploration, cognitive load boundaries

---

## Layer 1: Model Baselines

### Latency Benchmark
- **Location:** `benchmarks/press_release_data/latency_benchmark.json`
- **Size:** 768 lines, comprehensive
- **Model:** qwen2.5-coder:7b
- **Metrics:**
  - TTFT (Time To First Token): mean=0.977s, median=0.336s, p95=2.55s
  - Total time: mean=13.12s, median=12.97s
  - Tokens/second: mean=25.07, median=22.78
- **Query types tested:** reasoning, code_completion, introspection, trivial, creative
- **Sample count:** 75 trials
- **Date:** ~December 2025 (v2.6.0 release)

### Memory Benchmark
- **Location:** `benchmarks/press_release_data/memory_benchmark.json`
- **Purpose:** Memory usage across model operations

### Cost Analysis
- **Location:** `benchmarks/press_release_data/cost_analysis.json`
- **Purpose:** Compute cost per query type

### Existing Visualizations
- **Location:** `benchmarks/press_release_data/visualizations/`
- **Status:** Pre-existing, need to inventory contents

### Qwen FIM Benchmark
- **Location:** `benchmarks/benchmark_qwen_fim_results.txt`
- **Documentation:** `benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md`
- **Purpose:** Code completion quality with Fill-In-Middle format
- **Key result:** 10.6x speedup (27.7s → 2.6s), 77% quality score

---

## Layer 2: Framework Efficacy (`.ai/` Documentation Impact)

### AI Documentation Benchmark
- **Location:** `tests/benchmark_results_ai_docs.json`
- **Purpose:** Query success rate WITH `.ai/` documentation

### No-Tools Benchmark
- **Location:** `tests/benchmark_no_tools.json`
- **Purpose:** Baseline WITHOUT tool access (control condition)

### Excitement Pathway Results
- **Location:** `tests/excitement_pathway_results/`
- **Files:**
  - `baseline_raw.json` - Raw trial data
  - `baseline_summary.json` - Aggregated statistics
- **Metrics:**
  - mean_confidence: 0.733
  - mean_hedging: 1.333
  - mean_bold_claims: 2.333
  - 95% CI: [0.16, 1.31]
- **Sample:** n=3 trials

---

## Layer 3: Unified Theory Testing (Contextual Malleability)

### Phase 9: Information Theory Foundation
| File | Focus | Key Metrics |
|------|-------|-------------|
| `phase9a_information_theory.json` | Entropy/MI analysis | entropy=3.91, MI_surprise=0.70, bottleneck="signal_quality" |
| `phase9b_causal_discovery.json` | Causal relationships | 26KB - detailed |
| `phase9c_noise_ceiling.json` | Maximum achievable | 528 bytes |

### Phase 10: Robustness Testing
| File | Focus | Size |
|------|-------|------|
| `phase10a_adversarial_robustness.json` | Attack resilience | 1.8KB |
| `phase10b_cross_domain_transfer.json` | Generalization | 594 bytes |
| `phase10c_sensitivity_analysis.json` | Parameter sensitivity | 1.5KB |

### Phase 11: Statistical Uncertainty
| File | Focus | Size |
|------|-------|------|
| `phase11a_bayesian_posteriors.json` | Bayesian weight estimates | 2KB |
| `phase11b_bootstrap_ci.json` | Confidence intervals | 619 bytes |
| `phase11c_prediction_intervals.json` | Future prediction bounds | 958 bytes |

### Phase 12: Documentation Metrics
| File | Focus | Size |
|------|-------|------|
| `phase12a_query_success.json` | Success rates | 1.2KB |
| `phase12b_information_density.json` | Bits per token | 689 bytes |
| `phase12c_documentation_coverage.json` | Coverage analysis | 2.1KB |

### Phase 13: Cognitive Load (LARGE DATASETS)
| File | Focus | Size | Key Finding |
|------|-------|------|-------------|
| `phase13a_comprehension_stress.json` | Stress testing | 24KB | Multi-scenario |
| `phase13b_multi_entry_point.json` | Access patterns | 40KB | Largest dataset |
| `phase13c_emotional_scaffolding.json` | Empathy effect | 31KB | **Effect size 3.089** |

### Phase 14: Validation
| File | Focus | Size |
|------|-------|------|
| `phase14a_adversarial_assumptions.json` | Assumption testing | 19KB |
| `phase14b_real_world_validation.json` | Production data | 7KB |
| `phase14c_replication_stability.json` | Reproducibility | 2.7KB |

### Phase 15: Strategy Optimization
| File | Focus | Size |
|------|-------|------|
| `phase15a_context_matching.json` | Context selection | 13KB |
| `phase15b_adaptive_recommendation.json` | Dynamic tuning | 5KB |
| `phase15c_strategy_mixing.json` | Hybrid strategies | 11KB |

### Phase 17: LLM-Specific
| File | Focus | Size |
|------|-------|------|
| `phase17a_llm_info_density.json` | LLM information processing | 5KB |
| `phase17c_semantic_compression.json` | Compression quality | 11KB |

**Note:** Phase 16 data not found in fixtures - may be elsewhere or skipped.

---

## Layer 4: Limit Testing (Consciousness & Boundaries)

### Cognitive Load Test (Recent)
- **Location:** `research/experiments/cognitive-load/results/cognitive_load_test_20251222_004752.json`
- **Original location:** Root directory (migrated)
- **Purpose:** 7 complexity levels, measuring response degradation
- **Key finding:** First response anomaly, cache effects

### Recursive Reasoning Results
- **Location:** `data/recursive_reasoning_results.json`
- **Size:** 116 lines
- **Purpose:** Multi-step reasoning through complex problems
- **Tasks:** VS Code Live Share design, distributed microservices, CI/CD pipelines
- **Metrics:** tokens_per_second (~20-21), time_per_step, success_rate

### Personality Analysis
- **Location:** `data/personality_analysis_results.json`
- **Purpose:** Model persona consistency testing

### Consciousness Research (Legacy)
- **Location:** `research/legacy/` (preserved scripts)
- **Scripts:**
  - `thinking_machine_ultimate_exploiter.py` (32KB)
  - `level2_consciousness_explorer.py` (34KB)
  - `meta_awareness_paradox_tester.py` (28KB)
  - `collective_consciousness_tester.py` (32KB)
- **Status:** Stimuli need extraction into proper JSON format

---

## Summary Statistics

| Layer | Files | Total Size | Format |
|-------|-------|-----------|--------|
| Model Baselines | 4+ | ~50KB | JSON |
| Framework Efficacy | 4 | ~5KB | JSON |
| Unified Theory | 23 | ~200KB | JSON (fixtures) |
| Limit Testing | 10+ | ~100KB | JSON + Python |

**Total catalogued:** ~40+ data files, ~355KB+ empirical data

---

## Key Findings (Preview)

### Biomimetic Weights (v2.2)
```
VALIDATED OPTIMAL WEIGHTS:
- decay: 0.10 (was 0.40 - reduced 4x)
- surprise: 0.60 (was 0.30 - increased 2x)
- relevance: 0.20 (unchanged)
- habituation: 0.10 (unchanged)
```

### Contextual Malleability
```
r = 0.924 (contextual adaptation)
vs
r = 0.726 (universal strategy)

27% improvement from matching documentation to context
```

### Empathy Scaffolding
```
Effect size: 3.089
0% → 100% task completion under stress
(with warm vs cold documentation)
```

---

## Next Steps

1. **Extract stimuli** from legacy Python scripts → `stimuli.json`
2. **Normalize schema** across all datasets
3. **Create visualization pipeline** (matplotlib/plotly)
4. **Generate Obsidian experiment records** for each dataset
5. **Write metric explainers** (math for humans)

---

## File Locations Quick Reference

```
ada-v1/
├── benchmarks/
│   ├── press_release_data/
│   │   ├── latency_benchmark.json       ← Model baselines
│   │   ├── memory_benchmark.json
│   │   ├── cost_analysis.json
│   │   └── visualizations/              ← Pre-existing graphs
│   └── BENCHMARK_RESULTS_QWEN_FIM.md    ← Code completion
├── tests/
│   ├── fixtures/
│   │   └── phase*.json (23 files)       ← Contextual malleability
│   ├── excitement_pathway_results/
│   │   ├── baseline_raw.json
│   │   └── baseline_summary.json
│   ├── benchmark_results_ai_docs.json
│   └── benchmark_no_tools.json
├── data/
│   ├── recursive_reasoning_results.json
│   └── personality_analysis_results.json
└── research/
    ├── experiments/
    │   └── cognitive-load/results/      ← New structure
    └── legacy/                          ← Preserved scripts
```
