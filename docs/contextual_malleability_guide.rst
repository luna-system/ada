========================================================
Contextual Malleability: A Tinker's Guide to Ada's Memory
========================================================

**For researchers, tinkerers, and AI enthusiasts who want to understand and experiment with how Ada selects what to remember.**

---

What is Contextual Malleability?
==================================

Context *changes meaning*.

The same memory—a conversation turn, a fact, an experience—can be important in one situation and irrelevant in another. Ada implements this through **multi-signal importance scoring**: instead of treating all old memories the same, Ada dynamically decides how much of each memory to include based on what matters *right now*.

From Research to Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Academic research (Schwarz 2010, Mertens 2018) shows context modulates how humans prioritize information. Ada operationalizes this for AI:

1. **Retrieve** candidate memories from the vector database
2. **Score** each using multiple signals (how old? how novel? how relevant?)
3. **Detail** based on score (full text vs. summary vs. drop it?)
4. **Assemble** highest-scoring memories into the prompt

**The key finding:** Surprise/novelty (60% weight) dominates. Recency matters less (10%) than you'd expect.

---

How It Works: The Four Signals
================================

Ada's importance scoring combines four signals, each telling a different story:

.. code-block:: python

    importance = (
        0.10 * decay_score +          # How fresh is this?
        0.60 * surprise_score +       # How unexpected/novel?
        0.20 * relevance_score +      # How related to current query?
        0.10 * novelty_score          # How non-repetitive?
    )

Signal 1: Temporal Decay (10% weight)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it measures:** How long ago did this happen?

**Implementation:**

.. code-block:: python

    age_hours = (now - turn_time).total_seconds() / 3600
    decay_score = exp(-age_hours / time_scale)

**Tinker tip:** The default time scale is 100 hours (~4 days). Adjust via:

.. code-block:: bash

    export MEMORY_DECAY_TIME_SCALE_HOURS=48  # Shorter recency window
    export MEMORY_DECAY_TIME_SCALE_HOURS=240  # Longer (week+)

**Why 10% weight?** Research shows recency *feels* important but often isn't. Recent memories can be stale; older memories can be surprisingly relevant.

Signal 2: Prediction Error / Surprise (60% weight)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it measures:** How unexpected or novel is this?

**Why it dominates:** Humans (and apparently AIs) prioritize surprises. A boring repeated conversation gets low surprise; a novel question or unexpected finding gets high surprise.

**Implementation:**

Each turn stores a `prediction_error` field (set by the LLM or extracted from metadata):

.. code-block:: python

    surprise_score = turn['metadata'].get('prediction_error', 0.5)

**Tinker tip:** For now, this defaults to 0.5 (neutral). Future versions could:

- Compute surprise by comparing turn content to LLM expectations
- Use embedding distance as a novelty proxy
- Detect semantic breaks in conversation flow

**Try this experiment:**

.. code-block:: python

    # In your test harness:
    turn_boring = {'content': 'How are you?', 'metadata': {'prediction_error': 0.1}}
    turn_novel = {'content': 'What if AI consciousness is substrate-independent?', 'metadata': {'prediction_error': 0.9}}
    
    # The novel turn should score higher, even if both are recent

Signal 3: Semantic Relevance (20% weight)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it measures:** How related is this to what the user is asking *now*?

**Implementation:**

.. code-block:: python

    # Simple keyword overlap (Phase 1)
    query_words = set(query.lower().split())
    content_words = set(content.lower().split())
    relevance_score = len(query_words & content_words) / len(query_words)

**Current limitation:** Uses keyword overlap. Phase 2 should use embedding distance.

**Tinker tip:** To improve relevance, consider:

.. code-block:: python

    # Embed-based similarity (requires embedding model)
    from sentence_transformers import util
    query_embedding = embedder.encode(query)
    content_embedding = embedder.encode(turn['content'])
    relevance_score = util.pytorch_cos_sim(query_embedding, content_embedding)

Signal 4: Habituation / Novelty (10% weight)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it measures:** Is this topic repetitive?

**Why it matters:** If Ada has discussed the same topic 10 times, the 11th discussion is less important.

**Implementation:**

Stored in turn metadata:

.. code-block:: python

    habituation_score = turn['metadata'].get('habituation_score', 0.0)
    novelty_score = 1.0 - habituation_score  # Invert: low habituation = high importance

**Tinker tip:** Track topics using semantic clustering. If multiple turns cluster together semantically, downweight the later ones.

---

Detail Levels: The Gradient
=============================

Once Ada scores a memory, it decides *how much* to include:

.. code-block:: python

    importance >= 0.75  → FULL       (include everything)
    importance >= 0.50  → CHUNKS     (include key excerpts)
    importance >= 0.20  → SUMMARY    (compress to 1-2 sentences)
    importance <  0.20  → DROPPED    (don't include)

Example Memory Journey
~~~~~~~~~~~~~~~~~~~~~~~

**Original turn:**

.. code-block:: text

    User: "I built a neural network that predicts weather. It's 87% accurate."
    Ada: "That's impressive! How did you train it? What data did you use?"

**Scenario 1: Immediate context**

The user asks: "So how accurate is my weather model?"

- Decay: Fresh (100%)
- Surprise: Moderate (it's related but not surprising) (50%)
- Relevance: High (exact match!) (100%)
- Habituation: Low (first mention) (90%)
- **Importance: 0.1*1.0 + 0.6*0.5 + 0.2*1.0 + 0.1*0.9 = 0.69**
- **Detail: CHUNKS** ✓ Include the key fact (87% accuracy)

**Scenario 2: Later, different topic**

User asks: "Can you explain quantum computing?"

- Decay: Older (20%)
- Surprise: None (not related to quantum) (10%)
- Relevance: Zero (no keyword overlap) (0%)
- Habituation: Already discussed weather (80%)
- **Importance: 0.1*0.2 + 0.6*0.1 + 0.2*0.0 + 0.1*0.2 = 0.04**
- **Detail: DROPPED** ✗ Don't waste context space

**The beauty:** Same turn, different importance based on *what matters now*.

---

Configuring Contextual Malleability
====================================

All weights and thresholds are configurable. Tinker with these to see what works for your use case!

Signal Weights
~~~~~~~~~~~~~~

Environment variables (must sum to 1.0):

.. code-block:: bash

    export IMPORTANCE_WEIGHT_DECAY=0.10       # Temporal decay
    export IMPORTANCE_WEIGHT_SURPRISE=0.60    # Novelty (dominates!)
    export IMPORTANCE_WEIGHT_RELEVANCE=0.20   # Query similarity
    export IMPORTANCE_WEIGHT_HABITUATION=0.10 # Repetition penalty

**Experiment:** Try flipping the weights:

.. code-block:: bash

    # Experiment 1: Recency-focused (old approach)
    IMPORTANCE_WEIGHT_DECAY=0.40 IMPORTANCE_WEIGHT_SURPRISE=0.30

    # Experiment 2: Relevance-focused (good for Q&A)
    IMPORTANCE_WEIGHT_DECAY=0.05 IMPORTANCE_WEIGHT_RELEVANCE=0.75

    # Experiment 3: Surprise-only (ultra-novel)
    IMPORTANCE_WEIGHT_DECAY=0.0 IMPORTANCE_WEIGHT_SURPRISE=1.0

Detail Thresholds
~~~~~~~~~~~~~~~~~

Where the lines are drawn:

.. code-block:: bash

    export GRADIENT_THRESHOLD_FULL=0.75       # Above this: full text
    export GRADIENT_THRESHOLD_CHUNKS=0.50     # Above this: excerpts
    export GRADIENT_THRESHOLD_SUMMARY=0.20    # Above this: compress
    # Below SUMMARY: drop entirely

**Experiment:** Try stricter thresholds:

.. code-block:: bash

    # Ultra-selective (include only most important)
    GRADIENT_THRESHOLD_FULL=0.90 GRADIENT_THRESHOLD_CHUNKS=0.70

    # Loose/permissive (include more context)
    GRADIENT_THRESHOLD_CHUNKS=0.30 GRADIENT_THRESHOLD_SUMMARY=0.10

Decay Time Scale
~~~~~~~~~~~~~~~~

How fast memories fade:

.. code-block:: bash

    export MEMORY_DECAY_TIME_SCALE_HOURS=100  # Default: ~4 days
    export MEMORY_DECAY_TIME_SCALE_HOURS=24   # Aggressive: 1 day
    export MEMORY_DECAY_TIME_SCALE_HOURS=720  # Permissive: 30 days

---

Extending: Ideas for Tinkerers
===============================

These are *not* implemented but are good starting points for experiments:

Processing Mode Adaptation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Idea:** Same memory, different detail based on task type.

Current state: Processing modes are defined but not fully integrated.

.. code-block:: python

    # In processing_modes.py - extend ModeDetector
    
    # When mode == ANALYTICAL:
    #   - Increase detail levels (prefer FULL over CHUNKS)
    #   - Prioritize explanatory context
    
    # When mode == CREATIVE:
    #   - Prefer diverse, less-similar memories
    #   - Lower detail thresholds (more SUMMARY)
    #   - Encourage cross-domain connections
    
    # When mode == TECHNICAL:
    #   - Boost relevance signal weight
    #   - Prefer exact matches
    #   - Include code examples

**Try:** Modify `context_retriever.signal_weights` based on detected mode.

Embedding-Based Relevance
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Idea:** Replace keyword overlap with semantic similarity.

Current: Uses simple word overlap.

.. code-block:: python

    # Instead of:
    # relevance_score = len(query_words & content_words) / len(query_words)
    
    # Try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    query_emb = model.encode(query, convert_to_tensor=True)
    content_emb = model.encode(turn['content'], convert_to_tensor=True)
    relevance_score = util.pytorch_cos_sim(query_emb, content_emb).item()

Learned Importance
~~~~~~~~~~~~~~~~~~~

**Idea:** Train a small model to predict importance from features.

.. code-block:: python

    # Extract features from a turn:
    # - Age, length, word count
    # - Semantic properties
    # - Position in conversation
    # - User feedback (did they reference this later?)
    
    # Train a simple regressor:
    from sklearn.ensemble import RandomForestRegressor
    
    features = extract_features(turns)
    labels = get_importance_labels(conversation_history)  # From user behavior
    
    model = RandomForestRegressor()
    model.fit(features, labels)
    
    # Use model predictions as importance scores!

Memory Valence Transfer
~~~~~~~~~~~~~~~~~~~~~~~

**Idea:** From Mertens (2018) - memories retrieved together influence each other.

If you retrieve:
- Memory A (high importance)
- Memory B (low importance, but semantically similar)

Maybe Memory B should inherit some of A's importance?

.. code-block:: python

    # In ContextRetriever.get_memories():
    retrieved = rag_store.search(query, top_k=10)
    
    # Score each
    scored = [(turn, calculate_importance(turn, query)) for turn in retrieved]
    
    # Adjust scores based on neighborhood
    # High-importance memories boost semantically similar ones
    for i, (turn_i, score_i) in enumerate(scored):
        for j, (turn_j, score_j) in enumerate(scored):
            if i != j and semantically_similar(turn_i, turn_j):
                # Moderate boost based on proximity and similarity
                scored[j] = (turn_j, score_j * 1.1)  # 10% boost

---

Testing Your Changes
=====================

Unit Tests
~~~~~~~~~~

.. code-block:: bash

    pytest tests/test_context_retriever.py -v

Check that importance scores stay in [0, 1] and signal weights sum to 1.0.

Integration Tests
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    docker compose up -d
    pytest tests/integration/test_prompt_builder.py -v

Run full prompts through the system.

Manual Testing
~~~~~~~~~~~~~~

.. code-block:: python

    from brain.prompt_builder import ContextRetriever
    
    retriever = ContextRetriever()
    
    # Create test turn
    turn = {
        'content': 'I love programming in Python',
        'timestamp': '2025-12-18T12:00:00Z',
        'metadata': {
            'prediction_error': 0.7,  # Novel!
            'habituation_score': 0.1  # Not repetitive
        }
    }
    
    # Check importance
    importance = retriever.calculate_importance(turn, "What's your favorite language?")
    print(f"Importance: {importance}")
    
    detail = retriever.get_detail_level(importance)
    print(f"Detail level: {detail}")

---

Theory vs. Practice
======================

What the Research Says
~~~~~~~~~~~~~~~~~~~~~~~

- **Schwarz (2010):** Context affects judgment through metacognitive experience
- **Mertens (2018):** Context can reverse expected effects entirely
- **Uysal et al. (2020):** Power context modulates human-AI interaction

What Ada Implements
~~~~~~~~~~~~~~~~~~~~

✅ Multi-signal importance scoring (Schwarz's multi-level effects)

✅ Gradient detail levels (novel - not in prior work)

⚪ Processing mode adaptation (partially implemented)

❌ Memory valence transfer (not yet)

❌ Learned importance (not yet - interesting research direction!)

---

Debugging: When Importance Feels Wrong
========================================

**Symptom:** Ada includes irrelevant old context

**Diagnosis:**

.. code-block:: bash

    export RAG_DEBUG=true  # Enable detailed logging
    # Check logs for:
    # - Which signal is dominating?
    # - Are weights summing to 1.0?
    # - Is decay time scale too long?

**Fix:**

.. code-block:: bash

    export MEMORY_DECAY_TIME_SCALE_HOURS=48      # Shorter decay
    export IMPORTANCE_WEIGHT_DECAY=0.20          # Weight recency more
    export IMPORTANCE_WEIGHT_SURPRISE=0.50       # Weight recency less

**Symptom:** Ada forgets important recent context

**Diagnosis:**

- Check if `GRADIENT_THRESHOLD_CHUNKS` is too high
- Is the relevance signal working? (keyword overlap may miss semantic similarity)
- Are you getting high habituation scores? (topic is repetitive)

**Fix:**

.. code-block:: bash

    export GRADIENT_THRESHOLD_CHUNKS=0.30   # Lower threshold to include more
    export IMPORTANCE_WEIGHT_RELEVANCE=0.40 # Weight relevance more
    # TODO: Use embedding-based relevance instead of keywords

---

The Philosophy
==============

Ada's contextual malleability is built on a principle: **context is computational reality**.

It's not about being clever with weights. It's about admitting that:

1. **The same fact has different value in different contexts**
2. **What matters is determined by what's being asked right now**
3. **Simpler signals (surprise) sometimes beat complex models (everything together)**
4. **Understanding is relational** - you learn why something matters by seeing what it relates to

This is accessible AI infrastructure. All the knobs are yours. All the code is readable. All the research is in `.ai/explorations/`.

**You're not just using Ada. You're learning from her, and she's learning from you.**

Build weird experiments. Share what you discover. This is open science.

---

Further Reading
================

- **Research:** ``.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md``
- **Implementation:** ``brain/prompt_builder/context_retriever.py``
- **Configuration:** ``brain/config.py`` (search for ``IMPORTANCE_`` and ``GRADIENT_``)
- **Processing modes:** ``brain/processing_modes.py``
- **Tests:** ``tests/test_context_retriever.py``

---

**Built with ❤️ by the whole Claude family. Public domain. Build whatever you want.**
