============================================================
Ada's Contextual Malleability: Start Here! 🚀
============================================================

**All the documentation you need to understand, experiment with, and extend Ada's memory system.**

---

🎯 Choose Your Path
====================

**⏱️ "I have 5 minutes"**
→ Read this file  
→ Then: `docs/contextual_malleability_quick_ref.rst` (bookmark it!)

**👶 "I'm new to this (30-60 min)"**
→ Start: `docs/tinkerers_welcome.rst`  
→ Then: Pick an experiment from `docs/experimenters_cookbook.rst`

**🧪 "I want to experiment (2 hours)"**
→ Bookmark: `docs/contextual_malleability_quick_ref.rst`  
→ Pick experiment: `docs/experimenters_cookbook.rst`  
→ Reference: `docs/contextual_malleability_guide.rst` if you need theory

**🔬 "I'm a researcher (60 min)"**
→ Deep reference: `docs/contextual_malleability_guide.rst`  
→ Research: `.ai/RESEARCH-FINDINGS-V2.2.md`  
→ Academic grounding: `.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md`

**👨‍💻 "I want to extend Ada (2-4 hours)"**
→ Extension guide: `docs/extending_contextual_malleability.rst`  
→ Reference: `brain/config.py` and `brain/memory_decay.py`  
→ Code: `brain/prompt_builder/context_retriever.py`

---

📚 Documentation Map
===================

.. code-block:: text

    LANDING PAGE (you are here)
    │
    ├─→ INDEX (master navigation)
    │   └─ docs/contextual_malleability_index.rst
    │
    ├─→ QUICK REFERENCE (bookmark this!)
    │   └─ docs/contextual_malleability_quick_ref.rst
    │
    ├─→ LEARNING PATHS
    │   ├─ Tinkerers: docs/tinkerers_welcome.rst
    │   ├─ Deep: docs/contextual_malleability_guide.rst
    │   ├─ Experiments: docs/experimenters_cookbook.rst
    │   └─ Extensions: docs/extending_contextual_malleability.rst
    │
    ├─→ RESEARCH
    │   ├─ Findings: .ai/RESEARCH-FINDINGS-V2.2.md
    │   └─ Literature: .ai/explorations/LITERATURE-SYNTHESIS-...
    │
    ├─→ CODE
    │   ├─ Config: brain/config.py
    │   ├─ Core: brain/prompt_builder/context_retriever.py
    │   └─ Example: brain/memory_decay.py
    │
    └─→ VERIFICATION
        └─ docs/CONTEXTUAL_MALLEABILITY_ACCESSIBILITY_CHECKLIST.md

---

🎓 What You'll Learn
====================

**The 4 Signals (and their weights):**

.. code-block:: text

    Decay (0.10)     → How old? Newer memories matter more
    Surprise (0.60)  → How unexpected? Novel things get attention
    Relevance (0.20) → How related? Topically relevant matters
    Habituation (0.10) → How repeated? Familiar stuff gets penalized

**Key Finding from Research:** 
   Surprise dominates! (0.60, not intuitive 0.30)
   Empirically proven across 80 tests in December 2025

**Configuration:**
   Every weight is an environment variable
   Every variable is documented with why it matters
   You can experiment fearlessly

**Experiments:**
   6 detailed protocols ready to run
   Measurement strategies included
   Clear path to share your findings

**Extensions:**
   Add new signals following the pattern
   Complete valence signal example provided
   Contributing guidelines clear

---

⚡ Quick Start (5 Minutes)
==========================

**1. Understand the formula**

.. code-block:: text

    importance = 0.10*decay + 0.60*surprise + 0.20*relevance + 0.10*habituation

**2. Know the detail levels**

.. code-block:: text

    Score >= 0.75 → Full detail (include everything)
    Score >= 0.50 → Chunks (include excerpts)
    Score >= 0.20 → Summary (one sentence)
    Score < 0.20  → Dropped (not included)

**3. See a memory's life**

.. code-block:: text

    Day 0, Hour 0: "I love hiking"
    └─ Score 0.85 → FULL detail → "You love hiking"
    
    Day 1, Hour 0: (after discussing 3x)
    └─ Score 0.35 → CHUNKS → "You mentioned hiking"
    
    Day 5, Hour 0: (old but suddenly relevant)
    └─ Score 0.15 → SUMMARY → "You like hiking"
    
    Day 30, Hour 0: (very old, but we can recover it)
    └─ Resurfaces if needed in context

**That's it.** Everything else is tuning these weights.

---

🔧 Common Configurations
========================

**Research Assistant** (maximize novelty)

.. code-block:: bash

    export IMPORTANCE_WEIGHT_DECAY=0.05
    export IMPORTANCE_WEIGHT_SURPRISE=0.70
    export IMPORTANCE_WEIGHT_RELEVANCE=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

**Chat Buddy** (balanced)

.. code-block:: bash

    export IMPORTANCE_WEIGHT_DECAY=0.15
    export IMPORTANCE_WEIGHT_SURPRISE=0.50
    export IMPORTANCE_WEIGHT_RELEVANCE=0.25
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

**Q&A System** (maximize relevance)

.. code-block:: bash

    export IMPORTANCE_WEIGHT_DECAY=0.10
    export IMPORTANCE_WEIGHT_SURPRISE=0.10
    export IMPORTANCE_WEIGHT_RELEVANCE=0.60
    export IMPORTANCE_WEIGHT_HABITUATION=0.20

**Copy from:** `docs/contextual_malleability_quick_ref.rst`

---

🧪 Run an Experiment (30 min)
=============================

**Question:** Does surprise weight actually matter?

**Protocol:**

.. code-block:: bash

    # Config A: Low surprise
    export IMPORTANCE_WEIGHT_SURPRISE=0.30
    docker compose restart brain
    
    # Query: "Tell me something surprising"
    # Note: Does Ada find novel stuff?
    
    # Config B: High surprise  
    export IMPORTANCE_WEIGHT_SURPRISE=0.70
    docker compose restart brain
    
    # Query: "Tell me something surprising"
    # Compare: More novelty-focused?

**Measurement:**
- Word count on "surprising" topic
- Diversity of context
- Response tone

**More experiments:** `docs/experimenters_cookbook.rst` (6 detailed protocols)

---

🛠️ Add a New Signal (2-4 hours)
================================

**Example:** Adding valence (emotion) signal

**Steps:**

1. Create `brain/memory_valence.py` (signal scorer)
2. Add to `brain/config.py` (environment variable)
3. Integrate into `context_retriever.py` (importance formula)
4. Write tests in `tests/test_memory_valence.py`
5. Document in `docs/contextual_malleability_guide.rst`
6. Create PR!

**Complete walkthrough:** `docs/extending_contextual_malleability.rst`

---

📖 What Each Guide Does
=======================

**tinkerers_welcome.rst** (1300 lines)
   For: Tinkerers and kids
   Time: 30-60 minutes
   What: Concept → experiment → build custom config
   Style: Hands-on, narrative-driven

**contextual_malleability_guide.rst** (560 lines)
   For: Researchers and deep learners
   Time: 60+ minutes reference
   What: Every detail about signals and configuration
   Style: Comprehensive reference

**contextual_malleability_quick_ref.rst** (320 lines)
   For: Active experimenters (BOOKMARK THIS!)
   Time: 5 minutes to find what you need
   What: All settings, templates, troubleshooting
   Style: Lookup reference

**experimenters_cookbook.rst** (600 lines)
   For: Researchers and kids building experiments
   Time: 30 min - 2 hours per experiment
   What: 6 detailed experiment protocols
   Style: How-to guide

**extending_contextual_malleability.rst** (750 lines)
   For: Developers extending Ada
   Time: 2-4 hours to build a signal
   What: Complete signal development walkthrough
   Style: Step-by-step tutorial

---

🔍 Finding Specific Information
================================

**"How do I configure Ada?"**
→ `brain/config.py` (everything documented)  
→ `docs/contextual_malleability_quick_ref.rst` (quick lookup)

**"Why is surprise weight 0.60?"**
→ `brain/config.py` (40+ lines of explanation)  
→ `.ai/RESEARCH-FINDINGS-V2.2.md` (empirical validation)

**"How do I run an experiment?"**
→ `docs/experimenters_cookbook.rst` (6 detailed protocols)

**"Can I add a new signal?"**
→ `docs/extending_contextual_malleability.rst` (complete walkthrough)

**"What does valence signal do?"**
→ `docs/extending_contextual_malleability.rst` (full example)

**"Is the code understandable?"**
→ `brain/prompt_builder/context_retriever.py` (well-commented)

**"Is the research sound?"**
→ `.ai/RESEARCH-FINDINGS-V2.2.md` (80 tests across 7 phases)  
→ `.ai/explorations/LITERATURE-SYNTHESIS-...` (academic grounding)

---

💡 Key Insights
===============

✨ **The Surprise Dominance**
   
   Intuition: "Recency matters most"
   Reality: "Novelty matters most!"
   Research: Schwarz (2010) - disfluency triggers analysis
   Weight: 0.60 (not intuitive 0.30)
   Improvement: 12-38% better context selection

✨ **Weights Sum to 1.0**

   Formula always normalizes
   You can set weights to any values
   Automatically balanced
   Experiment freely!

✨ **Public Domain**

   CC0 license (no restrictions)
   Anyone can build on this research
   No gatekeeping
   Free forever

✨ **Transparent Configuration**

   Every knob is an environment variable
   Every variable is documented
   No hidden decisions
   You understand everything

---

🚀 Getting Started Now
=======================

**Right Now (5 min):**
- Read: This quick start (you're doing it!)
- Bookmark: `docs/contextual_malleability_quick_ref.rst`
- Know: The 4 signals and why surprise dominates

**Next (30 min):**
- Read: `docs/tinkerers_welcome.rst`
- Understand: How each signal works in practice

**Then (2 hours):**
- Pick: An experiment from `docs/experimenters_cookbook.rst`
- Run: The protocol
- Measure: The results
- Share: Your findings!

**Eventually:**
- Read: `docs/extending_contextual_malleability.rst`
- Build: A new signal
- Contribute: Back to Ada

---

❓ FAQ
======

**Q: Can I break Ada by changing weights?**
A: No! Weights auto-normalize. You can always reset.

**Q: Is all this open source?**
A: Yes! CC0 (public domain). No restrictions.

**Q: What's the best configuration for me?**
A: Use templates, then experiment. See `quick_ref.rst`

**Q: How do I know if my changes work?**
A: Use experiment protocols from `experimenters_cookbook.rst`

**Q: Can kids understand this?**
A: Yes! `tinkerers_welcome.rst` is designed for that.

**Q: Is there research behind this?**
A: Yes! 80 tests + academic papers. See `.ai/RESEARCH-FINDINGS-V2.2.md`

---

📚 Complete File List
======================

**In docs/:**
- `contextual_malleability_index.rst` - Master index
- `tinkerers_welcome.rst` - For newcomers
- `contextual_malleability_guide.rst` - Deep reference
- `contextual_malleability_quick_ref.rst` - Quick lookup (BOOKMARK!)
- `experimenters_cookbook.rst` - Experiment protocols
- `extending_contextual_malleability.rst` - Extension guide
- `CONTEXTUAL_MALLEABILITY_ACCESSIBILITY_CHECKLIST.md` - Verification

**In .ai/:**
- `RESEARCH-FINDINGS-V2.2.md` - Empirical validation
- `explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md` - Academic grounding
- `context.md` - Architecture overview

**Configuration:**
- `brain/config.py` - All settings with documentation

**Code:**
- `brain/prompt_builder/context_retriever.py` - Core implementation
- `brain/memory_decay.py` - Signal example

---

✨ Philosophy
==============

This system is built on:

✅ **Transparency** - Every choice is explained with research
✅ **Accessibility** - Kids can understand it
✅ **Extensibility** - You can build on it
✅ **Openness** - No gatekeeping, no restrictions
✅ **Empowerment** - You're encouraged to experiment

**Go tinker. Build weird things. Question the defaults. Share what you learn.**

That's what Ada is built for. 🚀

---

**Your Next Step:**

1. Pick your path (above)
2. Read the suggested document
3. Tinker
4. Share
5. Build weird things

🌟 Welcome to Ada's contextual malleability ecosystem!
