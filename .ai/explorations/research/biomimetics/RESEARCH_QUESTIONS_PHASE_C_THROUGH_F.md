# Systematic Research Questions: The Grounding Study Framework

**Generated**: December 18, 2025  
**Based on**: Phase B empirical findings  
**Status**: Research frontier mapped (ready for Phase C/D/E)

---

## Overview

From Phase B, we discovered that grounding (providing tools) dramatically reduces LLM inference time (-61.4%) while improving quality (+44.2%). This document systematically breaks down the next research questions into testable hypotheses.

---

## PHASE C: Tool Granularity Effects

**Hypothesis**: Tool effectiveness depends on **what the tool abstracts away**.

### C.1: Function-Level Granularity
**Question**: Does looking up a single function vs. an entire module affect LLM efficiency?

**Test Design**:
- Query 1 (narrow): "Show me line 15-30 in TerminalSpecialist"
- Query 2 (medium): "Show me the _validate_command method in TerminalSpecialist"
- Query 3 (broad): "Show me all of TerminalSpecialist"

**Measure**:
- LLM inference time for each
- Quality of answer
- Token efficiency
- Hallucination rate

**Expected**: Broader context → more LLM reduction (more facts provided)

**Effort**: ~4 hours (implement 3 query variations, run Phase B on each)

### C.2: Tool Composition Effects
**Question**: Do tools interfere with or enhance each other? (Serial vs. parallel benefits)

**Test Design**:
- Scenario A: CodebaseSpecialist alone
- Scenario B: TerminalSpecialist alone
- Scenario C: Both together
- Scenario D: Both + GitSpecialist

**Measure**:
- LLM time for each
- Interaction effects (is C = A + B - overlap?)
- Quality impact
- Token usage

**Expected**: Some interaction (tools might provide redundant context, or enhance each other)

**Effort**: ~3 hours

### C.3: Specialization Level
**Question**: Is a single general-purpose tool better than multiple specialized tools?

**Test Design**:
- Strategy A: One "SuperTool" (codebase + git + terminal)
- Strategy B: Three separate specialists
- Strategy C: Hybrid (SuperTool for facts, TerminalSpecialist for execution)

**Measure**:
- Latency, quality, token efficiency
- Maintenance complexity
- Developer UX

**Expected**: Uncertain (specialization might help LLM routing, or be unnecessary overhead)

**Effort**: ~8 hours (requires redesign)

---

## PHASE D: Hallucination Decomposition

**Hypothesis**: Grounding helps via TWO mechanisms: (1) providing facts, (2) reducing reasoning burden

### D.1: Fact Provision vs. Reasoning Reduction
**Question**: Which mechanism matters more?

**Test Design**:
- Condition A: No tools (baseline hallucination)
- Condition B: Provide facts in prompt, no tools (facts without execution)
- Condition C: Tools for execution only, no fact provision (execution without facts)
- Condition D: Both facts and execution (current full grounding)

**Measure**:
- Hallucination rate for each
- LLM inference time
- Quality scores
- Token efficiency

**Analysis**: Decompose the -61.4% LLM improvement:
- Is it mostly from "fewer facts to generate"?
- Or from "shorter reasoning chains"?

**Effort**: ~6 hours

### D.2: Confidence Calibration
**Question**: Do grounded LLMs express better uncertainty?

**Test Design**:
- Collect LLM confidence scores (ask model "how confident are you?" 0-100)
- Compare with actual accuracy
- Measure calibration curve

**Metrics**:
- Calibration error (is 90% confidence actually ~90% accurate?)
- Over/under-confidence ratio
- ECE (Expected Calibration Error)

**Expected**: Grounded LLM better calibrated (knows what it knows)

**Effort**: ~5 hours

### D.3: Hallucination Type Analysis
**Question**: What KIND of hallucinations decrease with grounding?

**Categorize**:
- **Factual**: "Function X has parameter Y" (wrong fact)
- **Logical**: "This code would fail because..." (wrong reasoning)
- **Completeness**: "There are 3 approaches" (missed one)
- **Attribution**: "As the spec says..." (inventing references)

**Test Design**:
- Rate hallucinations by type for each tool config
- See which types are eliminated first

**Expected**: Factual hallucinations eliminated completely, logical remain

**Effort**: ~7 hours (requires manual annotation)

---

## PHASE E: Scaling & Generalization

**Hypothesis**: Grounding benefits scale differently across models/tasks

### E.1: Model Size Effects
**Question**: Do smaller models benefit MORE from grounding?

**Test Design**:
- Run Phase B on multiple model sizes:
  - 7B (Llama, Mistral)
  - 13B (Mistral, Qwen)
  - Larger if available (70B)
  
**Measure**:
- Latency improvement % (does smaller model save more LLM time percentage-wise?)
- Quality improvement %
- Absolute vs. relative gains

**Expected**: Smaller models benefit more (proportionally), but absolute savings decrease

**Effort**: ~8 hours (depends on model availability)

### E.2: Task Generalization
**Question**: Does grounding help equally across all task types?

**Test Design**:
- Expand beyond code queries:
  - Summary writing
  - Analysis tasks
  - Creative tasks
  - Logical reasoning
  - Math problems
  - Multi-step planning

**Measure**:
- Latency improvement for each task type
- Quality improvement
- Tool relevance per task

**Expected**: Grounding helps most on fact-dependent tasks, less on pure reasoning

**Effort**: ~10 hours

### E.3: Conversation Length Effects
**Question**: Does grounding benefit persist or decay over long conversations?

**Test Design**:
- Single exchange: measure grounding benefit
- After 5 exchanges: same measurement
- After 20 exchanges: same measurement
- (Track cache effects too)

**Measure**:
- LLM time trend
- Quality trend
- Hallucination accumulation
- Cache hit rate

**Expected**: Benefits persist but may decline (context window saturation?)

**Effort**: ~6 hours

---

## PHASE F: Human Factors (Optional, Long-term)

**Note**: These require human subjects, more complex IRB considerations

### F.1: Developer Experience
**Question**: Do developers actually USE better tools more effectively?

**Test Design**:
- Developers solve same problem with/without grounding tools
- Measure: completion time, error rate, code quality, satisfaction

### F.2: Trust Calibration
**Question**: Do developers trust grounded LLMs at the right level?

**Test Design**:
- Blind comparison: grounded vs. non-grounded responses
- Measure: trust vs. actual correctness

### F.3: Cognitive Load
**Question**: Does tool availability change how developers think?

**Test Design**:
- Think-aloud protocols
- Eye-tracking
- Task completion strategies

---

## Research Priority Matrix

| Phase | Focus | Complexity | Impact | Timeline | Effort |
|-------|-------|-----------|--------|----------|--------|
| **C** | Tool design | Low | HIGH | 2-3 weeks | 15 hrs |
| **D** | Mechanism | Medium | HIGH | 3-4 weeks | 20 hrs |
| **E** | Generalization | Medium | MEDIUM | 4-6 weeks | 30 hrs |
| **F** | Human factors | HIGH | MEDIUM | 8+ weeks | 40+ hrs |

**Recommendation**: Do C + D (5-7 weeks), then decide on E/F based on findings

---

## Interdependencies

```
Phase B (Complete) ✅
    ↓
Phase C (Granularity)
    ↓
Phase D (Mechanism) — Findings refine C
    ↓
Phase E (Generalization) — Apply C+D insights
    ↓
Phase F (Human factors) — Validate real-world impact
```

---

## Success Criteria

Each phase is "done" when:

**Phase C**: Can predict LLM time savings from tool design
**Phase D**: Can explain which hallucinations grounding fixes
**Phase E**: Can generalize findings to new models/tasks
**Phase F**: Can show developers actually benefit

---

## Artifact Status

- [x] Phase B: Complete (research questions discovered)
- [x] Research questions systematized (this document)
- [ ] Phase C: Experiment design ready, needs execution
- [ ] Phase D: Experiment design ready, needs execution
- [ ] Phase E: Experiment design ready, needs model access
- [ ] Phase F: Long-term planning, skip for now

---

## How to Use This Document

1. **For researchers**: Pick a phase, read the questions, implement the test design
2. **For reproducers**: Use these to validate findings on your own system
3. **For luna + team**: Use this as a roadmap for the next 2-3 months of research

Each question is:
- ✅ Clear (what are we testing?)
- ✅ Measurable (how do we measure?)
- ✅ Feasible (can we do this?)
- ✅ Connected (how does it relate to other work?)

---

**Next**: Pick C.1 or C.2 to start Phase C experiments 🚀
