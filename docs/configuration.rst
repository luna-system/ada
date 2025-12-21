Configuration Reference
=======================

Ada uses environment variables for configuration, providing flexibility across development and production environments.

.. tip::

   **Runtime Configuration Discovery:** Once Ada is running, query **GET /v1/info** to see the current active configuration:
   
   .. code-block:: bash
   
      curl http://localhost:5000/api/info | jq
   
   This shows enabled features, active models, specialist count, and all available endpoints.

Quick Start
-----------

1. Copy the example configuration:

   .. code-block:: bash

      cp .env.example .env

2. Edit ``.env`` with your preferred settings
3. Restart services: ``docker compose up -d``

Configuration File
------------------

Ada loads configuration from ``.env`` in the project root. The file uses standard ``KEY=VALUE`` format:

.. code-block:: bash

   # Core Services
   OLLAMA_BASE_URL=http://ollama:11434
   OLLAMA_MODEL=qwen2.5-coder:7b

.. note::
   Docker Compose warnings about ``$ts``, ``$pid1``, ``$pid2`` are harmless - these are shell variables used in command blocks, not environment variables.

Core Services
-------------

These settings define essential services Ada needs to function.

OLLAMA_BASE_URL
^^^^^^^^^^^^^^^

:Default: ``http://localhost:11434``
:Required: No
:Examples: ``http://ollama:11434``, ``http://localhost:11434``

Base URL for the Ollama API server. In Docker Compose, use the service name (``ollama``). For local development, use ``localhost``.

OLLAMA_MODEL
^^^^^^^^^^^^

:Default: ``qwen2.5-coder:7b``
:Required: No
:Examples: ``deepseek-r1``, ``deepseek-r1:14b``, ``llama3.2:3b``, ``qwen2.5:7b``

The Ollama model to use for chat completions. Must be pulled before use:

.. code-block:: bash

   docker compose exec ollama ollama pull qwen2.5-coder:7b

OLLAMA_EMBED_MODEL
^^^^^^^^^^^^^^^^^^

:Default: ``nomic-embed-text``
:Required: No
:Examples: ``nomic-embed-text``, ``mxbai-embed-large``

The embedding model for vector operations (RAG). Must be pulled separately:

.. code-block:: bash

   docker compose exec ollama ollama pull nomic-embed-text

CHROMA_URL
^^^^^^^^^^

:Default: ``http://chroma:8000`` (in Docker)
:Required: No
:Examples: ``http://chroma:8000``, ``http://localhost:8000``

Chroma vector database URL. Leave unset to use the Docker service default.

BRAIN_URL
^^^^^^^^^

:Default: ``http://brain:7000``
:Required: No

Internal URL for the brain service. Used by the web frontend to proxy API requests.

RAG Configuration
-----------------

These settings control Ada's Retrieval-Augmented Generation system.

RAG_ENABLED
^^^^^^^^^^^

:Default: ``true``
:Type: Boolean (``true``/``false``)

Master toggle for the entire RAG system. When ``false``, Ada uses only the base model without context retrieval.

.. warning::
   Disabling RAG significantly reduces Ada's ability to remember context and use your custom persona.

Feature Toggles
^^^^^^^^^^^^^^^

Enable or disable specific retrieval types. All default to ``true``.

- **RAG_ENABLE_PERSONA**: Retrieve persona/identity context
- **RAG_ENABLE_FAQ**: Retrieve FAQ entries
- **RAG_ENABLE_MEMORY**: Retrieve long-term memories
- **RAG_ENABLE_SUMMARY**: Retrieve conversation summaries
- **RAG_ENABLE_TURN**: Retrieve recent conversation turns

Example:

.. code-block:: bash

   # Disable memory retrieval
   RAG_ENABLE_MEMORY=false

Retrieval Parameters (Top-K)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Control how many results to retrieve for each query. Higher values provide more context but use more tokens.

RAG_TURN_TOP_K
""""""""""""""

:Default: ``4``
:Range: 1-20

Number of recent conversation turns to retrieve. Higher values give Ada more conversational context.

RAG_SUMMARY_TOP_K
"""""""""""""""""

:Default: ``2``
:Range: 1-10

Number of conversation summaries to retrieve. Summaries compress multiple turns into key points.

RAG_FAQ_TOP_K
"""""""""""""

:Default: ``2``
:Range: 1-10

Number of FAQ entries to retrieve. Useful for specialist documentation and common questions.

RAG_MEMORY_TOP_K
""""""""""""""""

:Default: ``3``
:Range: 1-20

Number of long-term memories to retrieve. These persist across conversation sessions.

Processing Parameters
^^^^^^^^^^^^^^^^^^^^^

RAG_MEMORY_IMPORTANCE_WEIGHT
"""""""""""""""""""""""""""""

:Default: ``0.5``
:Range: 0.0-1.0

Weight for memory importance scoring when ranking memories. Higher values prioritize "important" memories over recent ones.

RAG_SUMMARY_EVERY_N
"""""""""""""""""""

:Default: ``8``
:Range: 1+

Generate a conversation summary every N turns. Summaries help compress long conversations.

RAG_SUMMARY_TURNS_WINDOW
"""""""""""""""""""""""""

:Default: ``12``
:Range: 1+

Number of conversation turns to include when generating a summary.

RAG_PERSONA_MAX_CHARS
""""""""""""""""""""""

:Default: ``2000``
:Range: 100+

Maximum characters to retrieve from the persona document. Truncates long personas to fit token budget.

Data Loading
^^^^^^^^^^^^

RAG_AUTOLOAD_PERSONA
"""""""""""""""""""""

:Default: ``true``
:Type: Boolean

Automatically load ``persona.md`` into the vector database on startup.

RAG_PERSONA_PATH
""""""""""""""""

:Default: ``/app/persona.md``

Path to the persona markdown file to load on startup.

RAG_AUTOLOAD_FAQ
""""""""""""""""

:Default: ``false``
:Type: Boolean

Automatically load FAQ entries from JSONL on startup.

RAG_FAQ_PATH
""""""""""""

:Default: ``/app/seed/faqs.jsonl``

Path to the FAQ JSONL file.

Debug Mode
^^^^^^^^^^

RAG_DEBUG
"""""""""

:Default: ``false``
:Type: Boolean

Enable debug endpoints at ``/v1/debug/*`` for inspecting RAG behavior.

.. warning::
   Only enable in development. Debug endpoints expose internal state.

Specialist System
-----------------

Controls how Ada uses external capabilities (web search, OCR, vision).

For detailed information on the specialist plugin system, see :doc:`specialists`.

SPECIALIST_PAUSE_RESUME
^^^^^^^^^^^^^^^^^^^^^^^

:Default: ``true``
:Type: Boolean

Enable bidirectional pause/resume for specialists (Phase 2). When ``true``, LLM generation pauses while the specialist executes, then resumes with enriched context. This produces higher-quality integration than mid-stream injection.

SPECIALIST_MAX_TURNS
^^^^^^^^^^^^^^^^^^^^

:Default: ``5``
:Range: 1-20

Maximum number of specialist calls allowed per conversation turn. Prevents infinite loops.

SPECIALIST_RAG_DOCS
^^^^^^^^^^^^^^^^^^^

:Default: ``true``
:Type: Boolean

Use RAG to dynamically retrieve relevant specialist documentation from the FAQ system. When ``false``, uses only static system prompt instructions.

Integrations
------------

All integrations are optional. Leave unset to disable.

Web Search (SearxNG)
^^^^^^^^^^^^^^^^^^^^

SEARXNG_URL
"""""""""""

:Default: (none)
:Required: No
:Example: ``https://hunt.airsi.de``

SearxNG instance URL for the web search specialist. When set, Ada can search the web for current information.

Setup:

.. code-block:: bash

   # In .env
   SEARXNG_URL=https://your-searxng-instance.com

.. tip::
   You can use a public SearxNG instance or host your own. See `SearxNG documentation <https://docs.searxng.org/>`_ for self-hosting.

ListenBrainz (Music Context)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

LISTENBRAINZ_USER
"""""""""""""""""

:Default: (none)
:Required: No
:Example: ``your_username``

ListenBrainz username for music context integration.

LISTENBRAINZ_TOKEN
""""""""""""""""""

:Default: (none)
:Required: No

ListenBrainz API token. Get yours at `ListenBrainz settings <https://listenbrainz.org/settings/>`_.

Setup:

.. code-block:: bash

   # In .env
   LISTENBRAINZ_USER=your_username
   LISTENBRAINZ_TOKEN=your_api_token

Backup Configuration
--------------------

Settings for automated Chroma database backups to Backblaze B2.

Backblaze B2 Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^

B2_ENDPOINT_URL
"""""""""""""""

:Default: (none)
:Required: For backups
:Example: ``s3.us-east-005.backblazeb2.com``

S3-compatible endpoint URL from your Backblaze B2 bucket settings.

B2_KEY_ID
"""""""""

:Default: (none)
:Required: For backups

Backblaze B2 key ID (starts with ``005...``).

B2_APPLICATION_KEY
""""""""""""""""""

:Default: (none)
:Required: For backups

Backblaze B2 application key (secret).

B2_BUCKET_NAME
""""""""""""""

:Default: (none)
:Required: For backups

Name of the B2 bucket to store backups.

Backup Options
^^^^^^^^^^^^^^

B2_BUCKET_PREFIX
""""""""""""""""

:Default: ``chroma-backups``

Folder prefix inside the bucket where backups are stored.

UPLOAD_MODE
"""""""""""

:Default: ``latest``
:Options: ``latest``, ``all``

- ``latest``: Only upload the most recent backup
- ``all``: Upload all local backups

BACKUPS_DIR
"""""""""""

:Default: ``/data/backups``

Local directory where backups are stored before upload.

Configuration Validation
-------------------------

Ada validates configuration at startup. Check the logs for warnings:

.. code-block:: bash

   docker compose logs brain | grep -i config

Common validation issues:

- **Missing required values**: Ada uses defaults, but may not work as expected
- **Invalid ranges**: Values outside allowed ranges are clamped
- **Type errors**: Non-boolean values for boolean settings

Best Practices
--------------

1. **Use .env for secrets**: Never commit ``.env`` to version control
2. **Document changes**: Comment your ``.env`` when deviating from defaults
3. **Test in development**: Verify configuration changes in dev before production
4. **Backup .env**: Include ``.env`` in your backup strategy
5. **Use .env.example**: Keep ``.env.example`` updated as a template

Environment-Specific Configuration
-----------------------------------

Development
^^^^^^^^^^^

.. code-block:: bash

   # .env.development
   RAG_DEBUG=true
   OLLAMA_BASE_URL=http://localhost:11434
   CHROMA_URL=http://localhost:8000

Production
^^^^^^^^^^

.. code-block:: bash

   # .env.production
   RAG_DEBUG=false
   OLLAMA_BASE_URL=http://ollama:11434
   CHROMA_URL=http://chroma:8000
   # Add Backblaze credentials for backups
   B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com
   B2_KEY_ID=<your-key-id>
   B2_APPLICATION_KEY=<your-secret>
   B2_BUCKET_NAME=<your-bucket>

Troubleshooting
---------------

Configuration not loading
^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: Changes to ``.env`` don't take effect

**Solutions**:

1. Rebuild containers: ``docker compose build brain``
2. Restart services: ``docker compose up -d``
3. Verify ``.env`` location (must be in project root)
4. Check for syntax errors in ``.env``

Services can't connect
^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: ``Connection refused`` errors

**Solutions**:

1. In Docker Compose, use service names (``http://ollama:11434`` not ``localhost``)
2. Check services are running: ``docker compose ps``
3. Verify network connectivity: ``docker compose exec brain ping ollama``

Models not found
^^^^^^^^^^^^^^^^

**Symptom**: ``model 'qwen2.5-coder:7b' not found``

**Solutions**:

1. Pull the model: ``docker compose exec ollama ollama pull qwen2.5-coder:7b``
2. List available models: ``docker compose exec ollama ollama list``
3. Update ``OLLAMA_MODEL`` to match an installed model

See Also
--------

- :doc:`getting_started` - Initial setup guide
- :doc:`testing` - Testing your configuration
- :doc:`development` - Development workflows
- :doc:`api_usage` - API reference
