# 🚀 Ada VS Code - Live Validation Playbook

**Date:** December 19, 2025  
**Status:** Phase 0.5 Complete, Ready for Real-World Testing

---

## Quick Setup (if not installed)

```bash
cd ada-vscode
code --install-extension ada-code-0.1.0.vsix
# Reload VS Code window
```

---

## THE MONEY TEST - Context Awareness

Open Ada chat panel and run these **3 CRITICAL TESTS**:

### ✅ Test 1: "what modules are in this project?"

**Expected:** Should list actual modules from codebase-map.json:
- brain/app.py
- brain/prompt_builder.py
- brain/rag_store.py
- brain/specialists/*
- etc.

**Pass Criteria:** ≥5 real module names mentioned

**Your Result:**
```
[paste Ada's response here]
```

Pass? ☐ YES ☐ NO

---

### ✅ Test 2: "how does the specialist system work?"

**Expected:** Should explain from .ai/context.md:
- Protocol-based design (BaseSpecialist)
- Auto-discovery from specialists/ folder
- should_activate() and process() methods
- Priority-based context injection

**Pass Criteria:** Mentions at least 3 of those concepts

**Your Result:**
```
[paste Ada's response here]
```

Pass? ☐ YES ☐ NO

---

### ✅ Test 3: "how does brain/app.py use prompt_builder?"

**Expected:** Should explain data flow from .ai/codebase-map.json:
- API endpoint calls build_prompt()
- Specialist activation
- RAG context retrieval
- Streaming to LLM

**Pass Criteria:** Accurate explanation with specific function names

**Your Result:**
```
[paste Ada's response here]
```

Pass? ☐ YES ☐ NO

---

## If All 3 Pass: CONTEXT AWARENESS VALIDATED ✅

You now have **machine timescale codebase knowledge!**

---

## Next Level Tests (Optional but Fun)

### Speed Test
Ask: "what is memory_graph.py?" with that file open

Time it:
- **First token:** _____ seconds
- **Complete:** _____ seconds
- **Feels fast?** ☐ YES ☐ NO

### Code Help Test
Select a function, ask: "what does this do?"

- **Accurate?** ☐ YES ☐ NO
- **Uses codebase context?** ☐ YES ☐ NO
- **Quality (1-5):** _____

### Implementation Help Test
Ask: "how do I add a new specialist?"

- **Provides steps?** ☐ YES ☐ NO  
- **References actual files?** ☐ YES ☐ NO
- **Would you follow these instructions?** ☐ YES ☐ NO

---

## The Million Dollar Question

**Can Ada replace Copilot for THIS codebase?**

Rate confidence (1-10): _____

**If ≥7:** Time to disable Copilot and dogfood Ada! 🐕‍🦺  
**If 5-6:** Almost there, note what's missing below  
**If ≤4:** Significant work needed, list blockers below

---

## Notes / Blockers

What would make you switch to Ada full-time?

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

## DECISION TIME

☐ **SHIP IT** - Disable Copilot, Ada is the primary assistant  
☐ **ALMOST** - Fix 1-2 things first: _______________  
☐ **NOT YET** - Need: _______________

---

**Remember:** You built this from scratch in one session. You're already doing the impossible. Now let's see if it works! 🚀

**Next:** Open VS Code, run these 3 tests, come back with results!
