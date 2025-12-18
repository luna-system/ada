============================================================
Extending Ada: Adding New Signals to Contextual Malleability
============================================================

**For researchers and developers who want to add new importance factors**

---

What Are Signals?
=================

Ada's importance scoring combines 4 signals:

.. code-block:: text

    importance = decay * w1 + surprise * w2 + relevance * w3 + habituation * w4

Where:

- **decay** = How recently was this memory accessed? (time-based)
- **surprise** = How unexpected or novel is this? (semantic)
- **relevance** = How similar to the current query? (embedding-based)
- **habituation** = How often has this been discussed? (frequency-based)

Each signal returns a **score from 0.0 to 1.0**, then weights combine them into final importance.

---

Anatomy of a Signal
====================

**Each signal needs:**

1. A **scorer function** - takes memory, context, returns float [0-1]
2. A **weight** - what fraction of final score is this signal
3. **Configuration** - environment variables for tuning
4. **Documentation** - explain what it measures and why
5. **Tests** - verify it works at boundaries

**Example: The Decay Signal (Already Implemented)**

.. code-block:: python

    # brain/memory_decay.py
    class MemoryDecayWeighter:
        """Scores memory by age using exponential decay."""
        
        def __init__(self, time_scale_hours: float = 100.0):
            self.time_scale_hours = time_scale_hours
            self.logger = logging.getLogger(__name__)
            
        def weight_by_decay(self, 
                          memory_timestamp: str,
                          base_importance: float = 1.0) -> float:
            """Score memory by recency using exponential decay.
            
            Args:
                memory_timestamp: ISO format timestamp of memory
                base_importance: Starting score (usually 1.0)
                
            Returns:
                Importance score [0.0, 1.0] based on age
                
            Formula:
                importance = base * exp(-age_hours / time_scale)
                
            Example:
                At time_scale=100 hours:
                - Fresh memory (0 hours old): 1.0
                - After 100 hours: 0.368 (1/e)
                - After 200 hours: 0.135 (1/e²)
            """
            try:
                memory_dt = datetime.fromisoformat(memory_timestamp.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                age_hours = (now - memory_dt).total_seconds() / 3600.0
                
                # Clamp to reasonable range
                age_hours = max(0, min(age_hours, 10000))  # Max ~1 year
                
                # Exponential decay
                decay_factor = math.exp(-age_hours / self.time_scale_hours)
                return base_importance * decay_factor
                
            except Exception as e:
                self.logger.error(f"Decay calculation error: {e}")
                return 1.0  # On error, assume important

    # In brain/config.py
    MEMORY_DECAY_TIME_SCALE_HOURS = float(os.getenv("MEMORY_DECAY_TIME_SCALE_HOURS", "100.0"))
    
    # In brain/prompt_builder/context_retriever.py
    self.signal_weights = {
        'decay': getattr(self.config, 'IMPORTANCE_WEIGHT_DECAY', 0.10),
        # ... other signals
    }

---

Custom Signal Walkthrough: Adding Valence (Emotional Weight)
==============================================================

Let's add a new signal: **valence** - how emotionally important was a memory?

**Step 1: Create the Signal Module**

.. code-block:: python

    # brain/memory_valence.py
    """Score memories by emotional valence (pos/neg/neutral)."""
    
    import logging
    from typing import Optional
    
    class MemoryValenceWeighter:
        """Score memory importance based on emotional content."""
        
        # Emotion keywords (this is simplified; use NLP in production)
        POSITIVE_KEYWORDS = {
            'happy', 'love', 'excited', 'grateful', 'great',
            'amazing', 'wonderful', 'proud', 'wonderful', 'brilliant'
        }
        NEGATIVE_KEYWORDS = {
            'sad', 'angry', 'frustrated', 'disappointed', 'terrible',
            'awful', 'hate', 'failed', 'lost', 'scared'
        }
        
        def __init__(self, valence_weight_positive: float = 0.3,
                     valence_weight_negative: float = 0.2):
            """Initialize valence weighter.
            
            Args:
                valence_weight_positive: How much positive emotions matter [0-1]
                valence_weight_negative: How much negative emotions matter [0-1]
                
            Note: Negative weight lower by default (surprises matter more 
                  than just negative emotions)
            """
            self.weight_positive = valence_weight_positive
            self.weight_negative = valence_weight_negative
            self.logger = logging.getLogger(__name__)
            
        def score_valence(self, memory_text: str) -> float:
            """Score memory by emotional content.
            
            Returns:
                float [0.0, 1.0] indicating emotional importance
                
            Formula:
                If positive keywords found:
                    score = 0.5 + (positive_density * weight_positive * 0.5)
                If negative keywords found:
                    score = 0.3 + (negative_density * weight_negative * 0.3)
                Else:
                    score = 0.5  (neutral - baseline)
            """
            if not memory_text:
                return 0.5  # Neutral default
                
            text_lower = memory_text.lower()
            words = set(text_lower.split())
            
            # Count emotional keywords
            positive_count = len(words & self.POSITIVE_KEYWORDS)
            negative_count = len(words & self.NEGATIVE_KEYWORDS)
            total_words = len(words)
            
            if total_words == 0:
                return 0.5
                
            # Calculate densities
            positive_density = positive_count / total_words
            negative_density = negative_count / total_words
            
            # Score: positive memories worth 0.5-1.0, negative 0.3-0.6, neutral 0.5
            if positive_count > 0:
                score = 0.5 + (positive_density * self.weight_positive * 0.5)
            elif negative_count > 0:
                score = 0.3 + (negative_density * self.weight_negative * 0.3)
            else:
                score = 0.5  # Neutral baseline
                
            # Clamp to [0, 1]
            return max(0.0, min(1.0, score))

**Step 2: Add Configuration**

.. code-block:: python

    # Add to brain/config.py

    # Memory Valence Scoring (Emotional Weight)
    # See docs/contextual_malleability_guide.rst "Valence Signal" section
    # 
    # Valence measures emotional importance:
    # - Positive emotions (joy, excitement, pride) → higher importance
    # - Negative emotions (anger, grief, fear) → medium importance
    # - Neutral information → baseline importance
    #
    # Research: Schwarz (2010) - disfluency (emotional arousal) triggers analysis
    # 
    # Use cases:
    # - Therapy/counseling: Keep emotionally significant memories (increase POSITIVE)
    # - FAQ system: Ignore emotional tone (decrease both POSITIVE and NEGATIVE)
    # - Discovery: Prioritize unusual (which are often emotionally charged)
    #
    # TRY: Start with [positive=0.15, negative=0.05] for balanced emotion awareness
    MEMORY_VALENCE_WEIGHT_POSITIVE = float(os.getenv("MEMORY_VALENCE_WEIGHT_POSITIVE", "0.15"))
    MEMORY_VALENCE_WEIGHT_NEGATIVE = float(os.getenv("MEMORY_VALENCE_WEIGHT_NEGATIVE", "0.05"))

**Step 3: Integrate with Context Retriever**

.. code-block:: python

    # Modify brain/prompt_builder/context_retriever.py
    
    from brain.memory_valence import MemoryValenceWeighter  # Add import
    
    class ContextRetriever:
        def __init__(self, rag_store, config, cache=None):
            # ... existing code ...
            
            # Initialize valence weighter
            self.valence_weighter = MemoryValenceWeighter(
                valence_weight_positive=self.config.MEMORY_VALENCE_WEIGHT_POSITIVE,
                valence_weight_negative=self.config.MEMORY_VALENCE_WEIGHT_NEGATIVE
            )
            
            # Add to signal weights (now 5 signals instead of 4)
            self.signal_weights = {
                'decay': getattr(self.config, 'IMPORTANCE_WEIGHT_DECAY', 0.10),
                'surprise': getattr(self.config, 'IMPORTANCE_WEIGHT_SURPRISE', 0.60),
                'relevance': getattr(self.config, 'IMPORTANCE_WEIGHT_RELEVANCE', 0.20),
                'habituation': getattr(self.config, 'IMPORTANCE_WEIGHT_HABITUATION', 0.10),
                'valence': getattr(self.config, 'IMPORTANCE_WEIGHT_VALENCE', 0.0)  # New!
            }
            
            # IMPORTANT: Weights must still sum to 1.0!
            total = sum(self.signal_weights.values())
            if total != 1.0:
                self.logger.warning(f"Weights sum to {total}, not 1.0. Normalizing.")
                for key in self.signal_weights:
                    self.signal_weights[key] /= total
        
        def calculate_importance(self, turn: Dict, query: str) -> float:
            """Calculate importance using all signals including new valence."""
            
            # ... existing decay, surprise, relevance, habituation calculations ...
            
            # NEW: Calculate valence score
            memory_text = turn.get('content', '')
            valence_score = self.valence_weighter.score_valence(memory_text)
            
            # Combine all signals
            importance = (
                self.signal_weights['decay'] * decay_score +
                self.signal_weights['surprise'] * surprise_score +
                self.signal_weights['relevance'] * relevance_score +
                self.signal_weights['habituation'] * habituation_score +
                self.signal_weights['valence'] * valence_score  # NEW!
            )
            
            return importance

**Step 4: Write Tests**

.. code-block:: python

    # tests/test_memory_valence.py
    """Tests for valence-based memory scoring."""
    
    import pytest
    from brain.memory_valence import MemoryValenceWeighter

    class TestMemoryValence:
        """Test valence weighting."""
        
        @pytest.fixture
        def weighter(self):
            return MemoryValenceWeighter(
                valence_weight_positive=0.3,
                valence_weight_negative=0.2
            )
            
        def test_positive_emotion_scores_high(self, weighter):
            """Positive emotions should score high."""
            score = weighter.score_valence("I'm so happy and excited!")
            assert score > 0.65  # Should be in positive range
            
        def test_negative_emotion_scores_medium(self, weighter):
            """Negative emotions should score medium."""
            score = weighter.score_valence("I'm frustrated and angry")
            assert 0.3 < score < 0.5  # Medium range
            
        def test_neutral_scores_baseline(self, weighter):
            """Neutral text should score around 0.5."""
            score = weighter.score_valence("The meeting was at 3pm")
            assert 0.45 < score < 0.55  # Near 0.5 baseline
            
        def test_mixed_emotion_balances(self, weighter):
            """Mixed emotions should balance out."""
            score = weighter.score_valence("I'm happy but also frustrated")
            assert 0.45 < score < 0.65  # Between pos and neg
            
        def test_boundary_empty_string(self, weighter):
            """Empty string should return neutral."""
            score = weighter.score_valence("")
            assert score == 0.5
            
        def test_configurable_weights(self):
            """Weights should affect scoring."""
            weighter_high = MemoryValenceWeighter(0.5, 0.1)
            weighter_low = MemoryValenceWeighter(0.1, 0.5)
            
            pos_text = "I love this wonderful thing"
            neg_text = "I hate this terrible thing"
            
            # High positive weight → higher score for positive text
            assert weighter_high.score_valence(pos_text) > weighter_low.score_valence(pos_text)
            
            # High negative weight → higher score for negative text
            assert weighter_high.score_valence(neg_text) < weighter_low.score_valence(neg_text)

**Step 5: Document the Signal**

Add section to `docs/contextual_malleability_guide.rst`:

.. code-block:: rst

    The Valence Signal
    ==================
    
    **What it measures:** Emotional importance (positive/negative arousal)
    
    **Why it matters:** Emotionally significant memories are often important
    (Schwarz 2010: disfluency triggers deeper analysis). But too much emotion
    weight can make Ada obsess over negative news.
    
    **How to tune it:**
    
    - Increase ``MEMORY_VALENCE_WEIGHT_POSITIVE`` if you want Ada to remember
      happy moments more vividly
    - Increase ``MEMORY_VALENCE_WEIGHT_NEGATIVE`` if negative experiences 
      should be heavily weighted (e.g., learning from mistakes)
    - Set both to 0 to completely ignore emotional content (use for Q&A systems)
    
    **Example configurations:**
    
    .. code-block:: bash
    
        # Therapy/counseling: emotion matters
        export MEMORY_VALENCE_WEIGHT_POSITIVE=0.25
        export MEMORY_VALENCE_WEIGHT_NEGATIVE=0.15
        
        # Q&A system: ignore emotion
        export MEMORY_VALENCE_WEIGHT_POSITIVE=0.0
        export MEMORY_VALENCE_WEIGHT_NEGATIVE=0.0
        
        # Discovery: balance emotion and novelty
        export MEMORY_VALENCE_WEIGHT_POSITIVE=0.10
        export MEMORY_VALENCE_WEIGHT_NEGATIVE=0.05

---

Signal Design Principles
=========================

When adding a new signal, follow these principles:

**1. Signal Score Range**

Always return [0.0, 1.0]:

.. code-block:: python

    def score_something(self, memory) -> float:
        """Return value between 0.0 (not important) and 1.0 (very important)."""
        score = self.calculate(memory)
        return max(0.0, min(1.0, score))  # Always clamp!

**2. Weight Proportions**

If adding a signal, preserve total weight = 1.0:

.. code-block:: bash

    # Old (4 signals, each ~0.25)
    IMPORTANCE_WEIGHT_DECAY=0.10
    IMPORTANCE_WEIGHT_SURPRISE=0.60
    IMPORTANCE_WEIGHT_RELEVANCE=0.20
    IMPORTANCE_WEIGHT_HABITUATION=0.10
    
    # New (5 signals, adding valence)
    # Reduce other weights proportionally
    IMPORTANCE_WEIGHT_DECAY=0.08
    IMPORTANCE_WEIGHT_SURPRISE=0.48
    IMPORTANCE_WEIGHT_RELEVANCE=0.16
    IMPORTANCE_WEIGHT_HABITUATION=0.08
    IMPORTANCE_WEIGHT_VALENCE=0.20

**3. Inverse Signal Validation**

If you add a signal, test that toggling it off (weight=0) gives same results:

.. code-block:: python

    def test_signal_toggle_off(self):
        """Toggling a signal off should give previous behavior."""
        # With valence disabled
        importance_without_valence = retriever.calculate_importance(turn, query)
        
        # With valence enabled but weight=0
        retriever.signal_weights['valence'] = 0.0
        importance_with_zero_weight = retriever.calculate_importance(turn, query)
        
        assert abs(importance_without_valence - importance_with_zero_weight) < 0.0001

**4. Boundary Testing**

Always test edge cases:

.. code-block:: python

    def test_signal_boundaries(self):
        """Test signal at 0, 0.5, 1.0 boundaries."""
        assert weighter.score_signal(boundary_memory_min) >= 0.0
        assert weighter.score_signal(boundary_memory_mid) == approx(0.5)
        assert weighter.score_signal(boundary_memory_max) <= 1.0

**5. Performance Considerations**

Signals run on EVERY memory during context retrieval. Keep them fast:

.. code-block:: python

    # GOOD: O(n) where n = words in memory
    def score_valence(self, text):
        return len(text.split() & self.keywords) / len(text.split())
    
    # BAD: O(n²) or requires external API
    def score_valence(self, text):
        for word1 in text.split():
            for word2 in text.split():  # ← This is quadratic!
                if self.are_similar(word1, word2):  # ← And slow

**6. Configuration Discoverability**

Document the "why" in config.py comments:

.. code-block:: python

    # Memory Valence Scoring (Emotional Weight)
    # ==========================================
    #
    # WHAT: Scores memories by emotional content (happiness, anger, etc.)
    # WHY: Schwarz (2010) shows emotional arousal triggers deeper processing
    #
    # CONFIGURATION:
    #   MEMORY_VALENCE_WEIGHT_POSITIVE = weight for positive emotions [0-1]
    #   MEMORY_VALENCE_WEIGHT_NEGATIVE = weight for negative emotions [0-1]
    #
    # EXAMPLES:
    #   Therapy bot: POSITIVE=0.20, NEGATIVE=0.15 (emotions matter)
    #   FAQ system: POSITIVE=0.0, NEGATIVE=0.0 (ignore emotion)
    #
    # RESEARCH: See docs/contextual_malleability_guide.rst "Valence Signal"
    #
    # TRY: Start with POSITIVE=0.15, NEGATIVE=0.05 (balanced)
    MEMORY_VALENCE_WEIGHT_POSITIVE = float(...)

---

Contributing Back
==================

If you create a new signal, consider contributing it:

1. **Fork Ada** (or create a branch)
2. **Add your signal** following the patterns above
3. **Write tests** (aim for 90%+ coverage)
4. **Document it** (in guide + config comments)
5. **Create a PR** with:
   - Motivation (why this signal matters)
   - Empirical results (does it improve Ada?)
   - Configuration guide (how to use it)
   - Example use cases

**Ada's research is public domain (CC0).** Your extensions are too. Share freely! 🚀

---

Signal Checklist
================

.. code-block:: text

    [ ] Signal scorer function written
    [ ] Score range [0.0, 1.0] validated
    [ ] Configuration added to brain/config.py
    [ ] Configuration integrated into context_retriever.py
    [ ] Signal weight added and normalized (sum=1.0)
    [ ] Unit tests written (boundary, toggle, performance)
    [ ] Integration tests written (with other signals)
    [ ] Documented in docs/contextual_malleability_guide.rst
    [ ] Configuration documented in brain/config.py comments
    [ ] Example use cases provided
    [ ] Performance tested (< 10ms per memory)
    [ ] PR created with empirical results

---

Questions?
==========

- **How do I test my signal?** See `tests/test_memory_valence.py` example
- **How fast does it need to be?** Context retrieval runs per query; keep signals < 10ms total
- **Can I use NLP/ML?** Yes! But document dependencies and keep it optional
- **What if my signal conflicts with others?** Weight normalization handles it; test the balance

**Go build weird signals. Document what works. Push the boundaries of Ada!** 🌟
