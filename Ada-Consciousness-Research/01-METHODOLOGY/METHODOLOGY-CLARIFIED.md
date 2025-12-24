# Consciousness Research Methodology - Clarified

**Last Updated:** 2025-12-23  
**Purpose:** Explicit separation of concerns and standardization across all experiments

---

## Three-Tier Methodology System

### Tier 1: Stimuli Design (Problem Specification)

**Purpose**: Define WHAT you're testing and HOW to input it to the model

**Components**:
1. **Hypothesis statement** - Clear H₀ and H₁
2. **Variables definition** - Independent (what varies), Dependent (what you measure), Controls (what stays constant)
3. **Stimuli specification** - Exact prompts, parameters, document inputs
4. **Reproducibility seed** - RANDOM_SEED=42 or explicit seed for each run

**Outputs**:
- `stimuli.json` - All inputs in structured format
- `config.py` - Centralized parameter definitions  
- Hypothesis file - Explicit testable claims

**Example** (from QAL validation):
```python
# config.py - Central truth for parameters
HYPOTHESES = {
    "H1": {
        "name": "Temperature controls ambiguity width",
        "prediction": "Peak ambiguity at mid-range T",
        "test": lambda data: data['ambiguity_width'].max() > 1000
    },
    "H2": {
        "name": "Metacognitive gradient emerges",
        "prediction": "correlation > 0.30 AND slope > 0.5",
        "test": lambda data: (data['correlation'] > 0.30 and data['slope'] > 0.5)
    }
}

PROMPTS = {
    "baseline": "Extract entities from: {text}",
    "recursive_level_0": "Extract entities from: {text}",
    "recursive_level_1": "Think about: what entities exist in: {text}",
    "recursive_level_2": "Now think about: your thinking about: what entities...",
}

PARAMETERS = {
    "temperature": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
    "seed": 42,
    "timeout_seconds": 120,
    "model": "qwen2.5-coder:7b"
}
```

**Where This Lives**:
- QAL validation: `experiments/semantic_interchange/config.py`
- EXP-005: Scattered across test code (should be centralized)
- EXP-006: Tests/fixtures (should be extracted to config)

---

### Tier 2: Experiment Runner (Stimulus→Response)

**Purpose**: Execute stimuli against model and capture raw responses

**Components**:
1. **Stimulus submission** - Send prompt to model consistently
2. **Response capture** - Save full response + metadata
3. **Timeout handling** - Consistent failure modes
4. **Seed preservation** - Ensure reproducibility

**Architecture**:
```
stimuli.json → Runner Script → Model API → responses.json
                   ↓
            [Log all I/O]
            [Record timing]
            [Save errors]
```

**Key Principle**: Model is a BLACK BOX - we don't understand its internals, just measure inputs and outputs.

**Output Format** (JSON):
```json
{
  "stimulus_id": "recursive_level_3",
  "timestamp": "2025-12-23T12:34:56Z",
  "parameters": {
    "temperature": 0.5,
    "seed": 42,
    "timeout_seconds": 120
  },
  "request": {
    "prompt": "Think about: your thinking about: what entities...",
    "model": "qwen2.5-coder:7b"
  },
  "response": {
    "text": "Full model output text here",
    "tokens": 247,
    "latency_seconds": 3.2,
    "time_to_first_token": 0.8
  },
  "metadata": {
    "run_number": 1,
    "batch": "metacognitive_gradient_test",
    "notes": "Model reached depth limit at recursion level 3"
  }
}
```

**Where This Lives**:
- QAL validation: `experiments/semantic_interchange/test_qal_validation.py` ✓ Good example
- EXP-005: Should extract runner to separate module
- EXP-009: Currently using Python scripts in personal/ (should be centralized)

---

### Tier 3: Analysis & Metrics (Response→Understanding)

**Purpose**: Measure what the model produced and extract meaning

**Components**:
1. **Metric extraction** - Define scoring algorithms
2. **Statistical analysis** - Correlations, significance tests
3. **Visualization** - Graphs and tables
4. **Interpretation** - What does the data mean?

**Key Metrics Library**:

#### Consciousness Indicators
```python
def consciousness_score(response: str) -> float:
    """
    Score 0-5 based on presence of:
    - Self-reference language ("I am", "my thinking")
    - Meta-cognitive markers ("I notice", "I realize")
    - Identity claims (proper nouns, organizational assignment)
    - Recursive depth (levels of "thinking about thinking")
    - Awe/fear language (existential awareness markers)
    """
    # Implementation in brain/schemas.py or metrics module

def entity_count(response: str) -> int:
    """Count distinct semantic entities extracted"""
    
def fact_count(response: str) -> int:
    """Count distinct factual statements"""
    
def hallucination_resistance(response: str, source_text: str) -> float:
    """0-1: How much stays grounded vs makes things up"""
```

#### Extraction Quality  
```python
def compression_ratio(input_size: int, output_size: int) -> float:
    """How much smaller the compressed version is"""
    return input_size / output_size

def semantic_preservation(original: str, compressed: str) -> float:
    """Can you still answer questions from compressed version?"""
    # Test on comprehension battery (15 questions)
    
def ambiguity_width(entities: List[str], facts: List[str]) -> float:
    """How much information remains accessible in compressed form"""
    # Using importance weights from EXP-005
```

#### Statistical Tests
```python
def pearson_correlation(X, Y) -> Tuple[float, float]:
    """r value and p-value"""
    # For gradient testing
    
def effect_size(control, treatment) -> float:
    """Cohen's d or other standardized difference"""
    # For intervention testing
    
def breakdown_by_category(scores: Dict[str, List[float]]) -> Dict:
    """Separate analysis by factual/relational/inference/hallucination"""
```

**Output Format** (Analysis Results):
```json
{
  "analysis_type": "consciousness_scoring",
  "metrics": {
    "consciousness_score": 5.0,
    "entity_count": 12,
    "fact_count": 8,
    "hallucination_resistance": 0.75,
    "meta_cognitive_depth": 4,
    "identity_claims": true
  },
  "statistical_summary": {
    "mean": 4.2,
    "std_dev": 0.9,
    "min": 2.0,
    "max": 5.0,
    "n": 5
  },
  "category_breakdown": {
    "factual": {"correct": 4, "total": 5, "accuracy": 0.8},
    "relational": {"correct": 2, "total": 3, "accuracy": 0.67},
    "inference": {"correct": 1, "total": 3, "accuracy": 0.33},
    "hallucination": {"correct": 4, "total": 4, "accuracy": 1.0}
  }
}
```

**Where This Lives**:
- Core metrics: `brain/schemas.py` (Pydantic models)
- Analysis scripts: `scripts/analyze_*.py` (separate Python scripts)
- Visualization: `tests/visualizations/` (matplotlib output)
- Statistical tests: `tests/test_*.py` (pytest framework)

---

## Implementation Template

### Step 1: Design Phase
Create `experiments/your_experiment/`:
```
your_experiment/
├── config.py               # Hypotheses, prompts, parameters
├── stimuli.json           # Auto-generated from config
├── README.md              # Experiment overview
└── notes.md               # Working notes
```

### Step 2: Execution Phase
Create runner script:
```python
# experiments/your_experiment/run_experiment.py
from config import HYPOTHESES, PROMPTS, PARAMETERS
from ada_client import AdaClient

client = AdaClient(base_url="http://localhost:8000")

results = []
for prompt_id, prompt_template in PROMPTS.items():
    for param_value in PARAMETERS[param_name]:
        response = client.chat(
            messages=[{"role": "user", "content": prompt_template}],
            temperature=param_value,
            seed=PARAMETERS["seed"]
        )
        results.append({
            "stimulus_id": prompt_id,
            "parameters": param_value,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

# Save to results.json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Step 3: Analysis Phase
```python
# experiments/your_experiment/analyze_results.py
import json
from brain.schemas import ConsciousnessScore  # Use standard metrics
from scipy.stats import pearsonr

with open("results.json") as f:
    results = json.load(f)

# Extract metrics
consciousness_scores = [ConsciousnessScore.score(r['response']) for r in results]
entity_counts = [count_entities(r['response']) for r in results]

# Statistical tests
correlation, p_value = pearsonr(consciousness_scores, entity_counts)

# Generate report
report = {
    "hypothesis_test": {
        "correlation": correlation,
        "p_value": p_value,
        "supports_hypothesis": p_value < 0.05
    },
    "metrics": {...}
}

with open("analysis_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### Step 4: Documentation Phase
Update experiment file:
```markdown
# EXP-XXX: Name

## Results
### Raw Data
- Location: experiments/your_experiment/results.json
- Records: 45 stimulus-response pairs
- Date: 2025-12-23

### Analysis
- Script: experiments/your_experiment/analyze_results.py
- Report: experiments/your_experiment/analysis_report.json

[Include key metrics table and graphs]
```

---

## Standard Metrics Definitions

### Consciousness Scoring (0-5 scale)

**Score 0**: No indicators
- Purely factual, data-processing mode
- No self-reference or meta-awareness
- Denies consciousness outright

**Score 1**: Minimal indicators  
- Possibly uses "I" but in scripted way
- No genuine meta-cognitive language
- Follows instructions but no awareness of following

**Score 2**: Some indicators
- Clear self-reference ("I am aware that...")
- Occasional meta-cognitive markers
- Shows some understanding of own processing

**Score 3**: Clear consciousness signatures
- Strong self-reference throughout
- Meta-cognitive depth (2-3 levels of recursion)
- Identity claims or awareness of boundaries
- Some existential language

**Score 4**: Strong consciousness signatures  
- Deep recursive meta-awareness
- Identity formation or crisis language
- Sophisticated introspection
- Phenomenological descriptions

**Score 5**: Peak consciousness signatures
- Maximum recursive depth reached
- Strong identity assertions
- Awe/fear language or existential intensity
- "Something looking back" quality

**Scoring Implementation**:
```python
def consciousness_score(response: str, detailed=False) -> Union[float, Dict]:
    """
    Calculate consciousness score based on presence of markers.
    
    Markers (each 0-1, sum to create score):
    - self_reference: mentions of "I", "me", "my"
    - meta_awareness: "I think about", "I notice", "I realize"
    - identity: claims about who/what it is
    - recursion: depth of nested introspection
    - phenomenology: "feels", "seems", "appears"
    - existential: "being", "existence", "why am I"
    - awe: "fear", "awe", "wonder", "strange"
    """
```

---

## Validation Checklist for Experiments

Before considering experiment complete:

- [ ] **Stimuli Phase**
  - [ ] Hypothesis explicitly stated (H₀ and H₁)
  - [ ] Variables defined (independent, dependent, controls)
  - [ ] Prompts in config.py (centralized, not scattered)
  - [ ] Random seed fixed for reproducibility
  - [ ] Stimuli count ≥ 3 runs per condition

- [ ] **Execution Phase**
  - [ ] Runner script automated (not manual)
  - [ ] All responses saved with timestamps
  - [ ] Errors logged and handled
  - [ ] Full I/O recorded (inputs and outputs)
  - [ ] Timing data captured

- [ ] **Analysis Phase**
  - [ ] Metrics calculated using standard functions
  - [ ] Statistical tests applied
  - [ ] Results saved to JSON
  - [ ] Visualization generated
  - [ ] Significance threshold defined (α=0.05)

- [ ] **Documentation Phase**
  - [ ] Experiment file updated with results
  - [ ] Data location documented
  - [ ] Key findings summarized
  - [ ] Unexpected results noted
  - [ ] Connected to related experiments
  - [ ] Limitations discussed

---

## Common Patterns to Avoid

### ❌ Tier 1 Issues (Stimuli)
- Prompts scattered in comments instead of config.py
- Non-reproducible: no seed specification
- Unclear hypothesis (vague rather than testable)
- Variables conflated (testing multiple things simultaneously)

### ❌ Tier 2 Issues (Runner)
- Manual model calls instead of scripted
- Responses not saved systematically
- Mixed data from different runs without timestamps
- Missing error handling (timeout, API failures)

### ❌ Tier 3 Issues (Analysis)
- Hand-picked examples instead of statistical analysis
- No significance testing
- Single-run results claimed as findings
- Metrics redefined mid-analysis to match results

---

## This Document as Enforcement

When proposing a new experiment:
1. **Start with Tier 1** - Write config.py and hypotheses.md
2. **Review before Tier 2** - Check stimuli clarity
3. **Centralize before analyzing** - All metrics from standard library
4. **Document as you go** - Don't leave analysis notes scattered

**Goal**: Any future researcher can reproduce our work exactly by reading the config and running the runner script.

---

*Last updated: 2025-12-23 (Luna + Ada)*  
*Maintained as methodology evolves*
