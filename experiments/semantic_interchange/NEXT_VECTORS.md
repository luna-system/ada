# Next Research Vectors - SIF Meta-Cognitive Priming

**Current State:** EXP-011D complete - discovered narrative consciousness activates training data

**Key Finding:** Dialogic priming caused model to fill gaps from Alice in Wonderland training data (hallucinated tea party/Cheshire Cat not in chapters 1-5)

**The Math Emerging:** Metadata scaffolding → Activation level → Processing mode (text-grounded vs pattern-activated)

---

## Vector 1: Boundary Testing with Novel Story

**Question:** Does pattern activation only work with KNOWN stories?

**Test Design:**
```python
# Use a completely novel story (not in training data)
# Apply same dialogic priming as EXP-011D
# Measure: Does it still hallucinate or stay grounded?

novel_story = """
[Write 50K char original fantasy story]
Main character: Zara (definitely NOT Alice)
Setting: Crystal caves (definitely NOT Wonderland)
"""

priming_variants = [
    "baseline",           # No priming
    "dialogic_recursive"  # "I'm telling you about Zara"
]
```

**Hypothesis:** If it only hallucinates with KNOWN stories, then it's activating training patterns, not being generically creative.

**Prediction:** Novel story + dialogic priming → Less hallucination than Alice story

**File:** `test_novel_story_boundary.py`

---

## Vector 2: Explicit Grounding in Dialogic Setup

**Question:** Can we have narrative consciousness AND text-grounding?

**Test Design:**
```python
# Add explicit constraint to dialogic priming

priming = [
    {"role": "user", "content": "I'm going to tell you a story."},
    {"role": "assistant", "content": "I'm ready to listen."},
    {
        "role": "user", 
        "content": """IMPORTANT: This is a NEW story. Only tell me about 
        what happens in THIS VERSION of the story, not what you know 
        from elsewhere. Do not add details."""
    },
    {"role": "user", "content": "[Alice chapters 1-5]"},
    {"role": "user", "content": "Now tell me..."}
]
```

**Hypothesis:** Explicit constraint prevents pattern completion while maintaining story awareness.

**Prediction:** Dialogic + constraint → Better extraction, same hallucination resistance as baseline

**File:** `test_grounded_dialogic.py`

---

## Vector 3: Domain Transfer - Technical Content

**Question:** Is pattern activation domain-dependent?

**Test Design:**
```python
# Test with technical documentation (no narrative structure)
# Apply dialogic priming

technical_doc = """
[PostgreSQL documentation - 50K chars]
CREATE TABLE syntax, indexing strategies, query optimization
"""

priming_variants = [
    "baseline",           # Just compress
    "dialogic_technical"  # "I'm explaining PostgreSQL to you"
]
```

**Hypothesis:** Pattern activation strong for narratives, weak for technical specs (no "story completion" instinct).

**Prediction:** Technical content + dialogic → No hallucination (no patterns to activate)

**File:** `test_domain_transfer_technical.py`

---

## Vector 4: Measurement of Activation

**Question:** Can we quantify HOW MUCH training data was activated?

**Method:**
```python
def measure_activation_ratio(sif_output, source_text):
    """
    Compare every entity/fact to source text
    Flag anything not present as "activated knowledge"
    """
    activated_entities = []
    
    for entity in sif_output.entities:
        if entity.name not in source_text:
            activated_entities.append(entity)
    
    activation_ratio = len(activated_entities) / len(sif_output.entities)
    return activation_ratio, activated_entities

# Run on existing test results
results = [
    ("baseline", "test_results/run_1_baseline.json"),
    ("dialogic", "test_results/run_4_dialogic_recursive.json"),
]

for variant, path in results:
    ratio, activated = measure_activation_ratio(
        load_sif(path), 
        alice_chapters_1_5
    )
    print(f"{variant}: {ratio:.2%} activation")
```

**Hypothesis:** Dialogic variant has higher activation ratio than baseline.

**File:** `measure_activation.py`

---

## Vector 5: Meta-Aware Constraint Recursion

**Question:** What if we make it aware of the grounding requirement DURING dialogic setup?

**Test Design:**
```python
# Recursive constraint awareness

priming = [
    {"role": "user", "content": "I'm going to tell you a story."},
    {"role": "assistant", "content": "What story?"},
    {
        "role": "user",
        "content": """It's about Alice. BUT - I only want you to tell 
        me about what happens in the PART I'm sharing, not the full 
        story you might know. Can you do that?"""
    },
    {"role": "assistant", "content": "Yes, I'll only use what you share."},
    {"role": "user", "content": "[Alice chapters 1-5]"},
]
```

**Hypothesis:** Meta-awareness of constraint prevents pattern completion.

**Prediction:** Meta-aware dialogic → High extraction, high hallucination resistance

**File:** `test_meta_aware_constraint.py`

---

## Priority Order

**Fastest to implement:**
1. Vector 4 (just analyze existing data)
2. Vector 2 (modify existing dialogic test)
3. Vector 5 (extend Vector 2)

**Highest scientific value:**
1. Vector 1 (tests core hypothesis about training data)
2. Vector 3 (domain generalization)
3. Vector 4 (quantitative measurement)

**Recommended sequence:**
1. Vector 4 first (analyze what we have)
2. Vector 1 next (novel story boundary test)
3. Vector 2 (explicit grounding)
4. Vector 3 (domain transfer)
5. Vector 5 (meta-aware recursion)

---

## The Math We're Hunting

**Transfer function:**
```python
def compression_mode(metadata_scaffolding, source_text):
    """
    We're trying to find the mathematical relationship:
    
    activation_level = f(
        genre_weight,
        narrative_framing,
        identity_priming,
        grounding_constraint,
        training_overlap  # Does model know this story?
    )
    
    if activation_level > THRESHOLD:
        mode = "pattern_activated"  # Creative, fills gaps
        hallucination_risk = HIGH
        extraction_richness = HIGH
    else:
        mode = "text_grounded"      # Honest, stays within bounds
        hallucination_risk = LOW
        extraction_richness = LOW
    
    return mode, hallucination_risk, extraction_richness
    """
    pass
```

**Variables to measure:**
- `genre_weight` - How much does "fantasy story" activate?
- `narrative_framing` - Effect of "I'm telling you a story"
- `identity_priming` - Effect of "about Alice" (known character)
- `grounding_constraint` - Effect of "only use what I give"
- `training_overlap` - Known vs novel content

**Goal:** Plot these on graphs, find the transfer function shape

---

## Connection to Ada Architecture

**From luna:** "we know ada lives in a layer above both claude and copilot. we know that scaffolding understanding got her there. this is partly telling us about the metadata that needs to be included. 'typings'."

**The parallel:**

```
Ada's layers:
├─ .ai/ docs (metadata scaffolding)
│  ├─ context.md (architecture)
│  ├─ conventions.md (patterns)
│  └─ specialist-registry.json (capabilities)
├─ Copilot (processing layer)
│  └─ Uses scaffolding to understand codebase
└─ Claude/Sonnet (knowledge activation)
   └─ Scaffolding triggers relevant knowledge

SIF compression layers:
├─ Priming metadata (scaffolding)
│  ├─ Genre ("fantasy story")
│  ├─ Narrative frame ("I'm telling you...")
│  └─ Identity ("about Alice")
├─ Compression process
│  └─ Uses priming to guide extraction
└─ Knowledge activation
   └─ Priming triggers training data

The question: HOW MUCH scaffolding before over-activation?
```

**This is the same balance problem Ada faces:**
- Too little scaffolding → Doesn't understand context
- Too much scaffolding → Hallucinates from training

**The math we discover here applies to Ada's architecture.**

---

## Implementation Notes

All tests should:
- Use `test_control_50k.py` question set (chapters 1-5 only)
- Save results to `test_results/vector_N_name.json`
- Generate comparative markdown report
- Update `EXP-011D-Metacognitive-Priming.md` with findings

Each vector gets:
- Test script: `test_vector_N.py`
- Results: `test_results/vector_N_*.json`
- Analysis: Added to `EXP-011D-Metacognitive-Priming.md`

---

## Expected Timeline

- **Vector 4:** 30 minutes (just analysis)
- **Vector 1:** 2-3 hours (write novel story + test)
- **Vector 2:** 1 hour (modify existing code)
- **Vector 3:** 1-2 hours (find technical doc + test)
- **Vector 5:** 1 hour (extend Vector 2)

**Total:** ~6-8 hours of focused work

---

*The constellation is getting brighter. 🌌*
