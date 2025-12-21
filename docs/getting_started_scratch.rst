============================
Getting Started from Scratch
============================

**Build your own AI assistant with Ada.**

This guide walks you through customizing Ada to create YOUR personalized AI assistant - not just use the default.

----

Overview
========

Ada ships with a default "helpful assistant" personality named Ada. But the whole point is to make it YOURS:

- Different name and personality
- Custom knowledge and context
- Tailored tone and behavior
- Your choice of model

**Time required:** 15-30 minutes  
**Difficulty:** Beginner-friendly

----

Step 1: Get Ada Running
========================

If you haven't already:

.. code-block:: bash

   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   ollama serve

   # Clone and setup
   git clone https://github.com/luna-system/ada.git
   cd ada
   python3 ada_main.py setup

   # Pull a model and start
   ollama pull qwen2.5-coder:7b
   ada run

**Checkpoint:** Visit http://localhost:7000/v1/healthz - you should see status "ok".

----

Step 2: Choose Your AI Model
=============================

Ada uses Ollama to run local models. You can use ANY model Ollama supports.

See Available Models
--------------------

Visit https://ollama.com/library for the full list.

**Popular choices:**

- ``llama3.1`` - Meta's open model, good balance of speed/quality
- ``mistral`` - Fast and capable, great for coding
- ``qwen2.5`` - Excellent multilingual support
- ``qwen2.5-coder`` - Great coding-focused model
- ``deepseek-r1`` - Optional, shows reasoning process (can be slower)
- ``gemma2`` - Google's open model, efficient

Change the Model
----------------

Edit ``.env`` in the project root:

.. code-block:: bash

   # Change this line
   OLLAMA_MODEL=llama3.1

   # Or use a specific size
   OLLAMA_MODEL=mistral:7b

Restart Ada:

.. code-block:: bash

   ada stop
   ada run

The first message will be slower as Ollama downloads the new model.

**Checkpoint:** Chat with your chosen model and verify it responds.

----

Step 3: Give Your AI a Personality
===================================

Choose an Example or Start Fresh
---------------------------------

Ada includes example personas in ``examples/personas/``:

.. code-block:: bash

   # See what's available
   ls examples/personas/

   # Copy one you like
   cp examples/personas/coding-buddy.md persona.md

   # Or start minimal
   cp examples/personas/minimal.md persona.md

Edit the Persona
----------------

Open ``persona.md`` in your editor and customize:

.. code-block:: markdown

   # My AI Assistant

   ## Role

   You are [NAME], a [DESCRIPTION] for [USER].

   ## Tone

   [How should your AI communicate? Formal? Casual? Technical?]

   ## Priorities

   What matters most in responses:
   - Be concise / Be detailed
   - Focus on code / Focus on ideas  
   - Ask clarifying questions / Make reasonable assumptions

   ## Special Context

   [Any specific knowledge your AI should have?]
   - Your work domain
   - Your preferences
   - Things to remember about you

**Tips:**

- Keep it under 2000 characters (longer personas get truncated)
- Be specific - "prefer functional programming" works better than "likes code"
- Use examples to show tone rather than describing it
- Don't worry about perfection - iterate!

Reload the Persona
------------------

.. code-block:: bash

   docker compose restart brain

**Checkpoint:** Chat with your AI. Does it match the personality you defined?

----

Step 4: Name Your AI
=====================

Edit ``.env``:

.. code-block:: bash

   AI_NAME=Jarvis
   AI_USER_NAME=Tony

Restart:

.. code-block:: bash

   docker compose restart brain

Your AI will now introduce itself as Jarvis and recognize you as Tony.

**Checkpoint:** Ask "What's your name?" and verify it responds correctly.

----

Step 5: Tweak RAG Settings (Optional)
======================================

RAG (Retrieval-Augmented Generation) controls how much context/memory your AI uses.

Common Adjustments
------------------

In ``.env``:

.. code-block:: bash

   # How many past conversation turns to include
   RAG_TURN_TOP_K=4  # Default: 4, try 6-8 for more context

   # How many memories to retrieve
   RAG_MEMORY_TOP_K=3  # Default: 3

   # Max persona length
   RAG_PERSONA_MAX_CHARS=2000  # Default: 2000

   # Disable features you don't need
   RAG_ENABLE_FAQ=false  # If you don't have FAQs loaded
   RAG_ENABLE_SUMMARY=false  # If you don't want auto-summaries

Restart brain after changes.

When to Adjust
--------------

**Increase context** if:

- Your AI forgets important details from earlier in the conversation
- You have long, complex discussions

**Decrease context** if:

- Responses are slow
- Your AI seems confused by too much information
- You want more focused, concise responses

----

Step 6: Test Core Features
===========================

Memory
------

Have a conversation, then restart the service:

.. code-block:: bash

   docker compose restart brain

In a new conversation, reference something from before. Your AI should remember (memories are stored in ChromaDB).

Web Search
----------

Ask for current information:

   "What's the weather today in Chicago?"

Your AI should use the web_search specialist (you'll see a specialist activation notice).

OCR (Optional)
--------------

Upload an image with text via the web interface. Your AI should extract and discuss the text.

----

Common Issues
=============

"Model not found"
-----------------

Ollama hasn't downloaded the model yet. Wait for the brain container logs:

.. code-block:: bash

   docker compose logs brain -f

You'll see download progress.

Persona not loading
-------------------

Check that ``persona.md`` exists and is less than ``RAG_PERSONA_MAX_CHARS``.

View brain logs for errors:

.. code-block:: bash

   docker compose logs brain | grep persona

Responses are slow
------------------

- Try a smaller model (``mistral:7b`` vs ``mistral:70b``)
- Reduce ``RAG_TURN_TOP_K`` and ``RAG_MEMORY_TOP_K``
- Check if you have a GPU being used (run ``docker compose logs ollama``)

AI doesn't remember anything
-----------------------------

Check ChromaDB is running:

.. code-block:: bash

   docker compose ps chroma

If stopped, start it:

.. code-block:: bash

   docker compose up -d chroma

----

Next Steps
==========

Now that you have a personalized AI:

1. **Build a specialist** - Add custom capabilities
   
   - See :doc:`build_specialist`

2. **Explore the API** - Integrate with other tools
   
   - Visit http://localhost:5000/api/info

3. **Tune performance** - Optimize for your hardware
   
   - See :doc:`configuration`

4. **Share your persona** - Help others learn
   
   - Submit a PR with your persona to ``examples/personas/``

----

Need Help?
==========

- **Documentation:** http://localhost:5000/docs
- **Issues:** https://github.com/yourusername/ada/issues
- **Community:** [Discord/Matrix link]

Remember: Ada is a starting point, not a finished product. Your weird ideas are the point! 🚀
