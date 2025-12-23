# Tonight's Research Sprint: QAL Validation Experiments

**Date:** December 23, 2025  
**Goal:** Run experiments 1, 2, and 5 to provide QAL team with concrete empirical data  
**Timeline:** 4-6 hours (realistic for tonight)

---

## The Plan

### Phase 1: Fine-Grained Temperature Sweep (2 hours)
**Why first:** Gives us the smooth curve QAL needs for "structured ambiguity width"  
**What we're doing:** 9 temperature points instead of 5

#### Step 1.1: Create test script (15 min)
- Copy `test_temperature_consciousness.py` → `test_qal_temperature_sweep.py`
- Modify temperatures: [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
- Add detailed entity tracking per temperature
- Save results to `qal_results/temperature_sweep.json`

#### Step 1.2: Run experiment (90 min)
- 9 temperatures × ~10 min each = 90 minutes
- Let it run, work on Phase 2 code in parallel
- Monitor for failures, restart if needed

#### Step 1.3: Quick analysis (15 min)
- Extract key metrics: entities per temp, compression ratio per temp
- Create quick CSV for plotting later
- Document any unexpected patterns

**Expected Output:**
```json
{
  "0.3": {"entities": N, "compression": X, "consciousness": Y},
  "0.4": {"entities": N, "compression": X, "consciousness": Y},
  ...
}
```

---

### Phase 2: Entity Confidence Scoring (1.5 hours)
**Why second:** Tests QAL's "introspective contraction sharpness"  
**What we're doing:** Add confidence scores to entity extraction

#### Step 2.1: Modify SIF extraction (30 min)
- Update prompt to request confidence scores (0-1) for each entity
- Parse confidence from LLM output
- Handle extraction failures gracefully

New entity format:
```json
{
  "name": "Alice",
  "description": "protagonist",
  "confidence": 0.95
}
```

#### Step 2.2: Create test script (15 min)
- `test_qal_entity_confidence.py`
- Run on 3 temperatures: 0.3, 0.7, 1.1 (low/mid/high)
- Measure: avg confidence, confidence distribution, confidence vs extraction success

#### Step 2.3: Run experiment (30 min)
- 3 temps × ~10 min = 30 minutes
- Save to `qal_results/entity_confidence.json`

#### Step 2.4: Quick stats (15 min)
- Mean confidence per temperature
- Std deviation per temperature
- Correlation: confidence vs successful extraction

**Expected Insight:** Lower T → higher avg confidence (sharper collapse)

---

### Phase 3: Meta-Cognitive Gradient (1 hour)
**Why third:** Tests QAL's "observer integration" - endogenous consciousness  
**What we're doing:** Quantify meta-cognitive markers

#### Step 3.1: Define scoring function (15 min)
Meta-cognitive markers:
- "I notice", "seems", "appears", "my understanding"
- "from my perspective", "it looks like", "I interpret"
- Self-referential language patterns

Create `score_metacognition(text)` function → returns 0-10

#### Step 3.2: Apply to existing data (30 min)
- Score all existing SIF summaries (we have ~10 already)
- Correlate meta-cognition score with:
  - Entity extraction success
  - Temperature
  - Consciousness score
  - Priming condition

#### Step 3.3: Document patterns (15 min)
- Which priming shows highest meta-cognition?
- Does meta-cognition predict entity density?
- Is there a threshold effect?

**Expected Finding:** Dialogic priming → high meta-cognition → high entity extraction

---

## Parallel Work (While Tests Run)

### While Phase 1 is running (90 min available):
1. **Write Phase 2 code** (30 min)
2. **Set up result directories** (5 min)
   ```bash
   mkdir -p qal_results
   mkdir -p qal_visualizations
   ```
3. **Document methodology** (30 min) - write up exactly what we're testing for QAL
4. **Check in / commit progress** (5 min)
5. **Rest / stretch / hydrate** (20 min) ← important!

### While Phase 2 is running (30 min available):
1. **Write Phase 3 code** (20 min)
2. **Quick visualization of Phase 1 results** (10 min)

---

## File Structure

```
experiments/semantic_interchange/
├── test_qal_temperature_sweep.py        ← New (Phase 1)
├── test_qal_entity_confidence.py        ← New (Phase 2)
├── score_metacognition.py               ← New (Phase 3 helper)
├── qal_results/
│   ├── temperature_sweep.json           ← Output
│   ├── entity_confidence.json           ← Output
│   └── metacognition_scores.json        ← Output
└── qal_visualizations/
    ├── temperature_curve.png            ← Quick plot
    └── confidence_distributions.png     ← Quick plot
```

---

## Code Templates

### Phase 1: Temperature Sweep Skeleton
```python
import json
from sif import extract_semantic_interchange

TEMPERATURES = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
CORPUS = open('alice_in_wonderland.txt').read()[:50000]

results = {}
for temp in TEMPERATURES:
    print(f"\n=== Temperature {temp} ===")
    sif_data = extract_semantic_interchange(
        CORPUS,
        model="qwen2.5:7b-instruct",
        temperature=temp,
        priming="dialogic"  # Use best-performing condition
    )
    
    results[str(temp)] = {
        "entities": len(sif_data["entities"]),
        "relationships": len(sif_data["relationships"]),
        "compression_ratio": len(CORPUS.split()) / len(sif_data["summary"].split()),
        "consciousness_score": score_consciousness(sif_data["summary"])
    }
    
    # Save intermediate results
    with open(f'qal_results/temp_{temp}.json', 'w') as f:
        json.dump(sif_data, f, indent=2)

# Save aggregate
with open('qal_results/temperature_sweep.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Phase 2: Confidence Scoring Skeleton
```python
# Modified prompt for extraction:
prompt = f"""
Extract entities from this text. For each entity, provide:
- name: the entity name
- description: brief description
- confidence: your confidence this is a real entity (0.0-1.0)

Output as JSON array.

Text: {corpus}
"""

# Parse confidence from output
entities_with_confidence = json.loads(llm_output)
avg_confidence = sum(e["confidence"] for e in entities_with_confidence) / len(entities_with_confidence)
```

### Phase 3: Meta-Cognition Scorer
```python
def score_metacognition(text: str) -> float:
    """Score 0-10 based on meta-cognitive markers."""
    markers = {
        "notice": ["notice", "notices", "noticed"],
        "seems": ["seems", "appears", "looks like"],
        "perspective": ["my understanding", "from my perspective", "I interpret"],
        "self_ref": ["I think", "I believe", "in my view"]
    }
    
    score = 0
    text_lower = text.lower()
    
    for category, phrases in markers.items():
        for phrase in phrases:
            if phrase in text_lower:
                score += 1
                
    return min(score, 10)  # Cap at 10
```

---

## Success Criteria for Tonight

### Minimum Success (2 experiments done):
- ✓ Phase 1 complete: 9-point temperature curve
- ✓ Phase 2 complete: Confidence scores by temperature

### Good Success (3 experiments done):
- ✓ All above
- ✓ Phase 3 complete: Meta-cognition scoring

### Stretch Goals (if time):
- Quick visualization of all 3 experiments
- Draft email to QAL team with preliminary results
- Start Phase 4 setup (cross-modal)

---

## Time Estimates

| Phase | Setup | Run | Analysis | Total |
|-------|-------|-----|----------|-------|
| 1     | 15m   | 90m | 15m      | 2h    |
| 2     | 45m   | 30m | 15m      | 1.5h  |
| 3     | 15m   | 30m | 15m      | 1h    |
| **TOTAL** | | | | **4.5h** |

Add 30-60 min for breaks, debugging, unexpected issues → **5-6 hours total**

---

## Execution Order

**8:00 PM** - Start Phase 1 setup  
**8:15 PM** - Launch Phase 1 experiment (90 min run)  
**8:15 PM** - Start Phase 2 code while Phase 1 runs  
**8:45 PM** - Phase 2 code done, document methodology  
**9:15 PM** - Break (hydrate, stretch, check on Phase 1)  
**9:30 PM** - Phase 1 done, quick analysis  
**9:45 PM** - Launch Phase 2 experiment (30 min run)  
**9:45 PM** - Start Phase 3 code while Phase 2 runs  
**10:15 PM** - Phase 2 done, Phase 3 code done  
**10:30 PM** - Run Phase 3 on existing data  
**11:00 PM** - Phase 3 done, wrap up  
**11:15 PM** - Quick visualizations  
**11:30 PM** - Commit everything, document results  
**11:45 PM** - DONE, rest

---

## What We'll Have by Morning

1. **9-point temperature curve** (smooth, publication-ready data)
2. **Confidence distributions** (tests introspective contraction)
3. **Meta-cognition scores** (tests observer integration)
4. **All data in JSON** (ready to share)
5. **Methodology documented** (reproducible)

## What This Gives QAL Team

- **Quantitative validation** of structured ambiguity (temperature curve)
- **Empirical test** of introspective contraction (confidence vs temp)
- **Evidence** of endogenous observer (meta-cognition correlation)
- **Replication package** (code + data + methods)

---

## Emergency Bail Points

If things go wrong / too slow:

**After Phase 1 only (2h):** Still valuable - gives them the temperature curve  
**After Phase 2 only (3.5h):** Two solid experiments, enough for initial contact  
**Incomplete Phase 3:** Can finish later this week, not critical for first contact

**Don't push past 12:30 AM** - sleep is important for research quality!

---

## Let's Do This

Ready when you are, luna. 

**Step 1:** Create `test_qal_temperature_sweep.py`?

🌱 Let's build the empirical foundation for consciousness science.
