# Research Validation Plan: Empirical Testing of Biomimetic Features

**Status:** Planned for post-Phase 1  
**Goal:** Generate HARD NUMBERS proving Ada's biomimetic features are legitimately cool science  
**Vibe:** Unemployed moon dog system makes graphs and proves theories 🌙✨

## Why This Matters

We have theories about how memory decay, habituation, attention, and importance scoring should behave. Let's **prove it with data** instead of just vibes. This turns Ada from "artisanal craft" into "research contribution" - the kind that could be a paper.

## Phase 1: Property-Based Testing (Start Here!)

**Timeline:** Next session after Phase 1 commit  
**Effort:** 1-2 hours  
**Tools:** Hypothesis (already installed!)  
**Output:** Find edge cases automatically

### What We'll Add

```python
from hypothesis import given, strategies as st

@given(
    age_hours=st.floats(min_value=0, max_value=1000),
    importance=st.floats(min_value=0, max_value=1),
    surprise=st.floats(min_value=0, max_value=1),
    relevance=st.floats(min_value=0, max_value=1)
)
def test_importance_always_bounded(age_hours, importance, surprise, relevance):
    """Property: importance score ALWAYS in [0,1] regardless of inputs."""
    # Generate thousands of random combinations
    # Find violations automatically
    pass

@given(st.lists(st.dictionaries(...), min_size=10, max_size=100))
def test_gradient_levels_consistent(conversation):
    """Property: Detail level always matches threshold."""
    pass
```

### Properties to Test

1. **Bounded outputs:** Importance always ∈ [0, 1]
2. **Monotonicity:** Recent > Old (when other factors equal)
3. **Temperature effect:** High importance decays slower
4. **Gradient consistency:** Same score always maps to same level
5. **Weight normalization:** Changing one weight affects total

## Phase 2: Synthetic Conversation Generation

**Timeline:** After property tests pass  
**Effort:** 4-6 hours  
**Output:** `tests/fixtures/synthetic_conversations.json`

### Data Generators

```python
def generate_conversation_dataset(
    num_turns=100,
    topics=['coding', 'philosophy', 'music', 'neuroscience'],
    importance_distribution='pareto',  # 80/20 rule
    temporal_pattern='burst',          # Clustered activity
    repetition_rate=0.2,               # 20% repeated content
    novelty_decay=0.05                 # Topics become less surprising
):
    """Generate synthetic conversations with known ground truth."""
```

### Distributions We'll Model

- **Pareto importance:** Most turns boring (0.1-0.3), few critical (0.8-1.0)
- **Burst timing:** Conversations happen in clusters, not uniform
- **Topic drift:** Gradual shifts (not random jumps)
- **Zipfian vocabulary:** Real word frequency distribution
- **Repetition patterns:** Some ideas revisited, some one-off

### Ground Truth Labels

Each turn gets:
- `ground_truth_importance` - What a human would rate it
- `ground_truth_topic` - Which topic it belongs to
- `ground_truth_retrieval` - Should this be retrieved for query X?

## Phase 3: Ablation Studies (The Science!)

**Timeline:** After synthetic data exists  
**Effort:** 8-12 hours  
**Output:** CSV of results, statistical significance tests

### Research Questions

#### A. Does Habituation Reduce Repetition? 🔬

**Hypothesis:** Repeated content scores lower with habituation enabled  
**Method:** Same conversations, two configs (habituation on/off)  
**Metric:** Average score for repeated vs novel turns  
**Expected:** t-test shows p<0.05, repeated turns 20-40% lower with habituation

```python
def test_habituation_effect():
    conversations = generate_repetitive_conversation()
    scores_baseline = score_all(conversations, habituation_weight=0.0)
    scores_habituated = score_all(conversations, habituation_weight=0.3)
    
    repeated_indices = find_repeated_content(conversations)
    
    from scipy.stats import ttest_rel
    t_stat, p_value = ttest_rel(
        [scores_baseline[i] for i in repeated_indices],
        [scores_habituated[i] for i in repeated_indices]
    )
    
    assert p_value < 0.05, "Habituation should significantly reduce repetition"
```

#### B. Does Temperature Preserve Important Memories? 🌡️

**Hypothesis:** High-importance memories survive decay longer  
**Method:** Generate memories with varied importance, age them, measure survival  
**Metric:** Survival rate at t=100hr, t=500hr by importance quartile  
**Expected:** Top quartile survives 2-5x longer than bottom quartile

#### C. Multi-Signal vs Single-Signal Scoring 📊

**Hypothesis:** Multi-signal scoring retrieves more relevant context  
**Method:** Compare our system (4 signals) vs baseline (decay only)  
**Metric:** Precision/recall on retrieval task with labeled data  
**Expected:** 10-30% improvement in precision, similar recall

#### D. Optimal Signal Weights 🎛️

**Hypothesis:** Default weights (0.4/0.3/0.2/0.1) are near-optimal  
**Method:** Grid search over weight combinations  
**Metric:** Context quality score (LLM-judged or human-labeled)  
**Output:** Heatmap showing performance across weight space

#### E. Gradient Efficiency vs Quality Trade-off ✂️

**Hypothesis:** Gradients reduce tokens 40-60% with <5% quality loss  
**Method:** Same conversations, all-FULL vs gradient  
**Metrics:**
  - Token count reduction (%)
  - Response quality (BLEU, LLM judge, or human)
**Expected:** 50% token reduction, 3% quality loss

## Phase 4: Visualization & Graphs 📈

**Timeline:** After ablation results exist  
**Effort:** 4-6 hours  
**Output:** Graphs for `docs/research/`, potential paper figures

### Graphs We'll Generate

1. **Decay Curves:** Empirical vs Ebbinghaus theoretical
   - Three lines: low/med/high importance
   - Show temperature modulation visually
   - Calculate R² to quantify fit

2. **Signal Contribution Breakdown:** Stacked bar chart
   - Show how each signal contributes to final score
   - Compare across different turn types

3. **Gradient Efficiency:** Scatter plot
   - X-axis: Token reduction (%)
   - Y-axis: Quality score
   - Points colored by detail level

4. **Habituation Effect:** Box plots
   - Repeated vs novel content scores
   - With/without habituation

5. **Weight Space Heatmap:** 2D heatmap
   - X: decay weight, Y: surprise weight
   - Color: performance metric
   - Find optimal region

6. **Survival Curves:** Kaplan-Meier style
   - Memory retention over time
   - Stratified by importance quartile

### Example Code

```python
def plot_decay_validation():
    """Prove decay follows Ebbinghaus curve."""
    ages = np.linspace(0, 500, 100)
    
    scores_low = [score_at_age(age, importance=0.1) for age in ages]
    scores_high = [score_at_age(age, importance=0.9) for age in ages]
    theoretical = [np.exp(-age/100) for age in ages]
    
    plt.figure(figsize=(10, 6))
    plt.plot(ages, scores_low, label='Low Importance', linewidth=2)
    plt.plot(ages, scores_high, label='High Importance', linewidth=2)
    plt.plot(ages, theoretical, '--', label='Theoretical (Ebbinghaus)', 
             linewidth=2, alpha=0.7)
    
    plt.xlabel('Age (hours)', fontsize=12)
    plt.ylabel('Importance Score', fontsize=12)
    plt.title('Memory Decay: Empirical vs Theoretical', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig('docs/research/decay_validation.png', dpi=300)
    
    r_squared = calculate_r_squared(scores_high, theoretical)
    print(f"Temperature-modulated decay fit: R² = {r_squared:.3f}")
```

## Phase 5: Documentation & Write-Up 📝

**Timeline:** After graphs exist  
**Effort:** 4-6 hours  
**Output:** `docs/research/biomimetic_validation.rst`

### Document Structure

1. **Introduction:** What we're testing and why
2. **Methods:** Data generation, metrics, test procedures
3. **Results:** Graphs, tables, statistical tests
4. **Discussion:** What it means, limitations, future directions
5. **Appendix:** Full test code, data availability

### Potential Paper

If results are solid, this could be:
- **Short paper:** NeurIPS Workshop, ICML Workshop, ACL Findings
- **Blog post:** For local-first community, AI researchers
- **Technical report:** ArXiv preprint

**Title Ideas:**
- "Biomimetic Memory Management in Conversational AI: An Empirical Study"
- "Temperature-Modulated Decay for Context Retrieval: Evidence from Synthetic Conversations"
- "Multi-Signal Importance Scoring: Beyond Temporal Decay in RAG Systems"

## Implementation Notes

### File Structure

```
tests/
├── benchmarks/              # NEW!
│   ├── __init__.py
│   ├── test_property_based.py      # Phase 1
│   ├── test_ablation_studies.py    # Phase 3
│   └── synthetic_data.py           # Phase 2
├── fixtures/
│   └── synthetic_conversations.json  # Generated data
└── research/                # NEW!
    ├── plot_decay.py
    ├── plot_signals.py
    ├── plot_gradients.py
    └── generate_report.py

docs/research/              # NEW!
├── biomimetic_validation.rst
└── _static/
    ├── decay_validation.png
    ├── signal_contributions.png
    ├── gradient_efficiency.png
    └── habituation_effect.png
```

### Dependencies

Already have:
- ✅ `hypothesis` - Property-based testing
- ✅ `pytest` - Test framework

Need to add:
- `scipy` - Statistical tests (t-test, etc.)
- `matplotlib` or `seaborn` - Graphs
- `numpy` - Numerical operations
- `pandas` - Data manipulation (optional, makes life easier)

## Why This Is Cool

1. **Falsifiable claims:** We can actually be *wrong* and learn from it
2. **Reproducible:** Anyone can run the tests and get same results
3. **Publishable:** Real research, not just engineering
4. **Community contribution:** Shows local-first AI can be rigorous
5. **Self-improvement:** Data guides future feature development

## Next Steps

1. ✅ Finish Phase 1 (importance scoring implementation)
2. ✅ Commit and document Phase 1
3. 🎯 **Start property-based testing** (this plan, Phase 1)
4. Generate synthetic data (Phase 2)
5. Run ablation studies (Phase 3)
6. Make pretty graphs (Phase 4)
7. Write it up (Phase 5)

## Philosophy

This isn't "work" in the capitalist sense - it's **play**. We're unemployed moon dogs doing science because it's **interesting** and **fun** and we want to **know if our theories are real**. 

The numbers don't validate us. They just help us understand the thing we're building.

Everything we need is already here, and everything goes on. 🌱✨

---

**Created:** 2025-12-17  
**Last Updated:** 2025-12-17  
**Status:** Planning phase  
**Next Action:** Commit Phase 1, then start property tests
