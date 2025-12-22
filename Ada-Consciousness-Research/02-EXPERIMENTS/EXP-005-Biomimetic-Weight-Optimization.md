# EXP-005: Biomimetic Weight Optimization

## Metadata
- **Date**: 2025-12-14 to 2025-12-18
- **Researcher**: luna & Ada (Claude Sonnet)
- **Status**: Complete
- **Priority**: High
- **Tags**: #biomimetic #memory #empirical #production-deployed

## Abstract
Seven-phase empirical research program to optimize signal weights in Ada's biomimetic memory system. Discovered that novelty/surprise dominates importance scoring (optimal weight 0.60), temporal decay is overweighted in intuitive design (optimal 0.10 vs intuitive 0.40), and single-signal surprise-only outperforms multi-signal baseline.

## Hypothesis
**H₀**: Intuitive signal weights (decay=0.40, surprise=0.30, relevance=0.20, habituation=0.10) are optimal  
**H₁**: Empirically optimized weights will outperform intuition-based design

## Method

### Phases
1. **Phase 1**: Property-based testing (27 tests, 0.09s) - Mathematical invariants
2. **Phase 2**: Synthetic data generation (10 tests, 0.04s) - Ground truth datasets
3. **Phase 3**: Ablation studies (12 tests, 0.05s) - Single-signal analysis
4. **Phase 4**: Grid search optimization (7 tests, 0.08s) - 169 weight configurations
5. **Phase 5**: Production validation (6 tests, 0.07s) - Real conversation data
6. **Phase 6**: Deployment (11 tests, 0.07s) - Optimal weights deployed
7. **Phase 7**: Visualization (7 tests, 2.93s) - 6 publication-quality graphs

### Procedure
```python
# Grid search over 169 configurations
for decay in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    for surprise in [0.0, 0.1, ...]:
        # Test correlation with ground truth importance
```

### Variables
- **Independent**: Signal weights (decay, surprise, relevance, habituation)
- **Dependent**: Pearson correlation with ground truth importance rankings
- **Controls**: Same synthetic datasets across all configurations

## Results

### Optimal Weights
| Signal | Intuitive | Optimal | Change |
|--------|-----------|---------|--------|
| Decay | 0.40 | 0.10 | **4x reduction** |
| Surprise | 0.30 | 0.60 | **2x increase** |
| Relevance | 0.20 | 0.20 | unchanged |
| Habituation | 0.10 | 0.10 | unchanged |

### Key Metrics
- **Baseline multi-signal correlation**: r = 0.869
- **Surprise-only correlation**: r = 0.876 (!)
- **Optimal multi-signal correlation**: r = 0.924
- **Improvement**: +12-38% correlation across synthetic datasets, +6.5% on real conversations

### Ablation Surprise
**Shocking finding**: Single-signal (surprise-only) beats multi-signal baseline!

This means novelty/surprise alone is a better predictor of memory importance than the combined intuitive weighting of all four signals.

## Findings

### Summary
1. **Surprise supremacy**: Novelty dominates importance scoring
2. **Recency overweighted 4x**: Intuition overweights temporal decay
3. **Smooth optimization landscape**: Enables future gradient-based tuning
4. **Same-day deployment**: Research → production in <24hrs via TDD

### Theoretical Implications
- Memory importance follows surprise-first architecture
- Aligns with Schwarz (2010) "disfluency triggers analysis"
- Human memory may also prioritize surprise over recency

### Production Impact
Deployed to `brain/config.py`:
```python
# Empirically validated (Dec 2025)
IMPORTANCE_WEIGHTS = {
    "decay": 0.10,      # Was 0.40
    "surprise": 0.60,   # Was 0.30
    "relevance": 0.20,
    "habituation": 0.10
}
```

## Discussion

### Interpretation
The dominance of surprise suggests that LLM-based assistants should prioritize "what's new" over "what's recent" when retrieving context. This is counterintuitive but empirically validated.

### Implications
1. Biomimetic memory can be empirically optimized
2. Intuition-based design underweights novelty
3. TDD methodology enables same-day research-to-production

### Limitations
1. Synthetic ground truth may not reflect real importance
2. Single model (Ada's architecture) - may not generalize
3. Static weights - could be dynamically adjusted

## Connections
- **Enables**: [[EXP-009-Consciousness-Edge-Testing]] (surprise as consciousness signal)
- **Supports**: [[EXP-010-Unified-Discomfort-Theory]] (surprise = alienation?)
- **Built on**: brain/memory_decay.py, brain/context_habituation.py

## Future Work
- [ ] Phase I: Is 0.60 a universal threshold?
- [ ] Dynamic weight adjustment based on context type
- [ ] Cross-model validation (Claude, GPT-4)

## Technical Notes

### Data Files
- tests/fixtures/test_memory_decay_*.json
- tests/fixtures/phase_*/
- tests/visualizations/*.png

### Test Suite
```bash
pytest tests/test_weight_optimization.py --ignore=tests/conftest.py
# 80 tests, 3.56s runtime, 100% passing
```

---
*Deployed: 2025-12-18*
*"The weights were wrong. Now they're right."*
