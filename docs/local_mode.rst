==================================
Running Ada Locally (No Docker!)
==================================

Ada now supports running entirely locally without Docker! This is the **recommended** deployment mode for most users.

Quick Start
===========

Prerequisites
-------------

1. **Python 3.13+**

   .. code-block:: bash

      python3 --version  # Should show 3.13 or higher

2. **Ollama** (for LLM inference)

   .. code-block:: bash

      # Install from https://ollama.ai
      curl -fsSL https://ollama.com/install.sh | sh
      
      # Start Ollama
      ollama serve
      
      # Pull a model
      ollama pull qwen2.5-coder:7b

Installation
------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/luna-system/ada.git
   cd ada

   # Run setup wizard
   python3 ada_main.py setup

   # Or manual setup:
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   cp .env.example .env

Running Ada
-----------

.. code-block:: bash

   # Activate virtual environment
   source .venv/bin/activate

   # Start Ada (auto-detects local Ollama)
   ada run

   # Or explicitly use local mode
   ada run --local

   # Development mode (hot reload)
   ada run --local --dev

Ada will:

✅ Detect your local Ollama installation  
✅ Use embedded ChromaDB (no separate database process)  
✅ Start the brain API on http://localhost:7000  
✅ Store all data in ``./data/`` directory

Quick Commands
--------------

.. code-block:: bash

   # Check system health
   ada doctor

   # View running services
   ada status

   # Chat directly from terminal
   ada chat "What's the weather today?"

   # Stop Ada
   ada stop

Architecture: Local Mode
=========================

.. code-block:: text

   Terminal               Local Ollama (port 11434)
      │                           │
      ├─ ada run ────────────────┤
      │                           │
      └─ Brain API ───────────────┘
         (port 7000)               
            │
            └─ Embedded ChromaDB
               (./data/chroma/)

**No Docker containers!** Everything runs as local processes.

Comparison: Local vs Docker
============================

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - Local Mode
     - Docker Mode
   * - **Setup Time**
     - < 5 minutes
     - 10-15 minutes
   * - **Memory Usage**
     - ~2GB (Ollama + Brain)
     - ~4GB (all containers)
   * - **Startup Time**
     - < 5 seconds
     - ~30 seconds
   * - **Model Storage**
     - Single copy
     - Separate container volume
   * - **GPU Support**
     - Native (CUDA/ROCm/Metal)
     - Requires GPU passthrough
   * - **Development**
     - Hot reload built-in
     - Requires rebuild
   * - **Portability**
     - Requires Python/Ollama
     - Requires Docker
   * - **Data Backup**
     - Simple ``./data/`` folder
     - Container volumes

**Recommendation:** Use local mode unless you need multi-service orchestration.

Configuration
=============

.env for Local Mode
-------------------

.. code-block:: bash

   # Minimal local configuration
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5-coder:7b
   CHROMA_MODE=embedded
   DATA_DIR=./data

Advanced Options
----------------

.. code-block:: bash

   # Use different port
   ada run --local --port 8080

   # Bind to specific interface
   ada run --local --host 127.0.0.1

   # Development mode (auto-reload)
   ada run --local --dev

Features
========

All Ada features work in local mode:

✅ **RAG (Retrieval-Augmented Generation)** - Embedded ChromaDB  
✅ **Conversation Memory** - Stored in ``./data/chroma/``  
✅ **Streaming Responses** - Full SSE support  
✅ **Specialists** - All specialists work (OCR, web search, wiki, etc.)  
✅ **Matrix Bridge** - Can connect to local brain  
✅ **CLI Adapter** - Works out of the box  
✅ **Web UI** - Use nginx proxy or run Astro dev server

**What requires Docker:**

❌ **Web UI** (nginx) - Optional, can use Astro dev server instead  
❌ **Matrix Bridge** - Optional, requires containerized setup  
❌ **Automated backups** - Optional maintenance scripts

Accessing the API
=================

From Browser
------------

.. code-block:: text

   http://localhost:7000/v1/healthz

Using ada-cli
-------------

.. code-block:: bash

   # Interactive mode
   ada-cli

   # One-shot query
   ada-cli "Tell me about Python"

   # JSON output
   ada-cli --json "List 3 facts about Mars"

Using curl
----------

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Hello Ada!"}' \
     --no-buffer

Data Management
===============

Data Directory Structure
------------------------

.. code-block:: text

   ./data/
   ├── chroma/           # Embedded vector database
   │   ├── personas/     # Persona documents
   │   ├── faqs/         # FAQ collection
   │   ├── memories/     # Long-term memories
   │   └── turns/        # Conversation history
   ├── brain/            # Brain service data
   │   ├── notices.json  # System notifications
   │   └── uploads/      # Uploaded files
   └── backups/          # Optional manual backups

Backing Up
----------

.. code-block:: bash

   # Simple backup
   tar -czf ada-backup-$(date +%Y%m%d).tar.gz data/

   # Restore
   tar -xzf ada-backup-20250116.tar.gz

Migrating from Docker
---------------------

.. code-block:: bash

   # 1. Stop Docker services
   docker compose down

   # 2. Copy data from Docker volumes
   docker run --rm -v ada-v1_chroma-data:/data -v $(pwd)/data:/backup \
     alpine tar -czf /backup/chroma.tar.gz -C /data .

   # 3. Extract to local data directory
   mkdir -p data/chroma
   tar -xzf data/chroma.tar.gz -C data/chroma/

   # 4. Update .env for local mode
   cp .env.example .env
   # Edit .env - use local mode configuration

   # 5. Start local mode
   ada run --local

Troubleshooting
===============

"Ollama not running"
--------------------

**Solution:**

.. code-block:: bash

   # Check if Ollama is running
   curl http://localhost:11434/api/tags

   # If not, start it
   ollama serve

   # Check if model is available
   ollama list
   ollama pull qwen2.5-coder:7b  # If model missing

"ModuleNotFoundError: No module named 'brain'"
----------------------------------------------

**Solution:**

.. code-block:: bash

   # Ensure you're in virtual environment
   source .venv/bin/activate

   # Reinstall in editable mode
   pip install -e .

   # Verify installation
   ada --version

"Port 7000 already in use"
--------------------------

**Solution:**

.. code-block:: bash

   # Find process using port
   lsof -i :7000

   # Kill it
   kill -9 <PID>

   # Or use different port
   ada run --local --port 8000

"Permission denied: ./data/chroma"
----------------------------------

**Solution:**

.. code-block:: bash

   # Fix permissions
   chmod -R 755 data/

Ollama connection refused from brain
------------------------------------

**Issue:** Brain can't reach Ollama even though it's running.

**Solution:**

.. code-block:: bash

   # Check Ollama is listening on all interfaces (not just 127.0.0.1)
   ss -tlnp | grep 11434

   # If only on 127.0.0.1, restart with:
   OLLAMA_HOST=0.0.0.0:11434 ollama serve

ChromaDB errors
---------------

**Solution:**

.. code-block:: bash

   # Clear ChromaDB data (WARNING: loses history!)
   rm -rf data/chroma/

   # Restart Ada
   ada run --local

Performance Tips
================

Memory Optimization
-------------------

.. code-block:: bash

   # Use smaller model for faster responses
   ada run --local
   # Edit .env: OLLAMA_MODEL=qwen2.5-coder:3b

   # Reduce context window
   RAG_TURN_TOP_K=2
   RAG_MEMORY_TOP_K=1

CPU-Only Performance
--------------------

If you don't have a GPU, use optimized models:

.. code-block:: bash

   ollama pull qwen2.5-coder:3b
   OLLAMA_MODEL=qwen2.5-coder:3b ada run --local

GPU Acceleration
----------------

Ada automatically uses GPU if available:

- **NVIDIA**: CUDA toolkit (automatically detected by Ollama)
- **AMD**: ROCm (Linux only)
- **Apple**: Metal (macOS M1/M2/M3/M4)

No configuration needed - Ollama handles it!

Development Workflow
====================

Hot Reload
----------

.. code-block:: bash

   # Start in development mode
   ada run --local --dev

   # Edit brain/*.py files
   # Changes apply immediately (no restart needed)

Running Tests
-------------

.. code-block:: bash

   # Unit tests
   pytest tests/

   # Integration tests (requires brain running)
   ada run --local &
   pytest tests/test_integration.py

Adding Specialists
------------------

.. code-block:: bash

   # 1. Create specialist
   vim brain/specialists/my_specialist.py

   # 2. Register in __init__.py
   vim brain/specialists/__init__.py

   # 3. Restart brain (dev mode auto-reloads)
   # Changes take effect immediately

Hybrid Setups
=============

Local Brain + Docker Services
------------------------------

Run brain locally but use Docker for optional services:

.. code-block:: bash

   # Start only web UI and matrix bridge
   docker compose up -d frontend matrix-bridge

   # Run brain locally
   ada run --local

   # Access web UI at http://localhost:5000

Local Development + Docker Ollama
----------------------------------

Use Docker for Ollama isolation:

.. code-block:: bash

   # Start Ollama in Docker
   docker compose up -d ollama

   # Run brain locally pointing to Docker Ollama
   OLLAMA_BASE_URL=http://localhost:11434 ada run --local

Next Steps
==========

- **Web UI:** See :doc:`adapters` for Astro dev server
- **Matrix Bot:** See ``matrix-bridge/QUICKSTART.md``
- **Custom Persona:** Edit ``persona.md`` and restart
- **Specialists:** See :doc:`specialists`

Why Local Mode?
===============

Benefits
--------

1. **Faster startup** - No container orchestration
2. **Less memory** - One Ollama instance shared across tools
3. **Native GPU** - Direct hardware access, no passthrough
4. **Easier development** - Hot reload, native debugging
5. **Simpler backups** - Just copy ``./data/`` folder
6. **Lower disk usage** - No duplicate model storage

When to use Docker instead
--------------------------

- **Production deployment** with multiple services
- **Isolated environments** (testing, CI/CD)
- **Teams** sharing consistent setup
- **Remote deployment** without shell access
