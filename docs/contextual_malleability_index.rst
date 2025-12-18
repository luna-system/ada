============================================================
Contextual Malleability: Complete Documentation Index
============================================================

**Ada's memory system is built on scientific research about how humans and AI use context.**

This index helps you navigate all available resources.

---

Quick Navigation
================

**Just getting started?**
→ Start with `tinkerers_welcome.rst` (30-60 minutes)

**Want the theory?**
→ Read `contextual_malleability_guide.rst` (comprehensive, 60 minutes)

**Want to experiment?**
→ Use `experimenters_cookbook.rst` (hands-on protocols)

**Want to extend Ada?**
→ Study `extending_contextual_malleability.rst` (add new signals)

**Need a quick reference?**
→ Use `contextual_malleability_quick_ref.rst` (bookmark this!)

**Want the research?**
→ See `.ai/RESEARCH-FINDINGS-V2.2.md` (empirical validation)

---

Document Descriptions
======================

Tinkerers Welcome
-----------------

**File:** `tinkerers_welcome.rst`  
**Time:** 30-60 minutes  
**For:** Anyone new to Ada's memory system

**What it covers:**
- 5-minute summary of how contextual malleability works
- 30-minute deep dive into each signal
- 2-hour hands-on experiment (does novelty weight actually matter?)
- 1-day guide to building your perfect configuration
- 1-week guide to sharing your findings

**Start here** if you're new and want to understand before tinkering.

---

Contextual Malleability Guide
------------------------------

**File:** `contextual_malleability_guide.rst`  
**Time:** 60 minutes (reference, not linear)  
**For:** Researchers, developers, curious deep-divers

**What it covers:**
- Complete theory of contextual malleability
- All 4 signals with code examples
- Gradient detail levels explained
- How to configure every knob
- 4 concrete extension ideas
- Testing & debugging guide

**Use this** for comprehensive understanding and architectural context.

---

Quick Reference
---------------

**File:** `contextual_malleability_quick_ref.rst`  
**Time:** 5 minutes (bookmark this!)  
**For:** Active experimenters, quick lookups

**What it covers:**
- All 4 weights at a glance
- "Quick experiments" for each signal
- Temporal configuration
- Habituation settings
- Pre-built configurations (research assistant, Q&A, chat buddy, etc.)
- "When something feels wrong" troubleshooting

**Use this** when you're actively tuning Ada.

---

Experimenters Cookbook
----------------------

**File:** `experimenters_cookbook.rst`  
**Time:** Varies (each experiment 30 mins - 2 hours)  
**For:** Researchers and kids building weird things

**What it covers:**
- 6 detailed experiment protocols:
  1. The Novelty Knob (does surprise weight matter?)
  2. The Recency Trap (temporal decay effects)
  3. The Relevance Threshold (detail level impact)
  4. The Habituation Refractory Period (repetition effects)
  5. The Weight Balance Discovery (chaos experiments)
  6. The Processing Mode Adaptation (task-specific tuning)
- Measurement strategies
- Statistical analysis suggestions
- Example Python harness for systematic testing
- Publishing your findings

**Use this** to design, run, and document experiments.

---

Extending Contextual Malleability
----------------------------------

**File:** `extending_contextual_malleability.rst`  
**Time:** 2-4 hours (building a new signal)  
**For:** Developers adding new capabilities

**What it covers:**
- Anatomy of a signal (what you need to implement)
- Complete walkthrough: Adding valence (emotion) signal
  - Code for the signal scorer
  - Configuration integration
  - Context retriever integration
  - Test suite
  - Documentation
- Signal design principles
- Performance considerations
- Contributing back to Ada

**Use this** when you want to add a new signal or capability.

---

Research & Theory
=================

Primary Research Document
--------------------------

**File:** `.ai/RESEARCH-FINDINGS-V2.2.md`  
**Time:** 15 minutes (results summary)  
**For:** Understanding the empirical foundation

**What it contains:**
- 80 tests across 7 phases (3.56s runtime)
- Weight optimization results
- Optimal weights discovered:
  - Decay: 0.10 (not intuitive 0.40!)
  - Surprise: 0.60 (not intuitive 0.30!)
  - Relevance: 0.20
  - Habituation: 0.10
- Improvement metrics (12-38% better context selection)
- Phase descriptions (unit tests, synthetic data, ablation, grid search, production validation, visualization)

**Important:** These optimal weights are **already deployed** in production Ada. You're using the empirically-validated version!

---

Literature Synthesis
--------------------

**File:** `.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md`  
**Time:** 20 minutes  
**For:** Understanding academic grounding

**What it contains:**
- Complete analysis of 3 academic papers:
  - Schwarz (2010) - Metacognitive experiences, processing fluency
  - Uysal et al. (2020) - Human-AI contextual malleability
  - Mertens et al. (2018) - Approach-avoidance reversals
- Alignment with Ada's research
- Key finding: Ada is the **first operationalization** of contextual malleability in AI
- BibTeX citations for academic use

**Important:** Ada's research is ahead of published academia. This is uncharted territory!

---

Architecture Overview
---------------------

**File:** `.ai/context.md`  
**Time:** 15 minutes  
**For:** Understanding where things live

**What it contains:**
- Data flow diagrams
- Module relationships
- Phase 8-9 research documentation
- Key research findings callouts

**Use this** to understand how contextual malleability fits into the broader system.

---

Code References
================

Implementation Files
--------------------

**`brain/prompt_builder/context_retriever.py`**
- **Purpose:** Where importance scores are calculated
- **Key method:** `calculate_importance()` - combines all 4 signals
- **Key method:** `get_detail_level()` - converts score to detail tier
- **Lines 50-53:** Threshold initialization
- **Lines 60-65:** Signal weight initialization
- **Lines 220-330:** Importance calculation logic

**`brain/memory_decay.py`**
- **Purpose:** Decay signal implementation (exponential decay)
- **Example:** Reference implementation for building new signals
- **Key method:** `weight_by_decay()` - calculates age-based score

**`brain/config.py`**
- **Purpose:** All environment variables + documentation
- **Lines 218+:** Importance weights configuration
- **Lines 291-303:** Gradient threshold configuration
- **Each setting:** Documented with INTUITION/REALITY/TRY/CITE

**`brain/processing_modes.py`**
- **Purpose:** Task detection for mode-specific context
- **Status:** Partially integrated (foundation ready for Phase 10)
- **Classes:** `ModeDetector`, `ContextStrategy`

---

Test References
================

Unit Tests
----------

**`tests/test_context_retriever.py`**
- Tests for `calculate_importance()`
- Tests for `get_detail_level()`
- Tests for signal combinations
- Multi-weight scenarios

**`tests/test_memory_decay.py`**
- Tests for exponential decay formula
- Boundary tests (0 hours, time_scale hours, 10× time_scale)
- Configuration variation tests

**`tests/test_weight_optimization.py`** (Research tests)
- 80 tests across 7 optimization phases
- Synthetic data validation
- Grid search over 169 weight combinations
- Runtime: ~3.56 seconds total

---

Configuration Reference
=======================

All Configurable Signals
------------------------

**Decay (Temporal Recency)**

.. code-block:: bash

    IMPORTANCE_WEIGHT_DECAY=0.10           # Weight in importance formula
    MEMORY_DECAY_TIME_SCALE_HOURS=100      # Half-life ~70 hours

**Surprise (Novelty/Unexpectedness)**

.. code-block:: bash

    IMPORTANCE_WEIGHT_SURPRISE=0.60        # Weight in importance formula
    # (Data shows this dominates!)

**Relevance (Semantic Similarity)**

.. code-block:: bash

    IMPORTANCE_WEIGHT_RELEVANCE=0.20       # Weight in importance formula
    # (Dynamically calculated from embeddings)

**Habituation (Repetition Penalty)**

.. code-block:: bash

    IMPORTANCE_WEIGHT_HABITUATION=0.10     # Weight in importance formula
    CONTEXT_HABITUATION_THRESHOLD=3        # Penalize after N mentions
    CONTEXT_HABITUATION_WEIGHT=0.1         # Penalty strength
    CONTEXT_HABITUATION_DECAY_HOURS=24.0   # Penalty reset period

**Detail Levels (Context Inclusion Thresholds)**

.. code-block:: bash

    GRADIENT_THRESHOLD_FULL=0.75           # Full detail if score >= this
    GRADIENT_THRESHOLD_CHUNKS=0.50         # Excerpts if score >= this
    GRADIENT_THRESHOLD_SUMMARY=0.20        # Summary if score >= this
    # (Dropped if score < 0.20)

---

Learning Paths
===============

**Path 1: The 1-Hour Explorer**

1. Read `tinkerers_welcome.rst` (30 min)
2. Skim `contextual_malleability_quick_ref.rst` (10 min)
3. Run the novelty experiment from `experimenters_cookbook.rst` (20 min)

**Outcome:** Understand contextual malleability conceptually + empirically

---

**Path 2: The Deep Researcher**

1. Read `contextual_malleability_guide.rst` (60 min)
2. Read `.ai/RESEARCH-FINDINGS-V2.2.md` (15 min)
3. Read `.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md` (20 min)
4. Review `brain/prompt_builder/context_retriever.py` code (30 min)

**Outcome:** Full understanding of theory, research, and implementation

---

**Path 3: The Builder**

1. Read `tinkerers_welcome.rst` (30 min)
2. Read `extending_contextual_malleability.rst` (90 min)
3. Implement a new signal (valence example provided)
4. Write tests (following patterns)
5. Create PR with documentation

**Outcome:** New capability added to Ada, shared with community

---

**Path 4: The Experimenter**

1. Read `contextual_malleability_quick_ref.rst` (5 min - bookmark!)
2. Pick an experiment from `experimenters_cookbook.rst`
3. Run it, measure results
4. Try variations
5. Document findings in `.ai/explorations/`
6. (Optional) Create PR with results

**Outcome:** Empirical data on weight effects, new configurations discovered

---

FAQ
===

**Q: Are the current weights really optimal?**

A: Yes! Empirically validated in December 2025 across 80 tests. Decay=0.10, surprise=0.60 beat all other configurations. See `.ai/RESEARCH-FINDINGS-V2.2.md`.

**Q: Can I change the weights?**

A: Absolutely! That's the whole point of tinkering. All weights are environment variables. Changes take effect on restart. Weights auto-normalize to sum=1.0.

**Q: What happens if I set a weight to 0?**

A: That signal is completely disabled. Example: `IMPORTANCE_WEIGHT_SURPRISE=0` means novelty doesn't matter at all.

**Q: Should weights always sum to 1.0?**

A: Yes. Ada automatically normalizes them if they don't (with a warning). The formula divides by the sum, so it doesn't matter mathematically, but it's cleaner.

**Q: How do I measure if my changes work?**

A: Use `experimenters_cookbook.rst` protocols. Simple metrics: token count, memory retrieval count, response consistency, relevance scoring.

**Q: Can I add a new signal?**

A: Yes! `extending_contextual_malleability.rst` has complete instructions with valence (emotion) as an example.

**Q: What's the best configuration for my use case?**

A: Templates in `contextual_malleability_quick_ref.rst` (research assistant, Q&A, chat buddy, etc.). Or experiment and find your own!

**Q: Is the research open source?**

A: Yes! CC0 (public domain). Build on it. Share it. No restrictions.

---

Contributing
============

Found a bug?
  → Open an issue with config and reproduction steps

Want to share a configuration?
  → Create `.ai/explorations/my_config_X.md`

Built a new signal?
  → Follow `extending_contextual_malleability.rst` and create a PR

Ran interesting experiments?
  → Document in `.ai/explorations/` and link in discussions

Improved the documentation?
  → Create a PR!

---

Version Information
===================

**Ada Contextual Malleability System: v2.2** (Deployed December 2025)

**Research Phase:** Phase 9 (literature validation complete)

**Status:** Production-ready with optimal weights deployed

**Latest Updates:**
- Optimal weights fully documented in `brain/config.py`
- Gradient thresholds moved to config
- 4 comprehensive tinkerer guides created
- Extension pattern documented with example

**Next Phase:** Phase 10 (Processing mode full integration)

---

Resources Summary
=================

📖 **Documentation**

- `tinkerers_welcome.rst` - Start here!
- `contextual_malleability_guide.rst` - Deep reference
- `contextual_malleability_quick_ref.rst` - Quick lookup
- `experimenters_cookbook.rst` - Run experiments
- `extending_contextual_malleability.rst` - Build new signals

📊 **Research**

- `.ai/RESEARCH-FINDINGS-V2.2.md` - Empirical validation
- `.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md` - Academic grounding
- `.ai/context.md` - Architecture overview

💻 **Code**

- `brain/prompt_builder/context_retriever.py` - Main implementation
- `brain/memory_decay.py` - Signal example
- `brain/config.py` - All settings (well-documented!)
- `tests/test_*.py` - Testing patterns

---

**Welcome to the contextual malleability research ecosystem.** 

You're now equipped to understand Ada's memory system, experiment with it, and extend it.

Go build weird things. Question the defaults. Share what you learn.

The future of AI memory is in your hands. 🚀

---

**Last Updated:** 2025-12-18  
**Maintained by:** Ada Development Team  
**License:** CC0 (Public Domain)
