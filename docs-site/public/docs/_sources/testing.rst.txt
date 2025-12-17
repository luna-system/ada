Testing Guide
=============

This guide covers testing Ada's Brain service, including manual testing, automated tests with pytest, and API endpoint testing.

For API endpoint documentation, see :doc:`api_reference`. For configuration options, see :doc:`configuration`. For architecture overview, see :doc:`architecture`.

Running Services for Testing
-----------------------------

Option 1: Using Docker Compose (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   docker compose up

Then open the UI in your browser at ``http://localhost:5000/``.

Option 2: Local Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If testing the FastAPI backend directly without Docker:

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   source .venv/bin/activate
   python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000

The API will be available at ``http://localhost:7000/v1/*`` with interactive docs at ``http://localhost:7000/docs``.

Manual Testing
--------------

Testing Markdown Rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the frontend running (via Docker Compose or local dev server):

1. Try these messages in the chat composer and submit (note: inline markdown is rendered; block-level markdown/code fences are rendered with syntax highlighting):

   - Hello **bold** text
   - *italic* and **bold** together
   - A link: `OpenAI <https://openai.com>`_
   - Inline code: ``const a = 1;``
   - Code block:

   .. code-block:: js

      function test() {
        return 42;
      }

2. Verify:

   - Messages render with bold/italic/links/inline code formatting
   - Links open in a new tab and have ``rel="noopener noreferrer"`` set
   - Code fences (```...```) render with a monospace, sanitized ``<pre><code>`` block and basic syntax highlighting
   - The 'Thinking' bubble (if enabled) renders inline markdown similarly
   - If markdown does not render, check the small header status next to the brand for ``marked:✓ DOMPurify:✓ hljs:✓`` — these indicate the client-side libraries loaded successfully
   - If any are missing (✕), open DevTools console to see errors and clear browser cache (or refresh with Ctrl/Cmd+Shift+R)

3. Optional: Check that the chat input and memory list still work as before.

Testing API Endpoints Directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To test API endpoints without the frontend:

.. code-block:: bash

   # Health check
   curl http://localhost:7000/v1/healthz

   # Get recent conversations
   curl http://localhost:7000/v1/conversations/recent

   # Query memory
   curl "http://localhost:7000/v1/memory?query=example"

   # Create a memory
   curl -X POST http://localhost:7000/v1/memory \
     -H "Content-Type: application/json" \
     -d '{"content": "Test memory", "memory_type": "important"}'

   # Interactive API docs
   # Open http://localhost:7000/docs in your browser

For complete endpoint documentation, see :doc:`api_reference` and :doc:`api_usage`. For code examples, see :doc:`examples`.

Testing with Frontend Proxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All API calls from the frontend go through the Nginx reverse proxy:

.. code-block:: bash

   # Same endpoints available via proxy
   curl http://localhost:5000/api/health
   curl http://localhost:5000/api/conversations/recent

   # Stream endpoint (SSE)
   curl http://localhost:5000/api/chat/stream -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "conversation_id": "test"}'

The proxy remaps ``/api/*`` → ``/v1/*`` on the brain service with proper SSE handling.

Automated Testing with Pytest
------------------------------

Ada uses a **hybrid testing approach** combining traditional example-based tests with property-based testing using **Hypothesis**. All tests are located in the ``tests/`` directory and run in a dedicated Docker container for consistency.

Test Infrastructure
~~~~~~~~~~~~~~~~~~~

The testing infrastructure includes:

- **Tests Container**: Dedicated Docker service with Python 3.13 and all dependencies
- **Pytest Configuration**: ``pytest.ini`` with sensible defaults
- **Fixtures**: Shared test fixtures in ``tests/conftest.py`` and feature-specific ``conftest.py`` files
- **Hypothesis**: Property-based testing for algorithmic correctness
- **Convenience Script**: ``scripts/run.sh`` wrapper for common test commands
- **Organized Structure**: Tests grouped by feature and type (traditional vs property-based)

Running Tests
~~~~~~~~~~~~~

Quick Way (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Run all tests
   ./scripts/run.sh test

   # Run with verbose output
   docker compose run --rm scripts pytest -vv

   # Run specific test file
   docker compose run --rm scripts pytest tests/test_rag.py

   # Run tests matching a pattern
   docker compose run --rm scripts pytest -k "memory"

   # Skip slow tests
   docker compose run --rm scripts pytest -m "not slow"

Direct Way (Full Control)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Run all tests
   docker compose run --rm scripts pytest

   # Run specific file with verbose output
   docker compose run --rm scripts pytest tests/test_prompt_builder.py -vv

   # Run only async tests
   docker compose run --rm scripts pytest -k "async"

Test Structure
~~~~~~~~~~~~~~

The test suite uses an organized directory structure:

.. code-block:: text

   tests/
     conftest.py                   # Global fixtures (rag_store, conversation_id)
     
     prompt_builder/               # Traditional example-based tests
       conftest.py                 # Shared fixtures for prompt_builder
       test_context_retriever.py   # Context retrieval from RAG (14 tests)
       test_section_builder.py     # Prompt section formatting
       test_prompt_assembler.py    # Final prompt assembly
     
     property/                     # Property-based tests (Hypothesis)
       conftest.py                 # Hypothesis configuration
       test_token_properties.py    # Token counting invariants (11 tests)
       test_memory_properties.py   # Memory decay, ranking (v2.0)
     
     test_rag.py                   # RAG store tests (6 tests)
     test_specialists.py           # Specialist system tests
     test_ai_documentation.py      # Documentation validation tests

**Traditional Tests** (example-based):
   Test specific API behavior, integration workflows, and regression cases.
   Use parametrization to reduce duplication.

**Property Tests** (Hypothesis):
   Test mathematical properties that should ALWAYS hold (bounds, monotonicity, etc.).
   Hypothesis generates 100+ random test cases automatically.

Test Types
^^^^^^^^^^

**Traditional Tests** verify specific behavior:

.. code-block:: python

   def test_context_retriever_initialization():
       """ContextRetriever initializes correctly."""
       retriever = ContextRetriever()
       assert retriever is not None
   
   @pytest.mark.parametrize("method,kwargs,expected_len", [
       ("get_memories", {"query": "test", "k": 5}, 2),
       ("get_faqs", {"query": "test", "k": 3}, 2),
   ])
   def test_retrieval_methods(retriever, method, kwargs, expected_len):
       """Test multiple similar methods with one parametrized test."""
       method = getattr(retriever, method)
       result = method(**kwargs)
       assert len(result) == expected_len

**Property Tests** verify universal invariants:

.. code-block:: python

   from hypothesis import given, strategies as st, example
   
   @given(st.text(min_size=1, max_size=10000))
   @example("🎵" * 100)  # Always test this edge case
   def test_positive_token_count(text):
       """Non-empty text ALWAYS produces positive tokens."""
       monitor = TokenBudgetMonitor()
       tokens = monitor.count_tokens(text)
       assert tokens > 0

Hypothesis will generate random inputs to try to falsify your assertions!

Adding New Tests
~~~~~~~~~~~~~~~~

**When to use which pattern:**

Traditional Tests (example-based)
   - ✅ Specific API behavior
   - ✅ Integration tests
   - ✅ Regression tests for known bugs
   - ✅ Business logic and workflows

Property Tests (Hypothesis)
   - ✅ Mathematical invariants
   - ✅ Algorithmic properties
   - ✅ Edge case discovery
   - ✅ Universal constraints

**Example: Traditional Test**

.. code-block:: python

   # tests/prompt_builder/test_my_feature.py
   import pytest
   from brain.my_module import my_function

   def test_my_feature(rag_store):
       """Test description."""
       result = my_function(rag_store)
       assert result == expected_value
       assert len(result) > 0

   @pytest.mark.parametrize("input,expected", [
       ("hello", 2),
       ("hello world", 3),
   ])
   def test_multiple_cases(input, expected):
       """Test multiple similar cases with parametrization."""
       result = my_function(input)
       assert result == expected

**Example: Property Test**

.. code-block:: python

   # tests/property/test_my_properties.py
   from hypothesis import given, strategies as st, example
   
   @given(st.text(min_size=1, max_size=1000))
   @example("edge case")  # Always test specific cases
   def test_universal_property(text):
       """This should ALWAYS be true for ANY input."""
       result = my_function(text)
       assert result > 0  # Non-empty input always produces positive result
       assert isinstance(result, int)  # Result is always an integer

No rebuild needed! Tests are volume-mounted, so you can ad
   
   # Run only property tests
   docker compose run --rm scripts pytest tests/property/
   
   # Run only traditional tests for a feature
   docker compose run --rm scripts pytest tests/prompt_builder/

Hypothesis Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

Property tests use different profiles for different environments:

.. code-block:: bash

   # Local development (100 examples, fast)
   pytest tests/property/
   
   # CI/thorough testing (1000 examples)
   HYPOTHESIS_PROFILE=ci pytest tests/property/
   
   # Debugging (10 examples, verbose)
   HYPOTHESIS_PROFILE=debug pytest tests/property/ -v

Configuration is in ``tests/property/conftest.py``.d/edit tests and run immediately.

Test Markers
^^^^^^^^^^^^

Use markers to categorize tests:

.. code-block:: python

   @pytest.mark.slow
   def test_expensive_operation():
       """This test takes a while."""
       pass

   @pytest.mark.integration
   def test_full_workflow():
       """Tests multiple components together."""
       pass

   @pytest.mark.unit
   def test_isolated_function():
       """Tests a single function."""
       pass

Run specific markers:

.. code-block:: bash

   # Skip slow tests
   docker compose run --rm scripts pytest -m "not slow"

   # Run only integration tests
   docker compose run --rm scripts pytest -m "integration"

Health Check Script
-------------------

Comprehensive health check for operational validation (not a test):

.. code-block:: bash

   ./scripts/run.sh health
   # Or directly:
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

CI/CD Integration
-----------------

The pytest infrastructure is designed for easy CI/CD integration:

GitLab CI Example
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .gitlab-ci.yml
   test:
     script:
       - docker compose build scripts
       - docker compose run --rm scripts pytest
       - docker compose run --rm scripts python /app/scripts/health_check_chroma.py

GitHub Actions Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run tests
           run: |
             docker compose build scripts
             docker compose run --rm scripts pytest
         - name: Health check
           run: docker compose run --rm scripts python /app/scripts/health_check_chroma.py

Pre-Deployment Health Check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # pre-deploy.sh
   ./scripts/run.sh health || exit 1
   ./scripts/run.sh test || exit 1
   
   if [ $? -eq 0 ]; then
     echo "All checks passed, proceeding with deployment"
     docker compose up -d
   else
     echo "Checks failed, aborting deployment"
     exit 1
   fi

Interactive Debugging
---------------------

Start an interactive Python session with all dependencies:

.. code-block:: bash

   ./scripts/run.sh shell
   # Or directly:
   docker compose run --rm scripts python

Then in Python:

.. code-block:: python

   >>> from brain.rag_store import RagStore
   >>> from brain import config
   >>> 
   >>> store = RagStore()
   >>> results = store.retrieve_memories("test query", k=5)
   >>> print(results)
   >>> 
   >>> # Test embedding generation
   >>> embedding = store.embed_text("sample text")
   >>> print(len(embedding))  # Should be 768

Test Coverage Priorities
-------------------------

Current Coverage
~~~~~~~~~~~~~~~~

✅ **Well-Covered:**

- RAG retrieval (6 tests)
- Prompt building (2 tests)
- Specialist system (1 test)

⚠️ **Needs Coverage:**

- API endpoints (streaming, non-streaming)
- Error handling (Chroma down, Ollama down)
- Edge cases (invalid input, timeouts)
- Specialist execution
- Memory consolidation

Recommended Next Tests
~~~~~~~~~~~~~~~~~~~~~~

**High Priority:**

1. API endpoint tests (~10 tests needed)

   - Test ``/v1/chat/stream`` endpoint
   - Test ``/v1/chat/completions`` endpoint
   - Test health check endpoint variations
   - Test error responses (400, 500, 503)

2. Error handling tests (~5-10 tests needed)

   - Test Chroma down scenarios
   - Test Ollama down scenarios
   - Test invalid input handling
   - Test timeout handling

**Medium Priority:**

3. Specialist system tests

   - Test specialist activation logic
   - Test specialist execution
   - Test bidirectional specialist communication

4. Memory consolidation tests

   - Test nightly consolidation logic
   - Test summary generation
   - Test memory archival

Example API Endpoint Test
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/test_api.py
   import pytest
   import httpx
   import json

   @pytest.mark.asyncio
   async def test_chat_stream_endpoint():
       """Test streaming chat endpoint."""
       async with httpx.AsyncClient() as client:
           response = await client.post(
               "http://localhost:7000/v1/chat/stream",
               json={"messages": [{"role": "user", "content": "hi"}]}
           )
           assert response.status_code == 200
           
           chunks = []
           async for line in response.aiter_lines():
               if line.startswith("data: "):
                   chunks.append(json.loads(line[6:]))
           
           assert len(chunks) > 0

   @pytest.mark.asyncio
   async def test_handles_chroma_down(monkeypatch):
       """Test graceful handling when Chroma is unavailable."""
       def mock_fail(*args, **kwargs):
           raise ConnectionError("Chroma unavailable")
       
       monkeypatch.setattr("chromadb.HttpClient", mock_fail)
       
       # Test that API returns 503 instead of crashing
       async with httpx.AsyncClient() as client:
           response = await client.get("http://localhost:7000/v1/healthz")
           assert response.status_code == 503

Troubleshooting Tests
---------------------

Tests Fail Locally but Pass in Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution:** Always run tests in the scripts container, not on your host machine. The container has the correct environment:

.. code-block:: bash

   # ✅ Correct
   ./scripts/run.sh test

   # ❌ Wrong
   pytest  # Don't run on host

Import Errors
~~~~~~~~~~~~~

**Problem:** ``ModuleNotFoundError: No module named 'brain'``

**Solution:** Use the scripts container. The PYTHONPATH is configured correctly:

.. code-block:: bash

   docker compose run --rm scripts pytest

Can't Reach Services
~~~~~~~~~~~~~~~~~~~~

**Problem:** ``httpx.ConnectError: Connection refused``

**Solution:**

1. Ensure services are running: ``docker compose ps``
2. Use service names (chroma, ollama), not localhost
3. Check environment variables in ``compose.yaml``

Test Discovery Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem:** Pytest doesn't find your tests

**Solution:**

1. Name files ``test_*.py`` or ``*_test.py``
2. Name functions ``test_*``
3. Place files in ``tests/`` directory
4. Check ``pytest.ini`` for ``testpaths`` configuration

Best Practices
--------------

1. **Always use scripts container**: Consistent environment across machines
2. **Exit codes matter**: Tests should return 0 (success) or 1 (failure)
3. **Use fixtures**: Share common setup via ``conftest.py``
4. **Test in isolation**: Each test should be independent
5. **Mock external services**: Use ``pytest-mock`` or ``monkeypatch`` for external APIs
6. **Document test purpose**: Clear docstrings for each test function
7. **Run tests before commits**: Catch issues early
8. **Add tests for bug fixes**: Prevent regression

Resources
---------

- `Pytest Documentation <https://docs.pytest.org/>`_
- `Pytest-asyncio Documentation <https://pytest-asyncio.readthedocs.io/>`_
- `FastAPI Testing <https://fastapi.tiangolo.com/tutorial/testing/>`_
- `Docker Compose for Testing <https://docs.docker.com/compose/>`_
