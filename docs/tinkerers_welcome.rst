============================================================
Welcome, Tinkerers! Your Guide to Ada's Memory System
============================================================

**You want to understand and experiment with how Ada remembers things.**

**This guide is for you.** 🚀

---

Five Minutes: What You Need to Know
====================================

Ada remembers conversations by scoring memories on **importance**.

Score combines 4 signals:

.. code-block:: text

    importance = decay × 0.10 + surprise × 0.60 + relevance × 0.20 + habituation × 0.10

**Plain English:**

- **Decay (0.10):** How old is this? Older = less important.
- **Surprise (0.60):** How unexpected? Novel = more important. ← This one dominates!
- **Relevance (0.20):** How related to what I'm asking? Similar = more important.
- **Habituation (0.10):** How many times have we discussed this? Repetitive = less important.

**One memory's journey:**

.. code-block:: text

    Day 1, Hour 0: "I love hiking"
    └─ Score: 0.85 (fresh, novel, highly relevant to user profile)
    └─ Action: FULL detail included in context
    
    Day 1, Hour 8: (discussed 3 more times, not novel anymore)
    └─ Score: 0.35 (old, familiar, still relevant but repeated)
    └─ Action: CHUNKS (excerpts only)
    
    Day 5, Hour 0: (not mentioned in days)
    └─ Score: 0.15 (old, forgotten, will resurface if needed)
    └─ Action: DROPPED (not included)
    
    Day 30, Hour 0: User asks "What are my interests?"
    └─ Score: 0.08 (very old, but suddenly relevant!)
    └─ Action: Resurfaces but as SUMMARY "You mentioned hiking once"

**That's it.** Everything else is tuning these weights for your use case.

---

Thirty Minutes: Understand Each Signal
=======================================

**Signal 1: Decay (Recency)**

*How old is this memory?*

.. code-block:: bash

    # Configuration
    export MEMORY_DECAY_TIME_SCALE_HOURS=100
    # At 100 hours old: score × 0.37
    # At 200 hours old: score × 0.14
    
    # Experiment
    export MEMORY_DECAY_TIME_SCALE_HOURS=24   # Forget within 1 day
    export MEMORY_DECAY_TIME_SCALE_HOURS=720  # Remember for 30 days

**Use case:**

- **Chat buddy:** Shorter time scale (24-50 hours) - recent context dominates
- **Knowledge keeper:** Longer time scale (500+ hours) - old facts matter
- **Optimal default:** 100 hours (≈4 days before forgetting)

**Signal 2: Surprise (Novelty)** ← **This is the surprising one!**

*How unexpected/novel is this?*

Research (December 2025) found this signal **dominates all others** (0.60 weight).

.. code-block:: bash

    # Experiment 1: Increase surprise weight
    export IMPORTANCE_WEIGHT_SURPRISE=0.80  # Ada obsesses over novelty
    export IMPORTANCE_WEIGHT_DECAY=0.05
    export IMPORTANCE_WEIGHT_RELEVANCE=0.10
    export IMPORTANCE_WEIGHT_HABITUATION=0.05
    # → Ada: "Have you noticed X is unusual?"
    
    # Experiment 2: Decrease surprise weight
    export IMPORTANCE_WEIGHT_SURPRISE=0.20  # Ada ignores novelty
    export IMPORTANCE_WEIGHT_RELEVANCE=0.50
    export IMPORTANCE_WEIGHT_DECAY=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.15
    # → Ada: "Based on patterns, you usually..."

**Intuition vs. Reality:**

- **Intuitive guess:** "Recency matters most" (decay=0.40)
- **Empirical finding:** "Novelty matters most" (surprise=0.60)
- **Improvement:** 12-38% better context selection with optimal weights

**Use case:**

- **Discovery engine:** High surprise (0.70+)
- **Advisor:** Balanced surprise (0.40-0.50)
- **Pattern matcher:** Low surprise (0.20-0.30)

**Signal 3: Relevance (Semantic Similarity)**

*How related to the current query?*

Uses embedding similarity (hidden, but you can tune its threshold):

.. code-block:: bash

    # Configuration
    export IMPORTANCE_WEIGHT_RELEVANCE=0.20  # Currently optimal
    
    # Experiment: Q&A system (care most about relevance)
    export IMPORTANCE_WEIGHT_RELEVANCE=0.60
    export IMPORTANCE_WEIGHT_SURPRISE=0.15
    export IMPORTANCE_WEIGHT_DECAY=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.10
    # → Ada returns directly relevant memories first

**Use case:**

- **FAQ system:** High relevance (0.50+)
- **Chat buddy:** Moderate relevance (0.20-0.30)
- **Discovery:** Low relevance (0.10-0.15)

**Signal 4: Habituation (Repetition Penalty)**

*How many times have we discussed this?*

Penalizes memories mentioned > 3 times in 24 hours:

.. code-block:: bash

    # Configuration
    export CONTEXT_HABITUATION_THRESHOLD=3
    export CONTEXT_HABITUATION_WEIGHT=0.1  # 90% penalty
    export CONTEXT_HABITUATION_DECAY_HOURS=24
    
    # Experiment: Strict (no repetition)
    export CONTEXT_HABITUATION_THRESHOLD=2
    export CONTEXT_HABITUATION_WEIGHT=0.05  # 95% penalty
    
    # Experiment: Permissive (allow repetition)
    export CONTEXT_HABITUATION_WEIGHT=0.5  # Only 50% penalty

**Use case:**

- **Therapy:** Disable habituation (let people talk about it)
- **Chat:** Keep habituation on (avoid boring repetition)
- **FAQ:** Disable habituation (same Q gets same A)

---

Two Hours: Run an Experiment
=============================

**Experiment: Does increasing surprise weight actually do anything?**

**Setup**

.. code-block:: bash

    # Create config file A
    cat > config_a.env << 'EOF'
    IMPORTANCE_WEIGHT_DECAY=0.10
    IMPORTANCE_WEIGHT_SURPRISE=0.40
    IMPORTANCE_WEIGHT_RELEVANCE=0.30
    IMPORTANCE_WEIGHT_HABITUATION=0.20
    EOF
    
    # Create config file B
    cat > config_b.env << 'EOF'
    IMPORTANCE_WEIGHT_DECAY=0.10
    IMPORTANCE_WEIGHT_SURPRISE=0.70
    IMPORTANCE_WEIGHT_RELEVANCE=0.10
    IMPORTANCE_WEIGHT_HABITUATION=0.10
    EOF

**Run Ada with Config A**

.. code-block:: bash

    source config_a.env
    docker compose up -d
    # Wait for startup
    sleep 10

**Test Protocol: Ask about novel things**

.. code-block:: bash

    # Query 1: Establish baseline interest
    ./scripts/cli.sh "I like hiking"
    
    # Wait a few queries
    ./scripts/cli.sh "I prefer sunny weather"
    ./scripts/cli.sh "My favorite food is pasta"
    
    # Query 2: Something surprising related to hiking
    ./scripts/cli.sh "I just bought a robot that does climbing!"
    
    # Query 3: Ask for surprise
    ./scripts/cli.sh "Tell me something interesting about our conversation"

**Note responses:** Is the robot climbing mentioned? How much detail?

**Switch to Config B**

.. code-block:: bash

    source config_b.env
    docker compose restart brain  # Apply new config
    sleep 5

**Run same tests again** - Do you get different responses?

**Metrics to Track**

.. code-block:: python

    # Save responses to JSON
    {
        "config_a": {
            "response_1": "I noted your love for hiking",
            "response_2": "Interesting! A robot climber - that's a twist on your hiking interest",
            "response_3": "The robot climber was unexpected..."
        },
        "config_b": {
            "response_1": "You enjoy hiking",
            "response_2": "A robot climber - novel combination!",
            "response_3": "Most surprising: your robot climber concept"
        }
    }
    
    # Compare:
    # - How much is the robot mentioned?
    # - How many words about novelty?
    # - Do the responses feel different in tone?

**This is real science.** Document what you find!

---

One Day: Build Your Perfect Configuration
==========================================

**Step 1: Identify Your Use Case**

.. code-block:: text

    I want Ada to be...
    [ ] A discovery engine (find new things)
    [ ] A Q&A system (answer questions accurately)
    [ ] A chat buddy (remember and relate to me)
    [ ] A knowledge keeper (retain everything)
    [ ] A pattern finder (identify trends)
    [ ] Something weird (describe below)

**Step 2: Find the Template**

From `docs/contextual_malleability_quick_ref.rst`, use the preset:

.. code-block:: bash

    # For chat buddy (balanced):
    export IMPORTANCE_WEIGHT_DECAY=0.15
    export IMPORTANCE_WEIGHT_SURPRISE=0.50
    export IMPORTANCE_WEIGHT_RELEVANCE=0.25
    export IMPORTANCE_WEIGHT_HABITUATION=0.10
    
    # For discovery engine (novelty):
    export IMPORTANCE_WEIGHT_DECAY=0.05
    export IMPORTANCE_WEIGHT_SURPRISE=0.70
    export IMPORTANCE_WEIGHT_RELEVANCE=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

**Step 3: Tune the Detail Thresholds**

How much context detail does Ada include?

.. code-block:: bash

    # Default (balanced)
    export GRADIENT_THRESHOLD_FULL=0.75
    export GRADIENT_THRESHOLD_CHUNKS=0.50
    export GRADIENT_THRESHOLD_SUMMARY=0.20
    
    # Ultra-concise (fast responses)
    export GRADIENT_THRESHOLD_FULL=0.85
    export GRADIENT_THRESHOLD_CHUNKS=0.65
    export GRADIENT_THRESHOLD_SUMMARY=0.35
    
    # Maximum context (longer responses, more tokens)
    export GRADIENT_THRESHOLD_FULL=0.60
    export GRADIENT_THRESHOLD_CHUNKS=0.35
    export GRADIENT_THRESHOLD_SUMMARY=0.10

**Step 4: Test and Iterate**

.. code-block:: bash

    # Apply config
    source my_config.env
    docker compose restart brain
    sleep 5
    
    # Ask questions that reveal the difference
    ./scripts/cli.sh "What do you know about me?"
    ./scripts/cli.sh "Tell me something surprising"
    ./scripts/cli.sh "What patterns do you see?"
    
    # Adjust and retry
    # → Responses felt too brief? Lower thresholds
    # → Responses too repetitive? Increase habituation penalty
    # → Need more novelty? Increase surprise weight

---

One Week: Join the Research
============================

**You've been experimenting.** Now share what you learned!

**Option 1: Document Your Configuration**

Create `.ai/explorations/my_configuration_X.md`:

.. code-block:: markdown

    # Configuration: "Hiking Buddy"
    
    **Use case:** Ada as a hiking enthusiast who shares recommendations
    
    **Configuration:**
    ```bash
    IMPORTANCE_WEIGHT_DECAY=0.08
    IMPORTANCE_WEIGHT_SURPRISE=0.65
    IMPORTANCE_WEIGHT_RELEVANCE=0.17
    IMPORTANCE_WEIGHT_HABITUATION=0.10
    GRADIENT_THRESHOLD_FULL=0.70
    GRADIENT_THRESHOLD_CHUNKS=0.45
    GRADIENT_THRESHOLD_SUMMARY=0.15
    ```
    
    **Results:**
    - Ada remembered hiking preferences for 5+ days
    - Suggested novel trails based on unusual preferences
    - Avoided boring repetition of "I like hiking"
    
    **Lessons learned:**
    - Higher surprise weight → Ada discovers interesting combinations
    - Lower decay threshold → Keeps old memories accessible
    
    **Try these experiments:**
    - Change decay time to 48hrs and see if Ada forgets too fast
    - Disable habituation entirely for pure enthusiasm
    
    **Trade-offs:**
    - Longer responses (more context included)
    - Sometimes tangential (novelty weight can prioritize weird stuff)

**Option 2: Report a Bug or Unexpected Behavior**

If something seems wrong:

.. code-block:: markdown

    **Issue:** Ada forgets important context
    
    **Configuration:**
    - IMPORTANCE_WEIGHT_DECAY=0.05
    - IMPORTANCE_WEIGHT_SURPRISE=0.60
    - IMPORTANCE_WEIGHT_RELEVANCE=0.25
    - IMPORTANCE_WEIGHT_HABITUATION=0.10
    - MEMORY_DECAY_TIME_SCALE_HOURS=100
    
    **Reproduction:**
    1. Set user preference: "I'm a Python programmer"
    2. Wait 4 days
    3. Ask: "What's my programming language?"
    
    **Actual:** "I don't have information about that"
    **Expected:** "You mentioned you're a Python programmer"
    
    **Hypothesis:** Decay weight too low? Or time scale not working?
    
    **Debug logs:**
    [paste relevant log section]

**Option 3: Create an Extension**

Add a new signal (see `docs/extending_contextual_malleability.rst`):

.. code-block:: bash

    # For example: Add "emotionality" signal
    # 1. Create brain/memory_emotion.py
    # 2. Write tests
    # 3. Integrate into context_retriever.py
    # 4. Document in config.py
    # 5. Create PR with results
    
    # Expected result: Emotionally significant memories remembered longer

---

Reference: Files You'll Use Most
=================================

📖 **Learning**

- `docs/contextual_malleability_guide.rst` - Deep explanation of all signals
- `docs/contextual_malleability_quick_ref.rst` - Quick lookup reference
- `docs/experimenters_cookbook.rst` - Detailed experiment protocols

🔧 **Tinkering**

- `brain/config.py` - All environment variables (with explanations!)
- `brain/prompt_builder/context_retriever.py` - Where importance scores are calculated
- `brain/memory_decay.py` - Decay signal implementation (example)

🧪 **Testing**

- `tests/test_context_retriever.py` - How to test your changes
- `tests/test_memory_decay.py` - Example test patterns
- `.ai/TESTING.md` - Testing philosophy

🚀 **Contributing**

- `docs/extending_contextual_malleability.rst` - How to add new signals
- `.ai/codebase-map.json` - Module relationships
- `.ai/RESEARCH-FINDINGS-V2.2.md` - Empirical validation of current weights

---

Common Questions
=================

**Q: Can I break Ada by changing weights wrong?**

A: No! You can always reset by removing the env vars (defaults will work). Weights always normalize to 1.0, so math stays sound.

**Q: What's the easiest way to start?**

A: Copy a template from `contextual_malleability_quick_ref.rst` and just increase or decrease one weight by 0.05 to see the effect.

**Q: Why does surprise matter so much (0.60)?**

A: Surprise triggers deeper cognitive processing (Schwarz 2010). Humans pay attention to unexpected things. Ada should too!

**Q: Can I disable a signal?**

A: Yes! Set its weight to 0.0 and increase others. Example: no novelty detection at all:

.. code-block:: bash

    export IMPORTANCE_WEIGHT_SURPRISE=0.0
    export IMPORTANCE_WEIGHT_RELEVANCE=0.40
    export IMPORTANCE_WEIGHT_DECAY=0.40
    export IMPORTANCE_WEIGHT_HABITUATION=0.20

**Q: My experiment worked! Can I share it?**

A: YES! Open an issue or PR with your findings. Link to `.ai/explorations/` if you documented it there.

**Q: What if I want to add a completely new signal?**

A: Read `docs/extending_contextual_malleability.rst`. It has a full walkthrough of adding valence (emotion) as an example signal.

---

You're Ready!
=============

✅ You understand the 4 signals  
✅ You know how to configure them  
✅ You've run an experiment  
✅ You have templates for your use case  
✅ You know how to share your findings  

**Now go tinker!**

- Try wild weight combinations
- Break Ada in interesting ways
- Build your perfect configuration
- Discover emergent behaviors
- Share what you learn
- Maybe add a new signal

**Ada's science is public domain.** Your experiments are too. 

Build weird things. Question the defaults. Push the boundaries.

That's what tinkerers do. 🔨✨

---

Resources
=========

- **Fast reference:** `docs/contextual_malleability_quick_ref.rst`
- **Deep dive:** `docs/contextual_malleability_guide.rst`
- **Experiments:** `docs/experimenters_cookbook.rst`
- **Extensions:** `docs/extending_contextual_malleability.rst`
- **Research:** `.ai/RESEARCH-FINDINGS-V2.2.md`
- **Code:** `brain/prompt_builder/context_retriever.py`
- **Tests:** `tests/test_context_retriever.py`

**Questions?** Open an issue. We're here to help.

**Ready to change the world of AI memory?** Let's go. 🚀
