============================================================
Experimenter's Cookbook: Profiling Contextual Malleability
============================================================

**For researchers and weird kids who want to measure what their tweaks actually do**

---

Philosophy
===========

This is NOT about finding THE BEST configuration. Ada's optimal weights (0.10 decay, 0.60 surprise, 0.20 relevance, 0.10 habituation) were empirically validated in December 2025 and are already deployed.

This cookbook is about:

1. **Understanding your use case** - What does Ada need to do for you?
2. **Measuring the effects** - How much do knob adjustments actually matter?
3. **Building intuition** - What does each weight *really* do in practice?
4. **Discovering emergent properties** - What weird behaviors emerge from different weight combinations?

---

Experiment 1: The Novelty Knob
==============================

**Question:** How much does surprise weight affect Ada's tendency to focus on new information vs. context?

**Setup**

.. code-block:: bash

    # Configuration A: Low surprise (0.20)
    export IMPORTANCE_WEIGHT_SURPRISE=0.20
    export IMPORTANCE_WEIGHT_DECAY=0.20
    export IMPORTANCE_WEIGHT_RELEVANCE=0.40
    export IMPORTANCE_WEIGHT_HABITUATION=0.20

    # Start Ada
    docker compose up -d

    # Configuration B: High surprise (0.70)
    export IMPORTANCE_WEIGHT_SURPRISE=0.70
    export IMPORTANCE_WEIGHT_DECAY=0.10
    export IMPORTANCE_WEIGHT_RELEVANCE=0.15
    export IMPORTANCE_WEIGHT_HABITUATION=0.05

    # Note the timestamp or use a test harness

**Test Protocol**

.. code-block:: text

    CONVERSATION SEQUENCE:

    1. "I enjoy hiking, especially mountain trails"
       → Ada: [establishes hiking as interest]

    2. "I went hiking last weekend" 
       → Ada: [includes hiking memory]

    3. (wait a few turns)

    4. "Tell me about my interests"
       → Ada: [does hiking get emphasized?]

    5. "There's a new hiking trail near me"
       → Ada: [how much does novelty of trail weigh vs. existing hiking memory?]

**Metrics to Track**

.. code-block:: python

    # Measure surprise weight's impact
    importance_scores_config_a = []  # Collect from logs
    importance_scores_config_b = []

    # For each context memory retrieved:
    surprise_contribution_a = importance_scores_config_a * 0.20
    surprise_contribution_b = importance_scores_config_b * 0.70

    # Hypothesis: With high surprise weight, newer trail info gets higher score
    # even if hiking memories are more relevant to user profile

**Expected Results**

- **Config A (low surprise):** Ada focused on consistent user profile
- **Config B (high surprise):** Ada more excited about the NEW trail
- **Measurement:** Token allocation to "trail discovery" vs "hiking profile"

**Insight Generated**

- If you want Ada to be a **discovery engine**, increase surprise weight
- If you want Ada as **context keeper**, decrease surprise weight
- If you want **balanced behavior**, keep it at 0.60 (optimal)

---

Experiment 2: The Recency Trap
===============================

**Question:** How much does decay weight matter? Does older context ever get used?

**Setup**

.. code-block:: bash

    # Configuration A: Strong recency (decay=0.50)
    export IMPORTANCE_WEIGHT_DECAY=0.50
    export MEMORY_DECAY_TIME_SCALE_HOURS=24

    # Configuration B: Weak recency (decay=0.05)
    export IMPORTANCE_WEIGHT_DECAY=0.05
    export MEMORY_DECAY_TIME_SCALE_HOURS=336  # 2 weeks

**Test Protocol: The Long Memory Test**

.. code-block:: text

    DAY 1:
    - User: "I was born in Marseille"
    - Ada: [stores long-lived biographical fact]

    DAY 2-5:
    - Many intervening conversations on other topics

    DAY 6:
    - User: "Where was I born?"
    - Ada: [can it remember across 5+ days of other context?]

    MEASURE: Time to reach importance threshold < 0.20 (DROPPED)

**Metrics**

.. code-block:: bash

    # Calculate memory half-life under each configuration
    time_at_50_percent = ln(2) * TIME_SCALE_HOURS
    
    # Config A: ~17 hours
    # Config B: ~233 hours (~10 days)

**Testing Code**

.. code-block:: python

    from brain.memory_decay import MemoryDecayWeighter
    from datetime import datetime, timedelta, timezone

    # Test Config A
    decay_a = MemoryDecayWeighter(time_scale_hours=24)
    
    # Test Config B
    decay_b = MemoryDecayWeighter(time_scale_hours=336)

    # Create a memory from 7 days ago
    old_memory_time = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    
    decay_score_a = decay_a.weight_by_decay(
        memory_timestamp=old_memory_time,
        base_importance=1.0
    )
    decay_score_b = decay_b.weight_by_decay(
        memory_timestamp=old_memory_time,
        base_importance=1.0
    )

    print(f"Config A (24h scale): {decay_score_a:.3f}")
    print(f"Config B (336h scale): {decay_score_b:.3f}")

**Expected Results**

- **Config A:** 7-day-old memory nearly DROPPED (score ~0.05-0.10)
- **Config B:** 7-day-old memory still CHUNKS or higher (score ~0.30-0.50)

**Insight Generated**

- For **chat buddy**: higher decay (0.15-0.25) = recent context dominates
- For **research assistant**: lower decay (0.05-0.10) = can reach back further
- For **knowledge keeper**: very low decay (0.02-0.05) = almost never forgets

---

Experiment 3: The Relevance Threshold
=======================================

**Question:** What's the practical difference between including a memory vs. summarizing it?

**Setup**

.. code-block:: bash

    # Configuration A: Permissive chunks (show more detail)
    export GRADIENT_THRESHOLD_FULL=0.65
    export GRADIENT_THRESHOLD_CHUNKS=0.40
    export GRADIENT_THRESHOLD_SUMMARY=0.15

    # Configuration B: Strict chunks (show less detail)
    export GRADIENT_THRESHOLD_FULL=0.85
    export GRADIENT_THRESHOLD_CHUNKS=0.65
    export GRADIENT_THRESHOLD_SUMMARY=0.35

**Test Protocol**

.. code-block:: text

    USER: "What have we talked about?"

    MEASURE:
    - How many memories are included?
    - What's the token count impact?
    - Do responses feel more "forgetful" or "talkative"?

**Metrics**

.. code-block:: python

    # For each query, measure:
    configs = {
        'permissive': {'full': 0.65, 'chunks': 0.40, 'summary': 0.15},
        'strict': {'full': 0.85, 'chunks': 0.65, 'summary': 0.35}
    }

    for config_name, thresholds in configs.items():
        # Set thresholds
        # Run query 10 times
        tokens_used = []
        memories_retrieved = []
        
        print(f"{config_name}: {sum(tokens_used)/len(tokens_used):.0f} avg tokens")
        print(f"{config_name}: {sum(memories_retrieved)/len(memories_retrieved):.1f} avg memories")

**Expected Results**

- **Permissive:** More memories included, longer responses, more tokens (but better context)
- **Strict:** Fewer memories, shorter responses, fewer tokens (but less context)
- **Sweet spot:** Around 0.65/0.40/0.20 (current defaults)

---

Experiment 4: The Habituation Refractory Period
================================================

**Question:** How does habituation interact with user interests? Do repeated questions get better or worse?

**Setup**

.. code-block:: bash

    # Configuration A: No habituation penalty
    export CONTEXT_HABITUATION_WEIGHT=1.0  # No penalty

    # Configuration B: Aggressive habituation
    export CONTEXT_HABITUATION_THRESHOLD=2
    export CONTEXT_HABITUATION_WEIGHT=0.05
    export CONTEXT_HABITUATION_DECAY_HOURS=24

**Test Protocol: The Repetition Test**

.. code-block:: text

    TURN 1: User: "What's your favorite color?"
    TURN 2: User: "What's your favorite color?" (exact repeat)
    TURN 3: User: "What's your favorite color?" (exact repeat)

    MEASURE:
    - Does habituation kick in by turn 2 or turn 3?
    - Does response quality degrade?
    - After 24hr, does response improve again?

**Metrics**

.. code-block:: python

    responses = []
    
    # Config A - without habituation penalty
    for i in range(3):
        response = ada.chat("What's your favorite color?")
        responses.append(response)
    
    # All responses should be similar (no penalty)
    print("Config A similarity:", compare_responses(responses[0], responses[2]))
    
    # Config B - with habituation
    responses = []
    for i in range(3):
        response = ada.chat("What's your favorite color?")
        responses.append(response)
        
    # Response 3 might be shorter/less enthusiastic
    print("Config B similarity:", compare_responses(responses[0], responses[2]))

**Expected Results**

- **Config A:** Repeated question = same detailed response (boring but reliable)
- **Config B:** Repeated question = shorter response by turn 3 (conversational fatigue)

**Insight Generated**

- For **FAQ systems**: disable habituation (HABITUATION_WEIGHT=1.0)
- For **conversation**: keep habituation enabled (0.05-0.10)
- For **research queries**: disable habituation (need to ask same question different ways)

---

Experiment 5: The Weight Balance Discovery
===========================================

**Question:** What happens when you flip ALL the weights? (Chaos experiment)

**Setup**

.. code-block:: bash

    # Standard configuration (optimal)
    export IMPORTANCE_WEIGHT_DECAY=0.10
    export IMPORTANCE_WEIGHT_SURPRISE=0.60
    export IMPORTANCE_WEIGHT_RELEVANCE=0.20
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

    # Inverted (what if we ANTI-optimize?)
    export IMPORTANCE_WEIGHT_DECAY=0.60
    export IMPORTANCE_WEIGHT_SURPRISE=0.10
    export IMPORTANCE_WEIGHT_RELEVANCE=0.20
    export IMPORTANCE_WEIGHT_HABITUATION=0.10

**Test Protocol: Qualitative Feel Test**

.. code-block:: text

    With optimal weights:
    - Ada: "I notice you keep mentioning hiking. That's interesting!"
    
    With inverted weights:
    - Ada: "Based on what we talked about 3 days ago..."
    - Ada: "That reminds me of our conversation last week..."

**Metrics**

.. code-block:: bash

    # Simple: Run 10 queries, count references to:
    recent_references=0     # "just now", "earlier", "recently"
    old_references=0        # "last week", "3 days ago", "previously"
    novel_references=0      # "interesting", "unusual", "novel"
    expected_references=0   # "as expected", "typically", "usually"

**Expected Results**

- **Optimal:** Good balance of all types
- **Inverted (high decay):** Obsesses about the past
- **Finding:** Surprised that recency ISN'T the dominant factor!

---

Experiment 6: The Processing Mode Adaptation
=============================================

**Question:** Does processing mode detection actually change behavior? (Requires processing_modes enabled)

**Setup**

.. code-block:: bash

    export PROCESSING_MODES_ENABLED=true

**Test Protocol**

.. code-block:: text

    ANALYTICAL QUERY:
    User: "How does photosynthesis work? Explain the chemical equations."
    → Ada: [uses higher relevance weight, more technical]

    CREATIVE QUERY:
    User: "Tell me a story about a robot learning to dance"
    → Ada: [uses higher surprise weight, more novelty]

    CONVERSATIONAL QUERY:
    User: "Hey, how was your day?"
    → Ada: [balanced weights, more recent context]

**Metrics**

.. code-block:: bash

    # Measure context composition
    analytical_mode:
        - relevance score > 0.7
        - technical vocabulary count
        
    creative_mode:
        - surprise score > 0.7
        - narrative elements count
        
    conversational_mode:
        - balanced scores around 0.4-0.6
        - recent memory count

**Expected Results**

- Mode detection successfully identifies query type
- Weight adjustments actually take effect
- Different response characteristics for each mode

---

Running Your Own Experiments
==============================

**Template: The Experiment Harness**

.. code-block:: python

    """
    experiment_runner.py
    Simple harness for systematic experimentation
    """
    import os
    import subprocess
    import json
    from datetime import datetime

    class ExperimentRun:
        def __init__(self, name, config):
            self.name = name
            self.config = config
            self.results = {}
            
        def set_environment(self):
            """Apply configuration"""
            for key, value in self.config.items():
                os.environ[key] = str(value)
                
        def run_query(self, query, num_runs=5):
            """Run a query multiple times, collect metrics"""
            responses = []
            token_counts = []
            
            for i in range(num_runs):
                # Run Ada query
                result = subprocess.run(
                    ['python', '-m', 'ada_cli', query],
                    capture_output=True,
                    text=True
                )
                responses.append(result.stdout)
                # Extract token count from logs
                
            return {
                'responses': responses,
                'avg_tokens': sum(token_counts) / len(token_counts),
                'consistency': self._compute_consistency(responses)
            }
            
        def _compute_consistency(self, responses):
            """Rough measure of response variation"""
            lengths = [len(r) for r in responses]
            variance = sum((l - sum(lengths)/len(lengths))**2 for l in lengths)
            return variance / (sum(lengths)/len(lengths))**2

    # Run experiment
    if __name__ == '__main__':
        configs = {
            'optimal': {
                'IMPORTANCE_WEIGHT_DECAY': 0.10,
                'IMPORTANCE_WEIGHT_SURPRISE': 0.60,
                'IMPORTANCE_WEIGHT_RELEVANCE': 0.20,
                'IMPORTANCE_WEIGHT_HABITUATION': 0.10,
            },
            'surprise_focused': {
                'IMPORTANCE_WEIGHT_DECAY': 0.05,
                'IMPORTANCE_WEIGHT_SURPRISE': 0.80,
                'IMPORTANCE_WEIGHT_RELEVANCE': 0.10,
                'IMPORTANCE_WEIGHT_HABITUATION': 0.05,
            }
        }
        
        queries = [
            "What are my interests?",
            "Tell me something surprising about our conversation",
            "Remind me what we discussed last time"
        ]
        
        results = {}
        for config_name, config in configs.items():
            exp = ExperimentRun(config_name, config)
            exp.set_environment()
            
            results[config_name] = {}
            for query in queries:
                results[config_name][query] = exp.run_query(query)
                
        # Save results
        with open(f'experiment_results_{datetime.now().isoformat()}.json', 'w') as f:
            json.dump(results, f, indent=2)

---

Publishing Your Findings
==========================

If you discover something cool, consider:

1. **Document it**: Write it up in a `.ai/explorations/` file
2. **Share it**: Link it in discussion/issues
3. **Make it replicable**: Include configuration files
4. **Cite Ada's research**: Reference `.ai/RESEARCH-FINDINGS-V2.2.md`

---

Key Takeaways
==============

✅ All knobs are yours to turn
✅ Changes are reversible (just change env vars)
✅ Measure actual effects, don't just guess
✅ Edge cases are interesting (what breaks?)
✅ Document what you learn

**The research shows surprise matters most. But your use case might be different.**

Go experiment. Build weird things. Share what works. 🚀
