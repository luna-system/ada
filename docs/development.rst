Development Tools
=================

This guide covers Ada's utility scripts, the scripts tooling container, and development workflows.

Scripts Tooling Container
--------------------------

Overview
~~~~~~~~

All utility scripts should be run via the dedicated ``scripts`` Docker service, which provides:

- Consistent Python environment (same as brain service)
- All dependencies pre-installed
- Network access to chroma, ollama, etc.
- Proper module imports (brain, rag modules available)

Why Use the Container?
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Running scripts directly on host causes issues:

- ❌ Different Python versions
- ❌ Missing dependencies
- ❌ Can't reach Docker services (chroma, ollama)
- ❌ Import errors (can't find brain/rag modules)
- ❌ Environment variable mismatches

**Solution**: Scripts container provides:

- ✅ Same Python 3.13 as brain
- ✅ All dependencies from pyproject.toml
- ✅ Network access via Docker Compose
- ✅ Clean imports with PYTHONPATH set
- ✅ Consistent environment variables

Usage Pattern
~~~~~~~~~~~~~

Quick Way (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Use the convenience wrapper
   ./scripts/run.sh health          # Run health check
   ./scripts/run.sh test            # Run test suite
   ./scripts/run.sh migrate         # Run migration (with confirmation)
   ./scripts/run.sh consolidate     # Run consolidation
   ./scripts/run.sh shell           # Interactive Python shell
   ./scripts/run.sh bash            # Bash shell in container
   ./scripts/run.sh my_script.py    # Run custom script

Direct Way (Full Control)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Run any script directly
   docker compose run --rm scripts python /app/scripts/<script_name>.py

   # Examples
   docker compose run --rm scripts python /app/scripts/health_check_chroma.py
   docker compose run --rm scripts python /app/scripts/migrate_chroma_http.py

Available Scripts
-----------------

Health & Testing
~~~~~~~~~~~~~~~~

Pytest Test Suite
^^^^^^^^^^^^^^^^^

Modern test suite using pytest with fixtures and better reporting.

.. code-block:: bash

   # Run all tests
   ./scripts/run.sh test
   # Or directly:
   docker compose run --rm scripts pytest

   # Run specific test file
   docker compose run --rm scripts pytest tests/test_rag.py

   # Run with more verbosity
   docker compose run --rm scripts pytest -vv

   # Run only tests matching a pattern
   docker compose run --rm scripts pytest -k "memory"

   # Skip slow tests
   docker compose run --rm scripts pytest -m "not slow"

**Test files:**

- ``tests/test_rag.py`` - RAG store retrieval tests
- ``tests/test_prompt_builder.py`` - Prompt building tests
- ``tests/test_specialists.py`` - Specialist system tests

Health Check Script
^^^^^^^^^^^^^^^^^^^

Comprehensive health check for Chroma database and RAG system (operational tool, not a test).

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/health_check_chroma.py

**Checks:**

- Chroma server connectivity
- Collection existence and document count
- Embedding generation
- Memory/FAQ/turn query functionality
- Specialist docs retrieval
- Query consistency
- Persona loading

**Exit codes:** 0 (healthy), 1 (unhealthy)

Data Management
~~~~~~~~~~~~~~~

Migrate Chroma Collection
^^^^^^^^^^^^^^^^^^^^^^^^^^

Migrate Chroma collection to HTTP-compatible format with fresh embeddings.

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/migrate_chroma_http.py

**What it does:**

- Backs up existing collection
- Deletes old collection
- Creates fresh collection
- Re-generates embeddings for all documents
- Verifies query functionality

**When to use:**

- After upgrading Chroma
- When queries return unexpected results
- When switching from embedded to HTTP mode

Import FAQ
^^^^^^^^^^

Import FAQs from JSONL file into Chroma.

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/import_faq.py

Import Conversation Turns
^^^^^^^^^^^^^^^^^^^^^^^^^^

Import conversation turns from CSV into Chroma.

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/import_turns_csv.py

Load Persona
^^^^^^^^^^^^

Load persona from markdown file into Chroma.

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/load_persona.py

Consolidate Memories
^^^^^^^^^^^^^^^^^^^^^

Run nightly memory consolidation (creates daily/weekly summaries).

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/consolidate_memories.py

.. note::
   This runs automatically via ``memory-consolidation`` service at 02:00 UTC.

Backup Management
~~~~~~~~~~~~~~~~~

Upload Backups to B2
^^^^^^^^^^^^^^^^^^^^

Upload Chroma backups to Backblaze B2.

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/upload_backups_b2.py

.. note::
   This runs automatically via ``sqlite-backup`` service hourly.

Development Patterns
--------------------

Similar Tools in Other Ecosystems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This pattern is well-established in containerized development:

- **Rails**: ``docker compose run --rm web bin/rails console``
- **Django**: ``docker compose run --rm web python manage.py shell``
- **Node.js**: ``docker compose run --rm node npm test``
- **Kubernetes**: Init containers for migrations/setup

When to Use the Scripts Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

✅ **Use the scripts container for:**

- Running health checks
- Running tests
- Database migrations
- Data imports/exports
- One-off maintenance tasks
- Interactive debugging

❌ **Don't use for:**

- Running the main application (use ``brain`` service)
- Anything that needs to stay running (use a regular service)

Running Tests in CI/CD
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .gitlab-ci.yml / .github/workflows/test.yml
   test:
     script:
       - docker compose run --rm scripts pytest
       - docker compose run --rm scripts python /app/scripts/health_check_chroma.py

Pre-Deployment Health Check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # pre-deploy.sh
   docker compose run --rm scripts python /app/scripts/health_check_chroma.py
   if [ $? -eq 0 ]; then
     echo "Health check passed, proceeding with deployment"
     docker compose up -d
   else
     echo "Health check failed, aborting deployment"
     exit 1
   fi

Interactive Debugging
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start an interactive Python session with all dependencies
   docker compose run --rm scripts python

   # Then in Python:
   >>> from brain.rag_store import RagStore
   >>> store = RagStore()
   >>> results = store.retrieve_memories("test query", k=5)
   >>> print(results)

Adding New Scripts
~~~~~~~~~~~~~~~~~~

1. Create script in ``scripts/`` directory
2. Import brain/rag modules as needed:

   .. code-block:: python

      from brain.rag_store import RagStore
      from brain import config

3. Run via scripts container:

   .. code-block:: bash

      docker compose run --rm scripts python /app/scripts/new_script.py

No rebuild needed! Scripts are mounted as volumes.

Troubleshooting
---------------

Script Not Found
~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: bash

   docker compose run --rm scripts python /app/scripts/my_script.py
   # Error: No such file

**Solution:** Check that script exists in ``scripts/`` directory. Path should be ``/app/scripts/``, not ``./scripts/``.

Import Errors
~~~~~~~~~~~~~

**Problem:**

.. code-block:: text

   ModuleNotFoundError: No module named 'brain'

**Solution:** Use the scripts container, not host Python. The PYTHONPATH is set correctly in the container.

Can't Reach Chroma/Ollama
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: text

   httpx.ConnectError: [Errno 111] Connection refused

**Solution:**

1. Ensure services are running: ``docker compose ps``
2. Use service names (chroma, ollama), not localhost
3. Check environment variables: ``CHROMA_URL=http://chroma:8000``

Permission Errors
~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: text

   PermissionError: [Errno 13] Permission denied

**Solution:** Scripts are mounted read-write. Check file permissions on host or run with appropriate user.

Architecture
------------

Container Configuration
~~~~~~~~~~~~~~~~~~~~~~~

The scripts service is defined in ``compose.yaml`` with:

- **Base:** ``scripts/Dockerfile`` (Python 3.13-slim)
- **Profile:** ``tools`` (not started by default)
- **Dependencies:** brain, rag, scripts directories mounted
- **Environment:** Same as brain service
- **Network:** Can reach chroma, ollama by service name
- **No ports:** Not a server, just a runner

Dockerfile Structure
~~~~~~~~~~~~~~~~~~~~

``scripts/Dockerfile`` includes:

.. code-block:: dockerfile

   FROM python:3.13-slim
   
   # Install uv package manager
   RUN pip install --no-cache-dir uv
   
   # Copy project files
   COPY pyproject.toml uv.lock ./
   COPY brain/ /app/brain/
   COPY scripts/ /app/scripts/
   COPY tests/ /app/tests/
   
   # Install dependencies (including dev extras)
   RUN uv venv && uv sync --frozen --extra dev
   
   # Set PATH and PYTHONPATH
   ENV PATH="/app/.venv/bin:${PATH}"
   ENV PYTHONPATH="/app:/app/brain"
   
   WORKDIR /app

Volume Mounts
~~~~~~~~~~~~~

Scripts and tests are volume-mounted for live updates:

.. code-block:: yaml

   volumes:
     - ./brain:/app/brain:ro
     - ./scripts:/app/scripts
     - ./tests:/app/tests
     - ./seed:/app/seed:ro
     - ./persona.md:/app/persona.md:ro
     - ./data:/data

This means you can edit scripts/tests without rebuilding the container.

Best Practices
--------------

1. **Always use scripts container:** Consistent environment
2. **Exit codes matter:** Scripts should return 0 (success) or 1 (failure)
3. **Log to stdout:** Docker captures logs automatically
4. **Handle errors gracefully:** Use try/except, print clear error messages
5. **Document usage:** Add script to this documentation with description
6. **Test in container:** Don't rely on host Python working
7. **Use fixtures:** Share common setup in ``tests/conftest.py``
8. **Version control:** Commit scripts and tests to git

Development Workflow
--------------------

Typical Development Cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start services:**

   .. code-block:: bash

      docker compose up -d

2. **Make changes to code**

3. **Run tests:**

   .. code-block:: bash

      ./scripts/run.sh test

4. **Health check:**

   .. code-block:: bash

      ./scripts/run.sh health

5. **Debug if needed:**

   .. code-block:: bash

      ./scripts/run.sh shell

6. **Commit and push**

Adding New Features
~~~~~~~~~~~~~~~~~~~

1. **Write the feature code**
2. **Add tests** in ``tests/test_<feature>.py``
3. **Run tests** to verify: ``./scripts/run.sh test``
4. **Add documentation** to Sphinx docs
5. **Update CHANGELOG** (if applicable)
6. **Create pull request**

Debugging Issues
~~~~~~~~~~~~~~~~

1. **Check logs:**

   .. code-block:: bash

      docker compose logs brain
      docker compose logs chroma

2. **Interactive debugging:**

   .. code-block:: bash

      ./scripts/run.sh shell

3. **Health check:**

   .. code-block:: bash

      ./scripts/run.sh health

4. **Test specific component:**

   .. code-block:: bash

      docker compose run --rm scripts pytest tests/test_rag.py -vv

Code Quality
------------

Linting and Formatting
~~~~~~~~~~~~~~~~~~~~~~~

(Future) Add code quality tools:

.. code-block:: bash

   # Format code
   docker compose run --rm scripts black brain/ scripts/
   
   # Lint code
   docker compose run --rm scripts ruff brain/ scripts/
   
   # Type checking
   docker compose run --rm scripts mypy brain/

Pre-commit Hooks
~~~~~~~~~~~~~~~~

(Future) Set up pre-commit hooks:

.. code-block:: yaml

   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.1.0
       hooks:
         - id: black
     - repo: https://github.com/charliermarsh/ruff-pre-commit
       rev: v0.0.260
       hooks:
         - id: ruff

Resources
---------

- See :doc:`testing` for comprehensive testing guide
- See :doc:`api_usage` for API documentation
- See :doc:`api_reference` for code-level API reference
- `Docker Compose Documentation <https://docs.docker.com/compose/>`_
- `uv Package Manager <https://github.com/astral-sh/uv>`_
