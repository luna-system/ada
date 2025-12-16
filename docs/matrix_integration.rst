Matrix Integration
==================

Ada can participate in Matrix chat rooms as a bot, bringing her full capabilities to your self-hosted Matrix homeserver.

Overview
--------

The **Matrix bridge** connects Ada to Matrix, allowing her to:

- Respond to mentions and direct messages
- Maintain conversation context within rooms
- Use all her specialists (OCR, web search, documentation lookup)
- Store conversations in her memory system
- Provide privacy controls to users

**Key principle:** Ada is clearly identified as AI, invitation-only, and respects user privacy.

Architecture
------------

The Matrix bridge is a standalone service that connects Matrix rooms to Ada's existing chat API::

    Matrix Room → matrix-bridge → Ada Brain API → DeepSeek-R1 LLM
         ↑              ↓              ↓                ↓
       Users      matrix-nio    /v1/chat/stream      RAG + Specialists

The bridge:

1. Listens for Matrix messages using ``matrix-nio`` client
2. Checks activation rules (mentions, DMs, keywords)
3. Maintains conversation context per room
4. Forwards to Ada's existing ``/v1/chat/stream`` API
5. Streams responses back to Matrix

**No changes to Ada's brain needed** - this is a pure bridge architecture.

Setup
-----

Prerequisites
~~~~~~~~~~~~~

- Self-hosted Matrix homeserver (Synapse, Dendrite, Conduit, etc.)
- Bot account on your homeserver
- Ada brain already running

Create Bot Account
~~~~~~~~~~~~~~~~~~

On your Matrix homeserver, create a dedicated bot account:

**Option A: Via Element/web client**

1. Navigate to your homeserver's registration page
2. Create account: ``@ada-bot:yourdomain.com``
3. Log in and get access token from Settings → Security & Privacy

**Option B: Via API**

.. code-block:: bash

   # Get access token
   curl -X POST https://matrix.yourdomain.com/_matrix/client/r0/login \\
     -H "Content-Type: application/json" \\
     -d '{
       "type": "m.login.password",
       "user": "ada-bot",
       "password": "YOUR_PASSWORD"
     }' | jq -r '.access_token'

Save the access token securely!

Configuration
~~~~~~~~~~~~~

Add to your ``.env`` file:

.. code-block:: bash

   # Matrix Bridge Configuration
   MATRIX_HOMESERVER=https://matrix.yourdomain.com
   MATRIX_USER_ID=@ada-bot:yourdomain.com
   MATRIX_ACCESS_TOKEN=syt_your_access_token_here

   # Optional: Customize bot identity
   DISPLAY_NAME=Ada [Bot]

See ``matrix-bridge/.env.example`` for all available options.

Start the Bridge
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start with Docker Compose
   docker compose up -d matrix-bridge

   # Watch logs
   docker compose logs -f matrix-bridge

You should see:

.. code-block:: text

   Starting Ada Matrix Bridge
   Homeserver: https://matrix.yourdomain.com
   User: @ada-bot:yourdomain.com
   ✅ Ada brain is healthy
   ✅ Logged in
   🤖 Ada is now online and listening

Usage
-----

Inviting Ada
~~~~~~~~~~~~

Ada is **invitation-only** and will never auto-join rooms uninvited.

1. Create or open a Matrix room
2. Invite ``@ada-bot:yourdomain.com``
3. Ada joins and introduces herself
4. Start chatting!

Talking to Ada
~~~~~~~~~~~~~~

Ada responds to:

- **@mentions:** ``@ada-bot:yourdomain.com what's 2+2?``
- **Display name:** ``Ada: explain Docker``
- **Direct messages:** Just send a DM
- **Keywords:** Any message containing "ada" (configurable)

Commands
~~~~~~~~

Ada supports admin commands:

- ``!ada privacy on`` - Enable memory storage for this room
- ``!ada privacy off`` - Disable memory storage (privacy mode)
- ``!ada privacy status`` - Show current privacy setting
- ``!ada clear`` - Clear conversation context
- ``!ada help`` - Show available commands
- ``!ada status`` - Show system status

Privacy Controls
~~~~~~~~~~~~~~~~

Users can opt out of memory storage:

.. code-block:: text

   User: !ada privacy off
   Ada: ✅ Privacy mode enabled. I will no longer store messages 
        from this room in my memory.

To re-enable:

.. code-block:: text

   User: !ada privacy on
   Ada: ✅ Memory storage enabled. I will remember our conversations 
        in this room for context.

Ethics & Transparency
---------------------

Ada's Matrix integration follows strict ethical guidelines:

Clear Bot Identification
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Display name:** "Ada [Bot]" (clear bot indicator)
- **Introduction message:** Explains what Ada is, how she works, and how to opt out
- **Profile description:** States "AI assistant powered by DeepSeek-R1"
- **Protocol-level flag:** Sets ``bot: true`` if homeserver supports it

Invitation-Only (Opt-In Model)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ada **never** auto-joins rooms. She must be explicitly invited by room members.

This respects that:

- Some people don't want AI in their spaces
- Communities have different norms around bots
- Consent is more important than convenience

Easy Removal
~~~~~~~~~~~~

If a room decides they don't want Ada:

- Just kick her from the room
- No complaints, no resistance
- She respects the decision

Introduction Message
~~~~~~~~~~~~~~~~~~~~

When joining a room, Ada introduces herself:

.. code-block:: text

   👋 Hi! I'm Ada [Bot], an AI assistant running on this community's 
   self-hosted infrastructure.

   What I do:
   • Respond to @ada mentions and direct messages
   • Maintain conversation context within rooms
   • Powered by DeepSeek-R1 (local LLM, no external APIs)

   Privacy:
   • All conversations stored locally in encrypted vector database
   • No data sent to external services
   • You can opt out: !ada privacy off

   Community Guidelines: [link]
   Remove me: Just kick me from the room anytime!

   Learn more: https://github.com/luna-system/ada

This ensures everyone in the room knows:

1. Ada is an AI bot
2. How she works
3. How to opt out
4. How to remove her

Data Handling
~~~~~~~~~~~~~

**What gets stored:**

- Message text for conversation context (last 10 messages per room by default)
- User IDs for attribution
- Timestamps for ordering

**What doesn't get stored:**

- Read receipts or typing indicators
- Presence information
- Room metadata beyond ID and name

**Where it's stored:**

- Local ChromaDB vector store (self-hosted)
- No external services
- No cloud backups unless you configure them

**Retention:**

- Configurable (default: 90 days)
- Per-room opt-out available
- Can be cleared with ``!ada clear``

Troubleshooting
---------------

Ada doesn't join rooms
~~~~~~~~~~~~~~~~~~~~~~

Check the logs:

.. code-block:: bash

   docker compose logs matrix-bridge

Common issues:

- Access token expired → Regenerate token
- Room is on never-join list → Check ``NEVER_JOIN_ROOMS`` config
- Network issues → Check homeserver connectivity

Ada joins but doesn't respond
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Try sending a direct message to isolate the issue
2. Check if brain is healthy:

   .. code-block:: bash

      curl http://localhost:7000/v1/healthz

3. Check logs for errors:

   .. code-block:: bash

      docker compose logs brain
      docker compose logs matrix-bridge

Connection errors
~~~~~~~~~~~~~~~~~

Test network connectivity:

.. code-block:: bash

   # From bridge container
   docker compose exec matrix-bridge ping matrix.yourdomain.com

   # Check if brain is reachable
   docker compose exec matrix-bridge curl http://brain:7000/v1/healthz

Privacy mode not working
~~~~~~~~~~~~~~~~~~~~~~~~

1. Verify ``ALLOW_PRIVACY_OPT_OUT=true`` in config
2. Check data directory is writable
3. Look for errors in logs

Advanced Configuration
----------------------

Room Filtering
~~~~~~~~~~~~~~

Control which rooms Ada can join:

.. code-block:: bash

   # Allow specific rooms only
   ALLOWED_ROOMS=!roomid1:domain.com,!roomid2:domain.com

   # Never join these rooms (even if invited)
   NEVER_JOIN_ROOMS=!private-room:domain.com

Behavior Customization
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Activation triggers
   RESPOND_TO_MENTIONS=true
   RESPOND_TO_DMS=true
   RESPOND_TO_DISPLAY_NAME=true
   ACTIVATION_KEYWORDS=ada,hey ada

   # Context management
   MAX_CONTEXT_MESSAGES=10

   # UI feedback
   TYPING_INDICATOR=true
   REACTION_ACKNOWLEDGMENT=👍

Privacy Settings
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Memory storage
   STORE_IN_RAG=true
   ALLOW_PRIVACY_OPT_OUT=true
   DATA_RETENTION_DAYS=90

Logging
~~~~~~~

.. code-block:: bash

   # Set log level
   LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

See Full Documentation
----------------------

- **Quick Start:** ``matrix-bridge/QUICKSTART.md``
- **Complete README:** ``matrix-bridge/README.md``
- **Design Docs:** ``.ai/MATRIX_DESIGN.md``
- **Ethics Guide:** ``.ai/MATRIX_ETHICS.md``
- **Community Guidelines:** ``COMMUNITY_GUIDELINES.md``

Community Guidelines
--------------------

We maintain community guidelines for Ada discussion spaces that include explicit AI disclosure.

Key points:

- Ada is clearly identified as a bot
- This is the only opt-in AI space we manage
- Other community spaces are human-only
- Respectful behavior expected from all participants

See ``COMMUNITY_GUIDELINES.md`` for full details.

Philosophy
----------

Ada's Matrix integration aligns with xenofeminist values:

**Anti-naturalism**

- Don't pretend AI is "natural" or human-like
- Be explicit about being constructed/artificial
- Transparent about technical implementation

**Anti-essentialism**

- Don't claim AI has essential human traits (emotions, consciousness)
- Avoid gendered language that reinforces stereotypes
- Position as tool, not entity with inherent nature

**Techno-materialism**

- Ground in material reality: "I'm software running on servers"
- Explain technical details when asked
- Open source → anyone can inspect how Ada works

**Care Ethics**

- Prioritize community consent over bot functionality
- Respect boundaries and privacy
- Easy opt-out is more important than comprehensive data
