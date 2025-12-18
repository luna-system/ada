============================================================
Quick Reference: Tweaking Ada's Memory System
============================================================

**One-page guide to configuring contextual malleability**

---

The Signal Weights (What Matters?)
====================================

**What each weight does:**

.. code-block:: bash

    IMPORTANCE_WEIGHT_DECAY=0.10        # Recency (age of memory)
    IMPORTANCE_WEIGHT_SURPRISE=0.60     # Novelty (how unexpected?)
    IMPORTANCE_WEIGHT_RELEVANCE=0.20    # Similarity (related to query?)
    IMPORTANCE_WEIGHT_HABITUATION=0.10  # Repetition (how familiar?)

**These must sum to 1.0**

**Quick experiments:**

.. code-block:: bash

    # Make Ada more novelty-focused (AI as discoverer)
    export IMPORTANCE_WEIGHT_SURPRISE=0.80
    export IMPORTANCE_WEIGHT_DECAY=0.05
    export IMPORTANCE_WEIGHT_RELEVANCE=0.10
    export IMPORTANCE_WEIGHT_HABITUATION=0.05

    # Make Ada more Q&A focused (fact machine)
    export IMPORTANCE_WEIGHT_RELEVANCE=0.60
    export IMPORTANCE_WEIGHT_SURPRISE=0.20
    export IMPORTANCE_WEIGHT_DECAY=0.10
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

    # Make Ada temporal (recent matters most)
    export IMPORTANCE_WEIGHT_DECAY=0.50
    export IMPORTANCE_WEIGHT_SURPRISE=0.25
    export IMPORTANCE_WEIGHT_RELEVANCE=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

---

The Detail Levels (How Much to Include?)
=========================================

Once Ada scores a memory, it decides how much detail:

.. code-block:: bash

    GRADIENT_THRESHOLD_FULL=0.75    # Score >= this: Include everything
    GRADIENT_THRESHOLD_CHUNKS=0.50  # Score >= this: Include excerpts
    GRADIENT_THRESHOLD_SUMMARY=0.20 # Score >= this: One sentence
    # Score < 0.20: Drop entirely

**Memory lifecycle example:**

.. code-block:: text

    Score: 0.85  → FULL      (User asked about weather directly)
    Score: 0.65  → CHUNKS    (Related to current topic)
    Score: 0.35  → SUMMARY   (Mentioned but not central)
    Score: 0.05  → DROPPED   (Too old/unrelated/repetitive)

**Quick experiments:**

.. code-block:: bash

    # Ultra-selective (minimal context, faster responses)
    export GRADIENT_THRESHOLD_FULL=0.85
    export GRADIENT_THRESHOLD_CHUNKS=0.60
    export GRADIENT_THRESHOLD_SUMMARY=0.30

    # Permissive (maximum context, longer responses)
    export GRADIENT_THRESHOLD_FULL=0.60
    export GRADIENT_THRESHOLD_CHUNKS=0.35
    export GRADIENT_THRESHOLD_SUMMARY=0.10

---

Temporal Configuration
======================

**How fast do memories fade?**

.. code-block:: bash

    export MEMORY_DECAY_TIME_SCALE_HOURS=100  # Default: ~4 days

**What this means:**

- After 100 hours, memory importance is cut by ~2.7x (1/e)
- At 200 hours, cut by ~7.4x (1/e²)
- Half-life: ~70 hours

**Quick experiments:**

.. code-block:: bash

    # Aggressive: 1 day half-life (forget quickly)
    export MEMORY_DECAY_TIME_SCALE_HOURS=24

    # Balanced: 4 days half-life (current default)
    export MEMORY_DECAY_TIME_SCALE_HOURS=100

    # Permissive: 2 weeks half-life (remember longer)
    export MEMORY_DECAY_TIME_SCALE_HOURS=336

---

Habituation (Repetition Penalty)
=================================

**When a topic gets repetitive:**

.. code-block:: bash

    export CONTEXT_HABITUATION_THRESHOLD=3        # Penalize after 3 mentions
    export CONTEXT_HABITUATION_WEIGHT=0.1         # 10% weight when habituated
    export CONTEXT_HABITUATION_DECAY_HOURS=24.0   # Penalty resets after 24hr

**Example:**

- Topic discussed 2x: Full importance
- Topic discussed 3+ times: Importance × 0.1 (90% penalty!)
- After 24 hours: Penalty resets

**Quick experiments:**

.. code-block:: bash

    # Strict: Penalize early, reset slowly
    CONTEXT_HABITUATION_THRESHOLD=2 CONTEXT_HABITUATION_WEIGHT=0.05 CONTEXT_HABITUATION_DECAY_HOURS=72

    # Permissive: Allow repetition, reset quickly
    CONTEXT_HABITUATION_THRESHOLD=5 CONTEXT_HABITUATION_WEIGHT=0.5 CONTEXT_HABITUATION_DECAY_HOURS=12

---

Testing Your Configuration
==========================

**1. Check config is valid**

.. code-block:: bash

    # Weights should sum to 1.0
    python3 -c "
    weights = [0.10, 0.60, 0.20, 0.10]
    print(f'Sum: {sum(weights)} (should be 1.0)')
    "

**2. Run with debug logging**

.. code-block:: bash

    export RAG_DEBUG=true
    export LOGLEVEL=DEBUG
    # Now importance calculations print detailed scores

**3. Test with a query**

.. code-block:: python

    from brain.prompt_builder import ContextRetriever
    from brain import config
    
    retriever = ContextRetriever()
    
    # Manually check importance
    test_turn = {
        'content': 'I learned Python',
        'timestamp': '2025-12-18T10:00:00Z',
        'metadata': {'prediction_error': 0.7}
    }
    
    importance = retriever.calculate_importance(test_turn, "What language do you use?")
    print(f"Importance: {importance}")
    print(f"Detail level: {retriever.get_detail_level(importance)}")

---

Common Configurations by Use Case
===================================

**Research Assistant** (maximize novelty/diversity)

.. code-block:: bash

    IMPORTANCE_WEIGHT_SURPRISE=0.70
    IMPORTANCE_WEIGHT_RELEVANCE=0.15
    GRADIENT_THRESHOLD_FULL=0.65
    MEMORY_DECAY_TIME_SCALE_HOURS=240

**Chat Buddy** (balance everything)

.. code-block:: bash

    IMPORTANCE_WEIGHT_DECAY=0.15
    IMPORTANCE_WEIGHT_SURPRISE=0.50
    IMPORTANCE_WEIGHT_RELEVANCE=0.25
    IMPORTANCE_WEIGHT_HABITUATION=0.10
    GRADIENT_THRESHOLD_CHUNKS=0.40

**Q&A System** (maximize relevance)

.. code-block:: bash

    IMPORTANCE_WEIGHT_RELEVANCE=0.70
    IMPORTANCE_WEIGHT_SURPRISE=0.10
    GRADIENT_THRESHOLD_FULL=0.80
    MEMORY_DECAY_TIME_SCALE_HOURS=50

**Fast Responder** (minimal context)

.. code-block:: bash

    GRADIENT_THRESHOLD_FULL=0.90
    GRADIENT_THRESHOLD_CHUNKS=0.70
    GRADIENT_THRESHOLD_SUMMARY=0.40
    MEMORY_DECAY_TIME_SCALE_HOURS=48

**Memory Machine** (retain everything)

.. code-block:: bash

    IMPORTANCE_WEIGHT_DECAY=0.05
    GRADIENT_THRESHOLD_SUMMARY=0.05
    MEMORY_DECAY_TIME_SCALE_HOURS=720
    CONTEXT_HABITUATION_THRESHOLD=10

---

Metrics to Watch
=================

**Enable token monitoring:**

.. code-block:: bash

    export TOKEN_MONITORING_ENABLED=true
    export LLM_MAX_CONTEXT=8000

**Check logs for:**

- "context selection accuracy: X%"
- "average importance score: Y"
- "token usage: Z of MAX"

---

When Something Feels Wrong
============================

**Ada seems to forget things**

→ Lower thresholds or increase decay time scale

.. code-block:: bash

    export GRADIENT_THRESHOLD_SUMMARY=0.10
    export MEMORY_DECAY_TIME_SCALE_HOURS=200

**Ada repeats the same context over and over**

→ Increase habituation penalty

.. code-block:: bash

    export CONTEXT_HABITUATION_THRESHOLD=2
    export CONTEXT_HABITUATION_WEIGHT=0.05

**Ada misses relevant context**

→ Increase relevance weight or lower its threshold

.. code-block:: bash

    export IMPORTANCE_WEIGHT_RELEVANCE=0.40
    export GRADIENT_THRESHOLD_CHUNKS=0.30

**Responses take too long / use too many tokens**

→ Tighten detail thresholds or reduce decay time

.. code-block:: bash

    export GRADIENT_THRESHOLD_FULL=0.85
    export MEMORY_DECAY_TIME_SCALE_HOURS=50

---

Documentation
===============

- **Full guide:** ``docs/contextual_malleability_guide.rst``
- **Research:** ``.ai/RESEARCH-FINDINGS-V2.2.md``
- **Code:** ``brain/prompt_builder/context_retriever.py``
- **Tests:** ``tests/test_context_retriever.py``

---

**Remember: All knobs are yours. Experiment. Share what works. Build weird things. 🚀**
