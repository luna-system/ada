===============
Code Completion
===============

**Copilot-style autocomplete in Neovim with Ada!** (v2.6+)

Ada provides native code completion with full context awareness, running entirely on your local machine. Press ``<C-x><C-a>`` in insert mode to get intelligent code suggestions.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Overview
========

**What You Get:**

- **10.6x faster than general models** - Optimized for code-specific models with FIM format
- **Context-aware completion** - Sees code before AND after cursor
- **Language-agnostic** - Works with Python, JavaScript, Lua, Rust, Go, and more
- **Privacy-first** - Runs entirely on your machine, no cloud dependencies
- **Copilot parity** - Similar quality and speed to commercial offerings

**Performance:**

- Mean latency: **2.6s**
- Quality score: **77%**
- Success rate: **100%** across 24 test scenarios
- Model size: 4.7GB (qwen2.5-coder:7b)

Quick Setup
===========

**Time:** 5 minutes

1. Pull the Code Model
----------------------

.. code-block:: bash

   ollama pull qwen2.5-coder:7b

This specialized model is optimized for code completion with FIM (Fill-In-Middle) format support.

2. Install ada.nvim
-------------------

Add to your Neovim config:

**Lazy.nvim:**

.. code-block:: lua

   {
     dir = "~/Code/ada-v1/ada.nvim",
     config = function()
       require("ada").setup({
         ada_url = "http://localhost:7000",
         completion = {
           enabled = true,
           model = "qwen2.5-coder:7b",
         },
       })
     end,
   }

**Packer.nvim:**

.. code-block:: lua

   use {
     "~/Code/ada-v1/ada.nvim",
     config = function()
       require("ada").setup({
         ada_url = "http://localhost:7000",
         completion = {
           enabled = true,
           model = "qwen2.5-coder:7b",
         },
       })
     end,
   }

3. Test It!
-----------

.. code-block:: bash

   cd ~/Code/ada-v1/ada.nvim
   ./test.sh

Open a code file and press ``<C-x><C-a>`` in insert mode.

Usage
=====

Basic Completion
----------------

1. **Open a code file** in Neovim
2. **Type some code** and position your cursor
3. **Press** ``<C-x><C-a>`` in insert mode
4. **Wait ~2-3 seconds** for the completion
5. **Accept or reject** the suggestion

The completion appears in a floating window with:

- Completed code
- Language detection
- Latency information

Advanced Features
-----------------

**Context Awareness:**

Ada sees code both before AND after your cursor, enabling:

- **Completing function bodies** when signature exists
- **Filling in middle of loops** with context from both sides
- **Smart import suggestions** based on usage below

**Language Support:**

Tested and working with:

- Python (functions, classes, error handling)
- JavaScript/TypeScript (async/await, promises, React)
- Lua (Neovim configs, functions)
- Rust (lifetimes, traits, error handling)
- Go (interfaces, error handling)
- And more! (Any language the model knows)

**Quality Scoring:**

Each completion is scored on:

- Syntax correctness (30%)
- Context relevance (40%)
- Completeness (30%)

Scores above 70% are considered high-quality.

Configuration
=============

Customize in your ``setup()`` call:

.. code-block:: lua

   require("ada").setup({
     ada_url = "http://localhost:7000",
     completion = {
       enabled = true,
       model = "qwen2.5-coder:7b",  -- Which model to use
       max_tokens = 150,              -- Max completion length
       temperature = 0.2,             -- Lower = more focused
       timeout = 10000,               -- 10s timeout
     },
   })

**Available Models:**

- ``qwen2.5-coder:7b`` (recommended) - 4.7GB, fast and accurate
- ``qwen2.5-coder:3b`` - 2.0GB, faster but less accurate
- ``qwen2.5-coder:14b`` - 8.9GB, slower but more capable
- ``deepseek-coder-v2`` - Alternative, similar performance

**Custom Keybinding:**

Change the default ``<C-x><C-a>``:

.. code-block:: lua

   vim.keymap.set('i', '<C-space>', function()
     require('ada.completion').complete()
   end, { desc = 'Ada code completion' })

Architecture
============

How It Works
------------

1. **Cursor position detected** - Neovim plugin captures context
2. **Code extracted** - Before cursor (prefix) and after cursor (suffix)
3. **Language detected** - From filetype (e.g., ``python``, ``javascript``)
4. **MCP tool invoked** - ``complete_code`` tool in ada-mcp
5. **Ollama queried directly** - Bypasses RAG overhead for speed
6. **FIM format used** - Model fills in the middle between prefix and suffix
7. **Result returned** - Completion appears in floating window

**Data Flow:**

.. code-block:: text

   Neovim → ada.nvim → MCP complete_code → Ollama → qwen2.5-coder
                                                     ↓
                                                   FIM format
                                                     ↓
                                          Completion ← Model

**Why It's Fast:**

- **Direct Ollama access** - Skips RAG, prompt building, specialists
- **FIM format** - Code models trained specifically for this task
- **Low temperature** - Focused output, less token generation
- **Smart max tokens** - 150 tokens balance quality and speed

Performance
===========

Benchmarks (24 Test Cases)
---------------------------

Comparing a general-purpose model (example: DeepSeek-R1) to a specialized code model (Qwen2.5-Coder):

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Metric
     - DeepSeek-R1
     - Qwen2.5-Coder
     - Improvement
   * - Mean Latency
     - 27.7s
     - 2.6s
     - **10.6x faster**
   * - Median Latency
     - 19.3s
     - 3.0s
     - 6.4x faster
   * - Best Case
     - 12.8s
     - 396ms
     - 32x faster
   * - Worst Case
     - 1049s
     - 3.7s
     - 283x faster
   * - Success Rate
     - 100%
     - 100%
     - ✅ Maintained

**Quality Scores:**

- Mean: 77% (high-quality)
- Range: 65-85% across test scenarios
- Syntax: 92% correctness
- Context relevance: 81%
- Completeness: 72%

Real-World Examples
-------------------

See ``ada.nvim/COMPLETION_QUICKSTART.md`` for 13 detailed examples including:

- Python function completion
- JavaScript async/await
- Lua Neovim configs
- Error handling patterns
- Loop completion
- Class methods
- And more!

Troubleshooting
===============

Completion Not Appearing
-------------------------

**Check Ada is running:**

.. code-block:: bash

   curl http://localhost:7000/v1/healthz

**Check model is installed:**

.. code-block:: bash

   ollama list | grep qwen2.5-coder

**Check Neovim logs:**

.. code-block:: vim

   :messages

Slow Completions
----------------

**Use smaller model:**

.. code-block:: bash

   ollama pull qwen2.5-coder:3b

Update config:

.. code-block:: lua

   completion = {
     model = "qwen2.5-coder:3b",
   }

**Check GPU:**

.. code-block:: bash

   ollama ps  # Should show GPU usage

See :doc:`hardware` for GPU setup.

Poor Quality Completions
-------------------------

**Use larger model:**

.. code-block:: bash

   ollama pull qwen2.5-coder:14b

**Check context:**

Make sure you have meaningful code before and after the cursor. Completion works best with:

- Clear function signatures
- Established patterns in surrounding code
- Comments describing intent

**Adjust temperature:**

.. code-block:: lua

   completion = {
     temperature = 0.1,  -- More focused (default 0.2)
   }

Error: MCP Tool Not Found
--------------------------

**Reinstall MCP tools:**

.. code-block:: bash

   cd ~/Code/ada-v1/ada-mcp
   npm install
   npm run build

**Check MCP config:**

Verify ``ada-mcp`` is in your editor's MCP settings.

Comparison to Copilot
======================

**What's Similar:**

- Context-aware completion
- Multi-language support
- Inline suggestions
- Quality and speed (with right model)

**What's Different:**

- **Fully local** - No cloud dependencies, runs on your hardware
- **Privacy-first** - Your code never leaves your machine
- **Free** - No subscription ($0 vs $10-20/month)
- **Hackable** - Modify behavior, swap models, add features
- **Transparent** - See exactly how it works

**Trade-offs:**

- Requires local compute (GPU recommended)
- Needs model download (4.7GB for qwen2.5-coder:7b)
- Slightly slower on CPU (use GPU for best performance)
- Quality depends on model choice (but very competitive!)

Next Steps
==========

- **Try different models** - Experiment with qwen2.5-coder variants
- **Build custom prompts** - Modify FIM format for your use case
- **Add to CI/CD** - Use Ada for code review automation
- **Extend MCP tools** - Add refactoring, documentation generation, etc.

See :doc:`development` for contributing!

Related Documentation
=====================

- :doc:`neovim_integration` - Full Neovim setup guide
- :doc:`hardware` - GPU setup for best performance
- :doc:`api_reference` - MCP tools documentation
- `ada.nvim/COMPLETION_QUICKSTART.md <../ada.nvim/COMPLETION_QUICKSTART.md>`_ - Quick reference
- `benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md <../benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md>`_ - Complete analysis
