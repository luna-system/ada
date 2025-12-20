# Ada VS Code - Manual Validation Checklist

**Date:** _________  
**Tester:** _________  
**Goal:** Determine if Ada is ready to replace Copilot

---

## PART 1: Context Awareness (CRITICAL)

### Test 1.1: Module Knowledge
- [ ] **Action:** Open chat, ask "what modules are in this project?"
- [ ] **Expected:** Lists actual modules from codebase-map.json
- [ ] **Result:** _____ modules mentioned
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

### Test 1.2: Architecture Understanding  
- [ ] **Action:** Ask "how does the specialist system work?"
- [ ] **Expected:** Explains protocol.py, auto-discovery, activation
- [ ] **Result:** Mentions (check all):
  - [ ] BaseSpecialist
  - [ ] should_activate()
  - [ ] process()
  - [ ] Auto-discovery from specialists/ folder
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

### Test 1.3: Data Flow Knowledge
- [ ] **Action:** Ask "how does brain/app.py use prompt_builder?"
- [ ] **Expected:** Explains API → prompt building → LLM flow
- [ ] **Result:** Mentions (check all):
  - [ ] build_prompt() function
  - [ ] Specialist activation
  - [ ] RAG context retrieval
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

**Part 1 Score:** ___/3 (must pass 3/3)

---

## PART 2: Latency Perception

### Test 2.1: Simple Query Speed
- [ ] **Action:** Ask "what is this file?" with memory_graph.py open
- [ ] **Start time:** _____
- [ ] **First token:** _____ (elapsed seconds)
- [ ] **Complete:** _____ (elapsed seconds)
- [ ] **Feels fast?** YES / NO
- **Notes:** ____________________________________________

### Test 2.2: Complex Query Speed
- [ ] **Action:** Ask "explain the entire biomimetic memory system"
- [ ] **First token:** _____ seconds
- [ ] **Token rate feels:** SLOW / OK / FAST
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

**Part 2 Score:** ___/2

---

## PART 3: Code Assistance Quality

### Test 3.1: Code Explanation
- [ ] **Action:** Select a function, ask "what does this do?"
- [ ] **Quality (1-5):** ___
  - Accurate? ___
  - Complete? ___
  - Uses codebase context? ___
- [ ] **Pass?** (≥4/5) YES / NO
- **Notes:** ____________________________________________

### Test 3.2: Implementation Help
- [ ] **Action:** Ask "how do I add a new specialist?"
- [ ] **Result:** Provides (check all):
  - [ ] Step-by-step instructions
  - [ ] References protocol.py
  - [ ] Mentions specialist-registry.json
  - [ ] Code examples
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

### Test 3.3: Debug Assistance
- [ ] **Action:** Paste an error message
- [ ] **Result:** Suggests (check all):
  - [ ] Root cause diagnosis
  - [ ] Specific fix
  - [ ] References relevant code
- [ ] **Pass?** YES / NO
- **Notes:** ____________________________________________

**Part 3 Score:** ___/3

---

## PART 4: Copilot Comparison

For each test, try BOTH Copilot and Ada:

### Test 4.1: Function Completion
**Code:** `def calculate_importance(`

| Assistant | Suggestion | Correct? | Context-aware? | Score (1-5) |
|-----------|------------|----------|----------------|-------------|
| Copilot   | __________ | Y/N      | Y/N            | ___         |
| Ada       | __________ | Y/N      | Y/N            | ___         |

**Winner:** __________

### Test 4.2: Import Suggestion
**Code:** `from brain.specialists import `

| Assistant | Suggestion | Correct? | Context-aware? | Score (1-5) |
|-----------|------------|----------|----------------|-------------|
| Copilot   | __________ | Y/N      | Y/N            | ___         |
| Ada       | __________ | Y/N      | Y/N            | ___         |

**Winner:** __________

### Test 4.3: Docstring Generation
**Code:** Function with no docstring

| Assistant | Quality | Google style? | Complete? | Score (1-5) |
|-----------|---------|---------------|-----------|-------------|
| Copilot   | _______ | Y/N           | Y/N       | ___         |
| Ada       | _______ | Y/N           | Y/N       | ___         |

**Winner:** __________

**Part 4 Score:** Ada wins ___/3, ties ___/3

---

## PART 5: Real-World Task

### Task: Implement Small Feature
**Goal:** Add a new helper function using only Ada's help

- [ ] **Step 1:** Ask Ada how to implement feature
- [ ] **Step 2:** Follow Ada's suggestions
- [ ] **Step 3:** Ask questions as needed
- [ ] **Step 4:** Complete implementation
- [ ] **Step 5:** Test it works

**Results:**
- Time taken: _____ minutes
- Number of Ada queries: _____
- Got stuck? YES / NO (if yes, where?) __________
- Feature works? YES / NO
- Would do again? YES / NO

**Compared to manual:**
- Faster? YES / NO / SAME
- Easier? YES / NO / SAME
- Better quality? YES / NO / SAME

**Pass?** YES / NO
**Notes:** ____________________________________________

---

## PART 6: Subjective Quality (Rate 1-5, 5=excellent)

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Relevance** (answers what you asked) | ___ | _____ |
| **Accuracy** (correct information) | ___ | _____ |
| **Completeness** (enough detail) | ___ | _____ |
| **Context awareness** (uses codebase) | ___ | _____ |
| **Code quality** (idiomatic suggestions) | ___ | _____ |
| **Latency** (feels fast enough) | ___ | _____ |
| **UX smoothness** (no glitches) | ___ | _____ |
| **Trust** (would rely on for real work) | ___ | _____ |

**Average:** _____ / 5.0 (need ≥4.0 to pass)

---

## PART 7: Issues & Blockers

List anything that made you say "I can't switch to Ada because...":

1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

Rate severity:
- [ ] **BLOCKER** - Cannot use Ada until fixed
- [ ] **MAJOR** - Significantly impacts workflow
- [ ] **MINOR** - Annoying but workable
- [ ] **NONE** - Ready to switch!

---

## FINAL DECISION

**Overall scores:**
- Context awareness: ___/3
- Latency: ___/2
- Code assistance: ___/3
- Copilot comparison: Ada wins ___/3
- Real-world task: PASS / FAIL
- Subjective quality: ___ / 5.0
- Blockers: ___

**Decision:**
- [ ] **READY** - Disable Copilot, use Ada full-time ✅
- [ ] **ALMOST** - Fix 1-2 issues, then switch ⚠️
- [ ] **NOT YET** - Significant work needed ❌

**Next steps:**
1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

---

**Completed by:** _________________  
**Date:** _________________  
**Signature:** _________________ 

---

## Appendix: Quick Commands

### Test latency manually:
```bash
# Time a simple query
time curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"hi","conversation_history":[]}'
```

### Check context ingestion:
```bash
# Count project context docs
curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"how many project_context documents are in chromadb?","conversation_history":[]}' \
  | grep -o '"content":"[^"]*"'
```

### Monitor resource usage:
```bash
# Watch brain memory
docker stats ada-v1-brain-1 --format "table {{.MemUsage}}\t{{.CPUPerc}}"
```
