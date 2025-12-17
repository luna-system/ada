Token Budget Monitoring
======================

.. note::
   This feature is part of Ada v2.0's biomimetic foundation. It provides visibility
   into token usage patterns before implementing optimization strategies.

Overview
--------

The Token Budget Monitor tracks how many tokens are consumed by different parts of Ada's
context window:

- **Persona** - Your AI persona description
- **FAQ** - Frequently asked questions and answers
- **Memories** - Retrieved memories from RAG search
- **Conversation History** - Recent messages
- **Specialist Results** - OCR output, web searches, etc.
- **System Notices** - Important system alerts

Why Token Monitoring?
~~~~~~~~~~~~~~~~~~~~~

**The Problem**: Modern LLMs have large context windows (128k+ tokens), but loading
too much context:

1. Slows down responses (more tokens to process)
2. Costs more (token-based pricing)
3. Can overwhelm the model with irrelevant information
4. Makes it harder to stay within limits

**The Solution**: Track what's using tokens so we can optimize strategically.

Architecture
------------

The monitoring system uses ``tiktoken`` (OpenAI's tokenizer) to accurately count
tokens the way language models see them.

.. code-block:: python

   from brain.token_monitor import TokenBudgetMonitor
   
   # Initialize monitor
   monitor = TokenBudgetMonitor(
       max_tokens=128000,      # Context window size
       warning_threshold=102400 # Warn at 80%
   )
   
   # Track components
   monitor.track("persona", persona_text)
   monitor.track("memories", memory_text)
   monitor.track("specialist_ocr", ocr_results)
   
   # Get breakdown
   breakdown = monitor.get_breakdown()
   print(f"Total tokens: {breakdown.total_tokens}")
   print(f"Percentage used: {breakdown.percentage_used:.1f}%")
   
   # Human-readable summary
   print(monitor.get_summary())

Data Structures
--------------

ComponentTokens
~~~~~~~~~~~~~~

Tracks tokens for a single component:

.. code-block:: python

   @dataclass
   class ComponentTokens:
       tokens: int          # Absolute token count
       percentage: float    # Percentage of total

TokenUsageBreakdown
~~~~~~~~~~~~~~~~~~

Complete breakdown of all token usage:

.. code-block:: python

   @dataclass
   class TokenUsageBreakdown:
       components: Dict[str, ComponentTokens]  # Per-component stats
       total_tokens: int                        # Sum of all components
       percentage_used: float                   # Percentage of budget
       is_warning: bool                         # True if over threshold

API Reference
------------

TokenBudgetMonitor
~~~~~~~~~~~~~~~~~

.. py:class:: TokenBudgetMonitor(max_tokens=128000, warning_threshold=102400, model="gpt-4")

   Main monitoring class.
   
   :param max_tokens: Maximum token budget (context window size)
   :param warning_threshold: Token count at which to warn
   :param model: Model name for tokenizer (affects counting)

   .. py:method:: count_tokens(text: str) -> int
   
      Count tokens in text.
      
      :param text: Text to count tokens for
      :returns: Number of tokens
   
   .. py:method:: track(component: str, text: str) -> int
   
      Track token usage for a component.
      
      :param component: Component name (e.g., "persona", "memories")
      :param text: Text content to track
      :returns: Number of tokens in this text
      
      Components accumulate tokens if tracked multiple times.
   
   .. py:method:: get_breakdown() -> TokenUsageBreakdown
   
      Get detailed breakdown of token usage.
      
      :returns: TokenUsageBreakdown with all stats
   
   .. py:method:: get_summary() -> str
   
      Get human-readable summary.
      
      :returns: Formatted string with breakdown
   
   .. py:method:: get_top_components(n: int = 3) -> List[Tuple[str, int]]
   
      Get top N components by token usage.
      
      :param n: Number of components to return
      :returns: List of (name, tokens) tuples, sorted descending
   
   .. py:method:: reset()
   
      Reset tracking for a new request.
      
      Call at the start of each request to track independently.
   
   .. py:method:: log_breakdown()
   
      Log detailed breakdown at INFO level.
      
      Useful for debugging and monitoring.

Usage Examples
-------------

Basic Tracking
~~~~~~~~~~~~~

.. code-block:: python

   from brain.token_monitor import TokenBudgetMonitor
   
   monitor = TokenBudgetMonitor()
   
   # Track different components
   monitor.track("persona", "I am Ada, a friendly AI assistant...")
   monitor.track("memories", "User prefers Python over JavaScript...")
   monitor.track("history", "User: Hello! Ada: Hi there!")
   
   # Get summary
   print(monitor.get_summary())
   
   # Output:
   # Token Usage: 1,234 / 128,000 (0.96%)
   #
   # Breakdown by component:
   #   history              :    567 tokens ( 45.9%)
   #   memories             :    456 tokens ( 37.0%)
   #   persona              :    211 tokens ( 17.1%)

Warning Detection
~~~~~~~~~~~~~~~~

.. code-block:: python

   monitor = TokenBudgetMonitor(
       max_tokens=1000,
       warning_threshold=800
   )
   
   # Add a lot of content
   monitor.track("large_component", "..." * 500)
   
   breakdown = monitor.get_breakdown()
   if breakdown.is_warning:
       print(f"⚠️  Warning! Using {breakdown.total_tokens} tokens")
       print("Top components:")
       for name, tokens in monitor.get_top_components(3):
           print(f"  {name}: {tokens} tokens")

Integration with Prompt Builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from brain.prompt_builder import build_prompt
   from brain.token_monitor import TokenBudgetMonitor
   
   # Create monitor
   monitor = TokenBudgetMonitor()
   
   # Build prompt with monitoring
   prompt = build_prompt(
       user_message="What's the weather?",
       token_monitor=monitor  # Pass monitor
   )
   
   # Log what was used
   monitor.log_breakdown()

Per-Request Tracking
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   monitor = TokenBudgetMonitor()
   
   for request in requests:
       # Reset for new request
       monitor.reset()
       
       # Track this request
       monitor.track("persona", persona)
       monitor.track("context", request.context)
       
       # Process request...
       
       # Log usage for this request
       monitor.log_breakdown()

Token Counting Details
---------------------

The monitor uses ``tiktoken`` to count tokens exactly as language models do.

.. important::
   Different models tokenize differently! The default uses GPT-4's tokenizer
   for consistency, but you can specify a different model:
   
   .. code-block:: python
   
      # Use a different tokenizer
      monitor = TokenBudgetMonitor(model="gpt-3.5-turbo")

Common token counts (approximate):

- "Hello" = 1 token
- "Hello world" = 2 tokens  
- "Hello, how are you?" = 6 tokens
- Average English word ≈ 1.3 tokens
- 100 words ≈ 130 tokens
- 1000 words ≈ 1300 tokens

Performance Considerations
-------------------------

Token counting is fast but not free:

- **Negligible impact** for normal usage (< 1ms per component)
- **Caching recommended** for large static content (persona, FAQ)
- **Monitor overhead** is far less than token processing by LLM

The token monitor itself uses minimal memory:

- ~1KB per component tracked
- Tracking 20 components = ~20KB overhead
- Completely acceptable for the visibility gained

Future Enhancements
------------------

Planned improvements for v2.0:

1. **Automatic Optimization** - Suggest which components to cache or reduce
2. **Historical Tracking** - Track token usage over time to identify trends
3. **Budget Allocation** - Set per-component token budgets
4. **Smart Truncation** - Automatically trim least important components when over budget
5. **Model-Specific Optimization** - Tune counting for different model families

Integration Status
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Component
     - Status
     - Notes
   * - Token Monitor (Core)
     - ✅ Complete
     - All tests passing
   * - Prompt Builder Integration
     - 🚧 Planned
     - Next step
   * - Logging Integration
     - 🚧 Planned
     - Automatic logging
   * - Dashboard/UI
     - 📋 Future
     - Visual token breakdown
   * - API Endpoint
     - 📋 Future
     - ``GET /v1/tokens/usage``

See Also
--------

- :doc:`architecture` - How token monitoring fits in Ada's architecture
- :doc:`memory` - RAG system that benefits from token optimization
- :doc:`streaming` - How tokens flow through the system
- **Phase 1 Roadmap** - ``.ai/explorations/planning/IMPLEMENTATION_ROADMAP.md``

.. note::
   Token monitoring is **read-only** - it observes but doesn't modify behavior.
   This provides a safe foundation for optimization features built on top.
