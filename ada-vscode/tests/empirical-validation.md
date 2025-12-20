# Ada VS Code Extension - Empirical Validation Tests

**Goal:** Quantitatively validate Ada is ready to replace Copilot

**Date:** 2025-12-19  
**Status:** Phase 0.5 complete, ready for validation

---

## Test Suite Overview

### 1. Context Awareness Tests (CRITICAL)
**Tests Ada can see and use preloaded .ai/ documentation**

#### Test 1.1: Direct Module Query
```
Query: "what modules are in this project?"
Expected: Lists actual modules from codebase-map.json
Pass criteria: ≥5 real module names mentioned
```

#### Test 1.2: Architecture Question
```
Query: "how does the specialist system work?"
Expected: Explains protocol.py, auto-discovery, activation triggers
Pass criteria: Mentions BaseSpecialist, should_activate(), process()
```

#### Test 1.3: Cross-Module Relationship
```
Query: "how does brain/app.py use brain/prompt_builder.py?"
Expected: Explains data flow from API → prompt building → LLM
Pass criteria: Mentions build_prompt(), specialist activation
```

---

## 2. Code Completion Quality Tests

#### Test 2.1: Function Signature Completion
**File:** Create `test_completion_quality.py`
**Type:** `def calculate_importance(`
**Expected:** Complete with biomimetic signal parameters
**Gold standard:** Copilot suggestion on same code
**Metrics:**
- Syntax correctness (bool)
- Parameter accuracy (% match)
- Type hint presence (bool)

#### Test 2.2: Import Statement Completion
**File:** New Python file
**Type:** `from brain.specialists import `
**Expected:** Suggests real specialist classes
**Pass criteria:** ≥3 valid specialist imports

#### Test 2.3: Docstring Completion
**File:** Function with signature, no docstring
**Type:** `"""`
**Expected:** Generates relevant docstring
**Metrics:**
- Args documented (bool)
- Returns documented (bool)
- Google style format (bool)

---

## 3. Latency Benchmarks

#### Test 3.1: Time to First Token (TTFT)
```bash
# Measure from enter to first chunk
for i in {1..10}; do
  echo "Test $i" | ts -s '%.s'
  # Send query, timestamp first chunk
done
```
**Target:** <500ms for cached context  
**Acceptable:** <2000ms cold start

#### Test 3.2: Token Generation Rate
**Measure:** Tokens per second during streaming  
**Target:** ≥30 tok/s (Copilot parity)  
**Method:** Count chunks / total time

#### Test 3.3: End-to-End Latency
**From:** User presses enter  
**To:** Complete response rendered  
**Breakdown:**
- Network latency (client → brain)
- RAG retrieval time
- Prompt building time
- LLM generation time
- Streaming transmission time

---

## 4. Workflow Integration Tests

#### Test 4.1: Inline Code Explanation
**Action:** Select code block, ask "what does this do?"  
**Expected:** Explains with codebase context  
**Pass:** References related modules from .ai/ docs

#### Test 4.2: Refactoring Suggestions
**Action:** Select function, ask "how can I improve this?"  
**Expected:** Context-aware suggestions using project patterns  
**Pass:** Mentions actual project conventions

#### Test 4.3: Bug Diagnosis
**Action:** Paste error message  
**Expected:** Suggests fixes using codebase knowledge  
**Pass:** Points to relevant files/functions

#### Test 4.4: Documentation Lookup
**Action:** Ask "how do I add a new specialist?"  
**Expected:** Explains with examples from actual codebase  
**Pass:** References specialist-registry.json, protocol.py

---

## 5. Comparison Baseline (Copilot Parity)

### Side-by-Side Tests
**For each test above, record:**
1. Copilot suggestion (screenshot/text)
2. Ada suggestion (screenshot/text)
3. Subjective quality ranking (1-5)
4. Latency comparison

### Scoring Matrix
| Test | Copilot Score | Ada Score | Winner |
|------|---------------|-----------|--------|
| Context awareness | ? | ? | ? |
| Code completion | ? | ? | ? |
| Latency TTFT | ? | ? | ? |
| Latency tok/s | ? | ? | ? |
| Workflow integration | ? | ? | ? |

**Pass threshold:** Ada wins ≥3/5 categories OR ties on all

---

## 6. Stress Tests

#### Test 6.1: Large Context Window
**Query:** "explain the entire biomimetic memory system"  
**Expected:** Coherent explanation using multiple docs  
**Pass:** Doesn't hallucinate, cites real modules

#### Test 6.2: Rapid Fire Queries
```bash
# 10 queries in quick succession
for query in "${queries[@]}"; do
  # Send without waiting for completion
done
```
**Expected:** No crashes, responses remain coherent  
**Pass:** All queries answered correctly

#### Test 6.3: Cache Effectiveness
```bash
# Same query 3 times
Query 1: "list all specialists" (cold)
Query 2: "list all specialists" (warm)
Query 3: "list all specialists" (hot)
```
**Expected:** Query 2-3 faster than Query 1  
**Pass:** ≥30% speedup on cached queries

---

## 7. Memory & Resource Tests

#### Test 7.1: Extension Memory Usage
**Baseline:** Memory before chat  
**After 10 queries:** Memory delta  
**Pass:** <50MB increase

#### Test 7.2: Brain Service Load
```bash
docker stats ada-v1-brain-1 --no-stream
```
**During idle:** <200MB RAM  
**During query:** <500MB RAM  
**Pass:** No memory leaks after 20 queries

---

## 8. Error Handling Tests

#### Test 8.1: Brain Offline
**Action:** Stop brain container, send query  
**Expected:** Clear error message, reconnect attempt  
**Pass:** No VS Code crash

#### Test 8.2: Malformed Query
**Action:** Send empty query, very long query (10K chars)  
**Expected:** Graceful handling  
**Pass:** Returns valid response or error

#### Test 8.3: Ollama Timeout
**Action:** Query during Ollama model load  
**Expected:** Wait or clear timeout message  
**Pass:** Eventually succeeds or fails cleanly

---

## 9. Subjective Quality Tests (Human Eval)

Rate each 1-5 (5 = excellent):

- [ ] **Relevance:** Does Ada answer what you asked?
- [ ] **Accuracy:** Are the answers correct?
- [ ] **Completeness:** Does it provide enough detail?
- [ ] **Context awareness:** Does it use codebase knowledge?
- [ ] **Code quality:** Are suggestions idiomatic/correct?
- [ ] **Latency perception:** Does it FEEL fast enough?
- [ ] **UX smoothness:** Any UI glitches/issues?
- [ ] **Trust factor:** Would you rely on it for real work?

**Pass threshold:** Average ≥4.0/5.0

---

## 10. Real-World Task Tests

### Task 10.1: Implement New Feature
**Goal:** Add a new specialist using only Ada's help  
**Steps:**
1. Ask "how do I create a new specialist?"
2. Follow Ada's instructions
3. Ask questions as needed
4. Complete implementation

**Success criteria:**
- ✅ Specialist works without manual doc lookup
- ✅ Followed project conventions
- ✅ Ada caught errors/suggested fixes
- ✅ Faster than doing it manually

### Task 10.2: Debug Existing Code
**Goal:** Fix a bug using Ada  
**Steps:**
1. Paste error message
2. Ask for diagnosis
3. Apply suggested fix
4. Verify fix works

**Success criteria:**
- ✅ Correct diagnosis
- ✅ Working fix suggested
- ✅ Faster than manual debugging

### Task 10.3: Refactor Module
**Goal:** Improve code quality with Ada's help  
**Steps:**
1. Select module
2. Ask "how can I improve this?"
3. Apply suggestions
4. Run tests

**Success criteria:**
- ✅ Suggestions improve code
- ✅ Tests still pass
- ✅ Learned something new

---

## Automated Test Runner

```bash
#!/bin/bash
# Run all empirical tests

echo "=== ADA EMPIRICAL VALIDATION SUITE ==="
echo "Date: $(date)"
echo ""

# Test 1: Context Awareness
echo "TEST 1: Context Awareness"
echo "Query: what modules are in this project?" | # send to Ada
# Parse response, count module mentions

# Test 2: Latency
echo "TEST 2: Latency Benchmark"
for i in {1..10}; do
  start=$(date +%s%N)
  # Send query
  # Wait for first chunk
  end=$(date +%s%N)
  ttft=$(( (end - start) / 1000000 ))
  echo "  Run $i: ${ttft}ms TTFT"
done

# Test 3: Token rate
# ... measure during streaming

echo ""
echo "=== RESULTS ==="
echo "Context awareness: PASS/FAIL"
echo "Avg TTFT: Xms (target <500ms)"
echo "Token rate: Xtok/s (target >30)"
echo ""
echo "Overall: PASS/FAIL"
```

---

## Decision Matrix

### When is Ada ready for production use?

**MUST PASS (blockers):**
- ✅ Context awareness tests (all 3)
- ✅ No crashes under normal load
- ✅ Latency <2s TTFT
- ✅ Token rate >20 tok/s

**SHOULD PASS (quality):**
- ⚠️ Comparison tests tie or win vs Copilot
- ⚠️ Subjective quality >4.0/5.0
- ⚠️ Real-world task success

**NICE TO HAVE:**
- 💡 Cache speedup >30%
- 💡 Memory usage <50MB delta
- 💡 Wins >60% of side-by-side comparisons

---

## Next Steps After Validation

If tests pass:
1. **Document workflow** - Write "How to use Ada for coding" guide
2. **Disable Copilot** - Turn off to force Ada usage
3. **Monitor and iterate** - Track what works, what doesn't
4. **Prompt refinement** - Tune system prompts for code completion
5. **Celebrate** 🎉

If tests fail:
1. **Identify bottlenecks** - Where does it fall short?
2. **Prioritize fixes** - What's blocking vs nice-to-have?
3. **Iterate quickly** - Backend-only changes = fast iteration
4. **Re-test** - Run suite again after fixes

---

## Current Status

- [x] Phase 0.5: .ai/ preload complete
- [x] Chat streaming working
- [x] Context visibility fixed
- [ ] Empirical validation (YOU ARE HERE)
- [ ] Production use
- [ ] Copilot disabled

**Next:** Run these tests, measure everything, make data-driven decisions!
