================
Ada Log Intelligence
================

**Biomimetic log analysis for kids and DevOps!** (v2.7+)

Ada understands log files using the same cognitive architecture as her memory system. Explain Minecraft crashes to kids OR compress production logs 100:1 for DevOps - same underlying intelligence.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Overview
========

**What You Get:**

- **Kid-friendly Minecraft crash explanations** - "OptiFine and Sodium are fighting!"
- **Pattern matching for common errors** - OptiFine conflicts, OutOfMemory, mod issues
- **Foundation for 100:1 log compression** - Using importance scoring from v2.2 research
- **Extensible parser system** - JSON logs, syslog, custom formats
- **Standalone library** - Use outside of Ada (``pip install ada-logs``)

**Philosophy:**

Logs are just another form of memory. Apply the same biomimetic importance scoring:

- **Surprise** - Novel errors matter more than repeated warnings
- **Relevance** - Crashes more important than debug messages
- **Temporal decay** - Recent errors matter more
- **Habituation** - Filter noise from repetitive log spam

Quick Start
===========

Option 1: Standalone Library
-----------------------------

.. code-block:: bash

   # Install standalone package
   pip install ada-logs

   # Analyze a Minecraft crash
   ada-logs analyze crash-2024-12-19.log --for-kids

   # Get machine-readable output
   ada-logs analyze crash.log --format json

Option 2: Within Ada
--------------------

1. **Upload a .log file** to Ada (Web UI or API)
2. **LogAnalysisSpecialist auto-activates**
3. **Get conversational explanation**

.. code-block:: python

   # Via Python API
   import requests
   
   files = {'file': open('minecraft-crash.log', 'rb')}
   response = requests.post(
       'http://localhost:7000/v1/chat/stream',
       data={'message': 'Explain this crash'},
       files=files
   )

Features
========

Minecraft Crash Analysis
-------------------------

**What It Does:**

- **Detects Minecraft crashes automatically** - Recognizes crash report format
- **Parses Java exceptions** - Stack traces, error messages, mod lists
- **Identifies common patterns** - OptiFine conflicts, OutOfMemory, missing mods
- **Kid-friendly explanations** - No jargon, clear metaphors
- **Fix suggestions** - Step-by-step remediation

**Example Output:**

.. code-block:: text

   🎮 MINECRAFT CRASH ANALYSIS

   **What Happened:** OptiFine and Sodium are fighting!

   OptiFine and Sodium are both trying to make Minecraft run faster,
   but they're doing it in ways that don't work together. It's like
   two people trying to steer the same car at the same time!

   **How to Fix:**
   1. Remove OptiFine from your mods folder
      OR
   2. Remove Sodium from your mods folder
   
   Pick ONE performance mod, not both.

   **Difficulty:** Easy ⭐
   **Estimated Time:** 2 minutes

**Pattern Detection:**

- ``OptiFine + Sodium conflict`` - Most common Minecraft crash
- ``OutOfMemoryError`` - Need to allocate more RAM
- ``Mod X requires Mod Y`` - Missing dependency
- ``NullPointerException`` - Bug in mod code
- ``ClassNotFoundException`` - Mod not loaded correctly

Biomimetic Compression
----------------------

**The Insight:**

Production logs have millions of lines. Most are noise. Apply Ada's importance scoring:

- **Surprise (60%)** - New errors are important
- **Relevance (20%)** - Crashes > warnings > debug
- **Temporal decay (10%)** - Recent matters more
- **Habituation (10%)** - Repeated logs lose importance

**Result:** 100:1 compression with preserved signal.

**Example:**

.. code-block:: text

   # Before (10,000 lines)
   [DEBUG] Request processed: 200 OK (x9,847)
   [WARN] Slow query: 1.2s (x142)
   [ERROR] Database connection failed (x1)
   [WARN] Slow query: 1.3s (x10)

   # After (100 lines) - Importance-weighted
   [ERROR] Database connection failed (SURPRISE: 0.95)
   [WARN] Slow query: 1.2s (SURPRISE: 0.62, COUNT: 152)
   [DEBUG] Request processed: 200 OK (omitted x9,847)

**Status:** Foundation implemented (v2.7), full compression coming in future release.

Conversational Analysis
-----------------------

Upload logs to Ada and chat about them:

.. code-block:: text

   User: [uploads minecraft-crash.log]
   
   Ada: I found a Minecraft crash! It looks like OptiFine and 
        Sodium are conflicting. This is really common - both 
        mods try to optimize rendering but in incompatible ways.
        
        Want me to explain more about what's happening?
   
   User: Yes, and how do I fix it?
   
   Ada: Here's what to do:
   
        1. Open your mods folder (.minecraft/mods)
        2. Find OptiFine-*.jar and delete it
           OR find Sodium-*.jar and delete it
        3. Start Minecraft again
        
        You only need ONE performance mod. I recommend Sodium 
        because it's faster on modern computers, but OptiFine
        has more features (shaders, zoom, connected textures).
        
        Pick based on what you need!

Usage Examples
==============

Command Line
------------

**Basic Analysis:**

.. code-block:: bash

   ada-logs analyze crash.log

**Kid-Friendly Mode:**

.. code-block:: bash

   ada-logs analyze crash.log --for-kids

**JSON Output:**

.. code-block:: bash

   ada-logs analyze crash.log --format json > analysis.json

**Pattern Detection:**

.. code-block:: bash

   ada-logs patterns crash.log

Python API
----------

.. code-block:: python

   from ada_logs import MinecraftParser
   
   parser = MinecraftParser()
   
   with open('crash.log') as f:
       result = parser.parse(f.read())
   
   if result.patterns:
       print(f"Found {len(result.patterns)} issues:")
       for pattern in result.patterns:
           print(f"  - {pattern.name}: {pattern.description}")
           if pattern.kid_friendly:
               print(f"    Kid explanation: {pattern.kid_friendly}")
           print(f"    How to fix: {pattern.fix}")

Within Ada
----------

**Upload via Web UI:**

1. Go to http://localhost:5000
2. Click "Upload File"
3. Select your .log file
4. LogAnalysisSpecialist auto-activates
5. Chat about the crash!

**Upload via API:**

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/chat/stream \
     -F "message=Explain this crash" \
     -F "file=@crash.log"

Architecture
============

How It Works
------------

**1. Pattern Matching:**

.. code-block:: python

   PATTERNS = [
       {
           'name': 'OptiFine + Sodium Conflict',
           'regex': r'(optifine|sodium).*mixin.*conflict',
           'severity': 'ERROR',
           'kid_friendly': 'OptiFine and Sodium are fighting!',
       },
       # ... more patterns
   ]

**2. Log Parsing:**

- Detect format (Minecraft, JSON, syslog, generic)
- Extract timestamps, log levels, messages
- Build structured representation

**3. Importance Scoring:**

- **Surprise:** Is this error new or repeated?
- **Relevance:** ERROR > WARN > INFO > DEBUG
- **Context:** Stack traces increase importance
- **Temporal:** Recent logs weighted higher

**4. Explanation Generation:**

- Match patterns to detected issues
- Select kid-friendly vs technical explanation
- Generate fix steps based on severity

**5. Compression (Future):**

- Group similar log lines
- Score importance using biomimetic signals
- Keep top N% by importance
- Emit compressed log with metadata

Design Philosophy
-----------------

**Inspired by v2.2 Memory Research:**

Ada's memory system learned that **surprise matters more than recency**. Logs are the same:

- A new ERROR is more important than the 1000th DEBUG message
- A surprising pattern (OptiFine + Sodium) more important than routine startup logs
- Temporal context helps (recent crashes matter) but novelty dominates

**Same cognitive architecture, different domain.**

Extending the Parser
====================

Add Custom Patterns
-------------------

.. code-block:: python

   from ada_logs import MinecraftParser
   
   parser = MinecraftParser()
   
   # Add your pattern
   parser.add_pattern({
       'name': 'MyMod Crash',
       'regex': r'MyMod.*NullPointerException',
       'severity': 'ERROR',
       'kid_friendly': 'MyMod has a bug!',
       'fix': 'Update MyMod to the latest version',
       'difficulty': 'Easy',
   })
   
   result = parser.parse(log_content)

Create New Parser
-----------------

.. code-block:: python

   from ada_logs.parsers.base import BaseParser
   
   class ApacheParser(BaseParser):
       def can_parse(self, content: str) -> bool:
           return 'Apache' in content
       
       def parse(self, content: str) -> ParseResult:
           # Your parsing logic
           return ParseResult(
               format='apache',
               timestamp=...,
               errors=[...],
               patterns=[...],
           )

Register in Ada
---------------

.. code-block:: python

   # brain/specialists/log_analysis_specialist.py
   
   from ada_logs.parsers import MinecraftParser, ApacheParser
   
   PARSERS = [
       MinecraftParser(),
       ApacheParser(),  # Your new parser!
       # ... more parsers
   ]

Configuration
=============

Standalone Library
------------------

.. code-block:: python

   from ada_logs import Config
   
   config = Config(
       kid_friendly_default=True,
       max_patterns=10,
       importance_threshold=0.5,
       compression_ratio=100,  # 100:1 compression target
   )
   
   parser = MinecraftParser(config=config)

Within Ada
----------

.. code-block:: bash

   # .env file
   LOG_ANALYSIS_ENABLED=true
   LOG_ANALYSIS_KID_MODE=true
   LOG_ANALYSIS_MAX_PATTERNS=10

Via Specialist Config
---------------------

.. code-block:: python

   # brain/config.py
   
   class Config(BaseSettings):
       log_analysis_enabled: bool = True
       log_analysis_kid_mode: bool = True
       log_analysis_compression_ratio: int = 100

Research Foundation
===================

v2.2 Importance Scoring
-----------------------

Ada Log Intelligence uses the research-validated importance weights from v2.2:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Signal
     - Weight
     - Application to Logs
   * - Surprise
     - 0.60
     - Novel errors, first occurrence of pattern
   * - Relevance
     - 0.20
     - ERROR > WARN > INFO > DEBUG
   * - Temporal Decay
     - 0.10
     - Recent logs slightly more important
   * - Habituation
     - 0.10
     - Repeated warnings lose importance

**Validated by:**

- 80 tests (property-based, synthetic, production)
- +6.5% improvement on real conversation data
- Published research in ``.ai/explorations/``

**See:** ``RELEASE_v2.2.0.md`` for complete research details.

Future Roadmap
==============

**v2.7 (Current):**

- ✅ Minecraft crash parser
- ✅ Pattern matching system
- ✅ Kid-friendly explanations
- ✅ Standalone ``ada-logs`` package
- ✅ LogAnalysisSpecialist for Ada

**v2.8+ (Planned):**

- 🚧 Full 100:1 log compression
- 🚧 JSON log parser (common in microservices)
- 🚧 Syslog parser (Linux system logs)
- 🚧 Custom format builder (regex-based)
- 🚧 Real-time log streaming analysis
- 🚧 Alert generation from importance spikes
- 🚧 Multi-file correlation (trace requests across services)

Troubleshooting
===============

Parser Not Detecting Format
----------------------------

**Check log format:**

.. code-block:: bash

   head -20 crash.log

Minecraft logs should start with:

.. code-block:: text

   ---- Minecraft Crash Report ----
   // There are four lights!

**Force format:**

.. code-block:: bash

   ada-logs analyze crash.log --format minecraft

Pattern Not Matching
--------------------

**Check pattern regex:**

.. code-block:: python

   import re
   pattern = r'optifine.*sodium'
   with open('crash.log') as f:
       if re.search(pattern, f.read(), re.IGNORECASE):
           print("Pattern matches!")

**Enable debug mode:**

.. code-block:: bash

   ada-logs analyze crash.log --debug

Related Documentation
=====================

- :doc:`specialists` - Specialist system overview
- :doc:`biomimetic_features` - v2.2 memory research
- `RELEASE_v2.7.0.md <../RELEASE_v2.7.0.md>`_ - Complete feature documentation
- `ada-logs/ <../ada-logs/>`_ - Standalone library source code
