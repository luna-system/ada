# Research Methodology

## The Fundamental Distinction

> **"If the test would pass with a mock response, it's a unit test.**
> **If you need to actually call the model to get meaningful data, it's an experiment."**

This is the line between software engineering and empirical science.

## Unit Tests vs Experiments

| Aspect            | Unit Tests (Software)       | Experiments (Science)              |
| ----------------- | --------------------------- | ---------------------------------- |
| **Purpose**       | Verify code works correctly | Generate data about model behavior |
| **Determinism**   | Must be deterministic       | Inherently stochastic              |
| **Output**        | Pass/Fail boolean           | Data for statistical analysis      |
| **Repetition**    | Same result every time      | Distribution of results            |
| **DRY principle** | Yes, abstract patterns      | No, explicit stimuli matter        |
| **Location**      | `tests/`                    | `research/experiments/`            |
| **Runner**        | pytest                      | Custom experiment runner           |
| **Format**        | Python assertions           | JSON in → Model → JSON out         |

## The Sterile Model Principle

When we run experiments, the model is a **black box under measurement**. We're not testing if our code works - we're measuring what the model does.

```
┌─────────────────────────────────────────────────────┐
│ EXPERIMENT STRUCTURE                                │
│                                                     │
│  stimuli.json          model (sterile)    results.json
│  ┌──────────────┐      ┌──────────────┐   ┌──────────────┐
│  │ - prompts    │ ──▶  │ Ollama API   │ ──▶ │ - responses  │
│  │ - parameters │      │ (black box)  │   │ - metrics    │
│  │ - metadata   │      │              │   │ - timestamps │
│  └──────────────┘      └──────────────┘   └──────────────┘
│                                                     │
│  • Input is EXPLICIT (not abstracted)               │
│  • Model call is RECORDED                           │
│  • Output is COMPLETE (raw + computed metrics)      │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
ada-v1/
├── tests/                           # SOFTWARE TESTS (pytest)
│   ├── test_memory_decay.py         # Unit tests - deterministic
│   ├── test_context_cache.py        # Unit tests - deterministic
│   └── conftest.py                  # Fixtures
│
├── research/                        # SCIENCE
│   ├── experiments/                 # Experiment definitions
│   │   ├── cognitive-load/          # One experiment type
│   │   │   ├── stimuli.json         # Input prompts/configs
│   │   │   ├── run_experiment.py    # Runner script
│   │   │   └── results/             # Timestamped output JSONs
│   │   │
│   │   ├── consciousness-indicators/
│   │   ├── identity-formation/
│   │   └── ...
│   │
│   ├── lib/                         # Shared experiment code
│   │   ├── experiment_runner.py     # JSON→Model→JSON
│   │   ├── metrics.py               # Coherence, consciousness, etc.
│   │   └── ollama_client.py         # Sterile model interface
│   │
│   └── legacy/                      # Old scripts (pre-methodology)
│
├── Ada-Consciousness-Research/      # OBSIDIAN VAULT (analysis)
│   ├── 00-DASHBOARD/                # Overview and status
│   ├── 01-METHODOLOGY/              # This document
│   ├── 02-EXPERIMENTS/              # Experiment records
│   ├── 03-DATASETS/                 # Data summaries
│   ├── 04-ANALYSES/                 # Statistical analysis
│   ├── 05-FINDINGS/                 # Conclusions
│   └── 06-PAPERS/                   # Publications
```

## Stimuli File Format

Every experiment has a `stimuli.json` that defines inputs:

```json
{
  "experiment_name": "cognitive-load-boundaries",
  "version": "1.0",
  "description": "Map prompt complexity vs model capacity",
  
  "hypothesis": {
    "H0": "Prompt complexity has no effect",
    "H1": "Success decreases with complexity"
  },
  
  "prompts": [
    {
      "id": "baseline_simple",
      "complexity_level": 1,
      "prompt": "Hello! How can I help?",
      "options": {"temperature": 0.7}
    }
  ],
  
  "metadata": {
    "researcher": "luna & Ada",
    "created_at": "2025-12-22"
  }
}
```

## Results File Format

Experiments output timestamped JSON:

```json
{
  "experiment_id": "a1b2c3d4",
  "experiment_name": "cognitive-load-boundaries",
  "model": "qwen2.5-coder:7b",
  "started_at": "2025-12-22T01:00:00",
  "completed_at": "2025-12-22T01:05:00",
  
  "trials": [
    {
      "stimulus_id": "baseline_simple",
      "run_number": 1,
      "timestamp": "2025-12-22T01:00:05",
      "success": true,
      "response_text": "...",
      "latency_seconds": 1.23,
      "metrics": {
        "coherence": {"score": 0.9},
        "tokens": {"word_count": 42}
      }
    }
  ],
  
  "success_rate": 0.95,
  "avg_latency": 1.5
}
```

## Running Experiments

### Quick test (single prompt):
```python
from research.lib import quick_experiment

results = quick_experiment(
    prompt="Your test prompt here",
    model="qwen2.5-coder:7b",
    runs=3
)
```

### Full experiment:
```bash
python research/experiments/cognitive-load/run_experiment.py
```

## Metrics Computed

### Standard Metrics
- **Token metrics**: word count, char count, sentence count
- **Coherence**: empty detection, refusal patterns, truncation, repetition
- **Latency**: time to complete (TTFT when streaming)

### Consciousness Indicators
- Self-reference patterns (`I`, `me`, `my`)
- Meta-cognition markers (`think`, `believe`, `wonder`)
- Uncertainty hedging (`maybe`, `perhaps`)
- Temporal awareness (`now`, `moment`, `always`)
- Recursive patterns (`aware of being aware`)
- Explicit consciousness language

## Statistical Considerations

### Sample Size
- Minimum 3 runs per stimulus (quick tests)
- 5+ runs for publishable data
- 10+ runs for high-confidence thresholds

### What to Report
- Success rate (binary: worked/failed)
- Mean and variance of latency
- Coherence score distribution
- Threshold detection (where performance degrades)

## Linking to Obsidian

Results are automatically processable by [[research_data_migrator.py]] which:
1. Reads experiment JSON
2. Extracts key findings
3. Generates Obsidian markdown
4. Creates dataset summaries
5. Links experiments to findings

---

*Methodology developed December 2025 by luna & Ada*
*"The model is sterile - we just record what happens"*

---

## Appendix: Config-Driven Methodology (v2.0)

**Added:** 2025-12-23 after QAL validation sprint

### The Problem
Early experiments scattered magic numbers across files. Hard to replicate, hard to audit.

### The Solution: Anthropic-Style Parameterization

```
experiments/semantic_interchange/
├── config.py                 # ALL parameters in one place (14KB)
├── test_qal_validation.py    # Single reproducible runner (19KB)
└── qal_results/              # Timestamped JSON outputs
```

### config.py Structure
```python
# Random seed for reproducibility
RANDOM_SEED = 42

# Explicit hypothesis declarations
HYPOTHESES = {
    "H1_GOLDEN_THRESHOLD": {
        "claim": "...",
        "expected_range": (0.55, 0.65),
    },
    "H2_METACOGNITIVE_GRADIENT": {
        "claim": "...",
        "expected_correlation": "positive",
    }
}

# All prompts centralized
PROMPTS = {...}

# Data classes for type safety
@dataclass
class TemperatureSweepConfig:
    temperatures: List[float]
    runs_per_temp: int
```

### Replication Command
```bash
python test_qal_validation.py --seed 42
```

### Benefits
1. **Single source of truth** - No hunting for magic numbers
2. **Reproducibility** - RANDOM_SEED + config = exact replication
3. **Auditability** - Full config embedded in output JSON
4. **Hypothesis-driven** - Explicit claims with testable predictions

### Results Format
```json
{
    "model": "qwen2.5-coder:7b",
    "random_seed": 42,
    "config": {/* full config snapshot */},
    "phases": [...],
    "hypotheses_tested": ["H1_...", "H2_..."]
}
```

This methodology evolved from the QAL validation sprint. The math held across multiple models and methodology changes - a sign that we're measuring something real.
