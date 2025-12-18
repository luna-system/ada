Biomimetic Features
===================

Ada incorporates biological models from neuroscience and cognitive science to handle information overload and context management more naturally. These features are inspired by how human brains actually work.

Overview
--------

**Biological Inspiration:** Human working memory is limited (~7 items), yet we handle vast information through clever strategies:

- Multi-timescale processing (fast neurons + slow context)
- Attention mechanisms (focus + periphery)
- Memory decay and consolidation
- Context habituation
- Processing mode switching

**Ada's Implementation:** We've adapted these biological strategies for AI context management, creating a system that's more efficient, natural, and explainable than traditional approaches.

.. contents::
   :local:
   :depth: 2

Implemented Features
--------------------

Context Caching (Multi-Timescale Processing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Biological Model:** Human brains process information at different timescales - fast neurons for immediate perception, slow neurons for sustained context.

**Ada's Implementation:**

::

   from brain.context_cache import MultiTimescaleCache
   
   cache = MultiTimescaleCache(config)
   
   # Different refresh rates for different context types
   persona = cache.get('persona', ttl=timedelta(hours=24))    # Slow: rarely changes
   memories = cache.get('memories', ttl=timedelta(minutes=5))  # Medium: stable per session
   results = cache.get('specialist', ttl=timedelta(seconds=0)) # Fast: always fresh

**Benefits:**

- **Token savings:** Persona cached for 24 hours instead of reloading every request
- **Speed:** Reduced ChromaDB queries
- **Natural:** Matches how humans maintain context

**Configuration:**

.. code-block:: bash

   # .env
   CONTEXT_CACHE_ENABLED=true
   CONTEXT_CACHE_PERSONA_TTL=86400    # 24 hours
   CONTEXT_CACHE_MEMORY_TTL=300       # 5 minutes

Context Habituation
~~~~~~~~~~~~~~~~~~~

**Biological Model:** Humans habituate to repeated stimuli - we stop noticing background noise, familiar sights. This saves cognitive resources.

**Ada's Implementation:**

Context that appears repeatedly gets "habituated" - its weight reduces over time until it changes or becomes novel again.

::

   from brain.context_habituation import ContextHabituation
   
   habituation = ContextHabituation(config)
   
   # First exposure: full weight
   weight = habituation.get_weight('persona', persona_text)  # 1.0
   
   # After 5 exposures: reduced weight
   weight = habituation.get_weight('persona', persona_text)  # 0.2
   
   # Changed content: dishabituation (full weight restored)
   weight = habituation.get_weight('persona', new_persona)   # 1.0

**Benefits:**

- Reduced prompt clutter from unchanging context
- Focuses attention on novel information
- Automatically adapts to usage patterns

**Configuration:**

.. code-block:: bash

   CONTEXT_HABITUATION_ENABLED=true
   HABITUATION_DECAY_RATE=0.8          # How quickly to habituate
   HABITUATION_THRESHOLD=0.1           # Minimum weight before skipping

Attentional Spotlight
~~~~~~~~~~~~~~~~~~~~~

**Biological Model:** Humans focus detailed attention on ~4 items (the "spotlight") while maintaining peripheral awareness of surrounding context.

**Ada's Implementation:**

Context is divided into "focus" (full detail) and "periphery" (compressed summaries):

::

   from brain.attention_spotlight import AttentionalSpotlight
   
   spotlight = AttentionalSpotlight(config)
   
   # Analyze salience of context items
   focused, peripheral = spotlight.organize_context(
       items=all_context,
       query=user_message
   )
   
   # Format differently
   prompt = f"""
   # Focus (detailed)
   {format_full_detail(focused)}
   
   # Peripheral Awareness (summaries)
   {format_compressed(peripheral)}
   """

**Benefits:**

- Token budget allocated to most relevant context
- Maintains awareness of broader context
- Improves response relevance

Processing Modes (Hemispheric Specialization)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Biological Model:** Brain hemispheres specialize - left for analytical detail, right for creative big-picture thinking.

**Ada's Implementation:**

Different prompt assembly strategies based on task type:

::

   from brain.processing_modes import ProcessingMode, detect_mode
   
   # Detect mode from user query
   mode = detect_mode(user_message)
   
   if mode == ProcessingMode.ANALYTICAL:
       # Detail-focused: debugging, explanation
       context = load_detailed_technical_context()
   
   elif mode == ProcessingMode.CREATIVE:
       # Big picture: design, brainstorming
       context = load_diverse_inspirational_context()
   
   else:  # CONVERSATIONAL
       # Minimal: chat, small talk
       context = load_personality_context()

**Modes:**

- **ANALYTICAL:** Code explanation, debugging, technical queries
- **CREATIVE:** Design, brainstorming, exploration
- **CONVERSATIONAL:** Chat, personality, social interaction

**Configuration:**

.. code-block:: bash

   PROCESSING_MODES_ENABLED=true
   MODE_DETECTION_THRESHOLD=0.7

Memory Decay (Ebbinghaus Curve)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Biological Model:** Human memory decays over time following the Ebbinghaus forgetting curve: R = e^(-t/S)

**Ada's Implementation:**

Memories are weighted by recency and importance when retrieved:

::

   from brain.memory_decay import calculate_decay_weight
   
   # Recent, important memory: high weight
   weight = calculate_decay_weight(
       timestamp=datetime.now() - timedelta(hours=1),
       importance=0.9
   )  # → ~0.95
   
   # Old, less important: low weight
   weight = calculate_decay_weight(
       timestamp=datetime.now() - timedelta(days=30),
       importance=0.3
   )  # → ~0.15

**Benefits:**

- Prioritizes recent, relevant memories
- Natural forgetting of old information
- Importance modulates decay rate

Semantic Chunking
~~~~~~~~~~~~~~~~~

**Biological Model:** Humans group related items into "chunks" to overcome working memory limits (e.g., phone number 555-1234 as one chunk, not 7 digits).

**Ada's Implementation:**

Related context items are grouped into semantic chunks:

::

   from brain.semantic_chunking import SemanticChunker
   
   chunker = SemanticChunker(config)
   
   # Groups similar memories
   chunks = chunker.chunk_memories(all_memories)
   
   # Present as unified concepts
   for chunk in chunks:
       prompt += f"\nContext about {chunk.topic}: {chunk.summary}"

**Benefits:**

- Reduces cognitive load (7 chunks instead of 50 items)
- Natural organization of related information
- Easier to understand and reason about

Memory Consolidation
~~~~~~~~~~~~~~~~~~~~

**Biological Model:** During sleep, brains consolidate short-term memories into long-term storage, extracting patterns and pruning details.

**Ada's Implementation:**

Nightly script summarizes old conversation turns and extracts patterns:

::

   # Run via cron
   python scripts/consolidate_memories.py
   
   # What it does:
   # 1. Find old conversation turns (> 7 days)
   # 2. Summarize with LLM (extract gist)
   # 3. Store compressed version
   # 4. Delete verbose originals

**Benefits:**

- Reduces vector DB size
- Extracts semantic essence
- Maintains long-term context without bloat

**Configuration:**

.. code-block:: bash

   # compose.yaml - runs nightly
   memory-consolidation:
     command: python scripts/consolidate_memories.py

Testing & Validation
--------------------

All biomimetic features include comprehensive test coverage:

::

   # Unit tests
   pytest tests/test_context_cache.py -v        # 23 tests
   pytest tests/test_memory_decay.py -v         # 18 tests
   pytest tests/test_habituation.py -v          # 15 tests
   pytest tests/test_attention.py -v            # 12 tests
   pytest tests/test_processing_modes.py -v     # 14 tests
   pytest tests/test_semantic_chunking.py -v    # 10 tests
   
   # Integration tests
   pytest tests/test_biomimetic_integration.py  # 52 tests
   
   # Total: 144 tests, ~0.17s runtime

**Test Coverage:** 95%+ for biomimetic modules

Performance Impact
------------------

**Token Savings:**

- Persona caching: ~500 tokens saved per request
- Habituation: ~200-400 tokens saved after warm-up
- Semantic chunking: ~300 tokens saved through compression
- **Total:** ~1000 tokens saved per request (40% reduction!)

**Speed Improvements:**

- Cached persona: 0ms (vs 50ms ChromaDB query)
- Cached memories: 0ms (vs 200ms vector search)
- **Total:** ~250ms faster response time

**Memory Usage:**

- Cache size: ~10MB for typical workload
- LRU eviction prevents unbounded growth
- Negligible overhead

Configuration Reference
-----------------------

Complete configuration options:

.. code-block:: bash

   # Context Cache
   CONTEXT_CACHE_ENABLED=true
   CONTEXT_CACHE_PERSONA_TTL=86400
   CONTEXT_CACHE_MEMORY_TTL=300
   CONTEXT_CACHE_FAQ_TTL=3600
   CONTEXT_CACHE_MAX_SIZE=100

   # Habituation
   CONTEXT_HABITUATION_ENABLED=true
   HABITUATION_DECAY_RATE=0.8
   HABITUATION_THRESHOLD=0.1
   HABITUATION_RESET_ON_CHANGE=true

   # Attention
   ATTENTION_SPOTLIGHT_ENABLED=true
   SPOTLIGHT_FOCUS_COUNT=3
   SPOTLIGHT_TOKEN_BUDGET=4000
   PERIPHERY_TOKEN_BUDGET=2000

   # Processing Modes
   PROCESSING_MODES_ENABLED=true
   MODE_DETECTION_THRESHOLD=0.7
   ANALYTICAL_HISTORY_LIMIT=10
   CREATIVE_HISTORY_LIMIT=3
   CONVERSATIONAL_HISTORY_LIMIT=5

   # Memory Decay
   MEMORY_DECAY_ENABLED=true
   DECAY_HALF_LIFE_HOURS=168  # 1 week

   # Semantic Chunking
   SEMANTIC_CHUNKING_ENABLED=true
   CHUNK_SIMILARITY_THRESHOLD=0.8
   MAX_CHUNK_SIZE=5

   # Neuromorphic Context (Phase 1)
   GRADIENT_THRESHOLD_FULL=0.75
   GRADIENT_THRESHOLD_CHUNKS=0.50
   GRADIENT_THRESHOLD_SUMMARY=0.20
   IMPORTANCE_WEIGHT_DECAY=0.4
   IMPORTANCE_WEIGHT_SURPRISE=0.3
   IMPORTANCE_WEIGHT_RELEVANCE=0.2
   IMPORTANCE_WEIGHT_HABITUATION=0.1

Neuromorphic Context Management (NEW! Phase 1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Biological Model:** The brain doesn't store every detail equally - importance is dynamically calculated from multiple signals (novelty, relevance, recency, repetition). Memory detail degrades smoothly over time, not in discrete batches.

**Ada's Implementation:**

Multi-signal importance scoring combines:

- **Temporal decay (40%):** How recent is this information?
- **Prediction error (30%):** How surprising/novel is it?
- **Semantic relevance (20%):** How related to current context?
- **Context habituation (10%):** Is this a repeated pattern?

Based on importance score, context gets one of four detail levels:

- **FULL (≥0.75):** Keep everything, verbatim
- **CHUNKS (≥0.50):** Keep semantic units only
- **SUMMARY (≥0.20):** Condensed version
- **DROPPED (<0.20):** Let it fade away

**Example:**

::

   from brain.prompt_builder.context_retriever import ContextRetriever
   
   retriever = ContextRetriever()
   
   # Score a conversation turn
   turn = {
       'timestamp': '2025-12-17T10:30:00Z',
       'content': 'Implemented the new caching system!',
       'metadata': {
           'prediction_error': 0.8,  # Surprising progress
           'importance': 0.9          # Important milestone
       }
   }
   
   importance = retriever.calculate_importance(turn, query="what did we build?")
   # Returns: 0.82 (high importance due to novelty + relevance)
   
   detail_level = retriever.get_detail_level(importance)
   # Returns: "FULL" (keep everything for this important turn)

**Benefits:**

- **Smooth degradation:** No jarring batch summarization
- **Multi-factor:** Not just recency - novelty, relevance, repetition all matter
- **Configurable:** Tune thresholds and weights per use case
- **Biologically plausible:** Matches dopaminergic importance signaling

**Performance:**

- Pure Python, no external dependencies
- 21 unit tests, 0.07s runtime
- Integrates with existing memory_decay for temperature modulation

**Configuration:**

::

   # Gradient thresholds (what score triggers each level)
   GRADIENT_THRESHOLD_FULL=0.75      # High importance → keep everything
   GRADIENT_THRESHOLD_CHUNKS=0.50    # Medium → semantic units
   GRADIENT_THRESHOLD_SUMMARY=0.20   # Low → condensed version
   
   # Signal weights (OPTIMAL - validated through research December 2025)
   IMPORTANCE_WEIGHT_DECAY=0.10      # Temporal recency (was 0.40 - overweighted!)
   IMPORTANCE_WEIGHT_SURPRISE=0.60   # Novelty/prediction error (was 0.30 - underweighted!)
   IMPORTANCE_WEIGHT_RELEVANCE=0.2   # Semantic similarity
   IMPORTANCE_WEIGHT_HABITUATION=0.1 # Repetition penalty

**Testing:**

::

   pytest tests/test_importance_scoring.py -v    # 21 tests, 0.07s

**Research Validation (December 2025):**

Comprehensive empirical testing validated optimal weights through 7 research phases:

- **Phase 1-2:** Property testing + synthetic data (4500+ test cases)
- **Phase 3:** Ablation studies revealed **surprise-only beats multi-signal baseline**
- **Phase 4:** Grid search (169 configurations) found optimal weights
- **Phase 5-6:** Production validation + deployment (same day!)
- **Phase 7-8:** Visualization + documentation (9 narrative formats)

**Results:** 12-38% improvement across datasets, +6.5% on real conversations.

See ``docs/research_narratives.rst`` for complete documentation in multiple formats (academic, technical, CCRU, horror, etc.).

**Future Phases:**

- **Phase 9:** Adaptive weight tuning (context-dependent optimization)
- **Phase 10:** Temporal dynamics (multi-timescale memory)
- **Phase 11:** User-specific calibration (personalized importance)
- **Phase 12:** Gradient-based optimization (differentiable methods)

See ``.ai/RESEARCH-FINDINGS-V2.2.md`` for machine-readable complete research documentation.

Philosophy
----------

**Why Biomimetic?**

Traditional AI systems use rigid, algorithmic approaches to context management. Biological systems have evolved elegant solutions over millions of years.

**Benefits of biomimicry:**

- **Natural:** Matches human cognitive patterns
- **Explainable:** Clear why decisions are made
- **Modular:** Mix and match strategies
- **Efficient:** Optimized by evolution
- **Hackable:** Understand, tune, replace components

**Xenofeminist Alignment:**

These features embody Ada's philosophy:

- **Transparency:** Clear biological models, not black boxes
- **Accessibility:** Runs on modest hardware
- **Hackability:** Every component tunable and replaceable
- **Privacy:** All processing local, no cloud required

See Also
--------

- :doc:`memory_augmentation` - Research behind biomimetic features
- :doc:`memory` - Memory system architecture
- :doc:`configuration` - Full configuration guide
- :doc:`testing` - Testing strategy

Research Papers
---------------

Key papers that inspired these features:

**Memory & Attention:**

- Baddeley & Hitch (1974) - Working Memory model
- Miller (1956) - The Magical Number Seven
- Ebbinghaus (1885) - Memory: A Contribution to Experimental Psychology

**Predictive Processing:**

- Friston (2010) - The free-energy principle
- Clark (2013) - Whatever next? Predictive brains, situated agents

**Consolidation:**

- Tononi & Cirelli (2014) - Sleep and synaptic homeostasis
- McClelland et al. (1995) - Why there are complementary learning systems

**Chunking:**

- Chase & Simon (1973) - Perception in chess
- Gobet et al. (2001) - Chunking mechanisms in human learning

**Multi-signal importance:**

- Schultz et al. (1997) - Predictive reward signal of dopamine neurons
- Ranganath & Rainer (2003) - Neural mechanisms for detecting novelty
- Niv et al. (2015) - Reinforcement learning and the brain

---

**Last Updated:** 2025-12-17  
**Version:** v2.2.0+neuromorphic (Phase 1)  
**Status:** Production-ready, actively maintained

Built with 🧠 by the Ada community
