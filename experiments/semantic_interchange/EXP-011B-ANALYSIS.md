
# EXP-011B Results: SIF Extraction Aggressiveness

**Timestamp:** 2025-12-30T16:57:03.945094+00:00
**Source:** /home/luna/Code/ada/experiments/semantic_interchange/alice_in_wonderland.txt (151,191 bytes)

## Runs Completed


### Run 1: Baseline (Conservative)

**Configuration:**
- Entity target: 5-15
- Fact target: 10-30
- Output token limit: 4000
- Prompt emphasis: "Extract only the most important entities and facts."

**Results:**
- Entities extracted: 5
- Facts extracted: 5
- Output size: 1,848 bytes
- Compression ratio: **81.8x**
- Accuracy: **26.7%**
- Hallucination resistance: **100.0%** ✨


### Run 2: Aggressive (Run 2)

**Configuration:**
- Entity target: 30-50
- Fact target: 50-100
- Output token limit: 8000
- Prompt emphasis: "Extract ALL key characters, relationships, and events. Be comprehensive."

**Results:**
- Entities extracted: 5
- Facts extracted: 9
- Output size: 3,166 bytes
- Compression ratio: **47.8x**
- Accuracy: **33.3%**
- Hallucination resistance: **100.0%** ✨


### Run 3: Maximum Detail (TODAY)

**Configuration:**
- Entity target: 50-100
- Fact target: 100-200
- Output token limit: 12000
- Prompt emphasis: "Extract EVERY significant character, all relationships, all plot points, all dialogue context. Prioritize COVERAGE over brevity."

**Results:**
- Entities extracted: 12
- Facts extracted: 18
- Output size: 5,200 bytes
- Compression ratio: **29.1x**
- Accuracy: **46.7%**
- Hallucination resistance: **100.0%** ✨


## Summary Analysis

| Metric | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| Entities | 5 | 5 | 12 |
| Facts | 5 | 9 | 18 |
| Compression | 81.8x | 47.8x | 29.1x |
| Accuracy | 26.7% | 33.3% | 46.7% |

### Key Finding

Aggressiveness tuning shows **clear tradeoff pattern**:
- More entities/facts requested → Better comprehension
- But still maintains 30-50x compression (vs expected 137x)
- **Sweet spot appears to be at Run 3 aggressiveness**
- All runs maintain **100% hallucination resistance** ✨

### Recommendation for v4.0

Use Run 3 configuration as DEFAULT:
- 50-100 entity targets
- 100-200 fact targets  
- 12K output token limit
- Achieves: ~29.1x compression + 46.7% accuracy

This balances:
- Portability (still highly compressed)
- Accuracy (respectable comprehension)
- Honesty (perfect hallucination resistance)
