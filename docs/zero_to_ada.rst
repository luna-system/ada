===============
Zero to Ada
===============

**Get Ada running in under 10 minutes - guaranteed!**

This page is your express lane from nothing to a working Ada assistant. Choose your starting point:

.. contents:: Quick Navigation
   :local:
   :depth: 2

Step 1: Choose Your Path
=========================

Answer one question: **Do you have Python 3.13 installed?**

.. code-block:: bash

   python3 --version

Path A: Yes, I Have Python 3.13+
---------------------------------

✅ **You're on the fast track!** Jump to :ref:`local-setup-fast`.

Path B: No, I Have Python 3.12 or Earlier
------------------------------------------

No problem! You have three options:

**Option 1: Nix (Recommended) ⭐**
   Instant Python 3.13 environment, no compilation.
   
   Jump to :ref:`nix-setup-fast`

**Option 2: Docker**
   Isolated containers, works with any Python version.
   
   Jump to :ref:`docker-setup-fast`

**Option 3: Build from Source**
   Advanced users only, takes 30+ minutes.
   
   See :doc:`installation_advanced`

Path C: I Have Nothing Installed Yet
-------------------------------------

**Fresh Ubuntu/Debian/other Linux?** → Use :ref:`nix-setup-fast` (easiest)

**Fresh macOS?** → Install Ollama, then :ref:`local-setup-fast`

**Windows?** → Use :ref:`docker-setup-fast` or WSL + Nix

.. _nix-setup-fast:

Setup with Nix (Recommended for Most Users)
============================================

**Best for:** Ubuntu, Debian, Fedora, any Linux/macOS without Python 3.13

**Time:** 5-10 minutes

**Why Nix?** Provides Python 3.13 instantly without compiling or breaking your system.

Step 1: Install Nix
--------------------

.. code-block:: bash

   # One-time Nix installation
   curl -L https://nixos.org/nix/install | sh
   
   # Follow the prompts, then restart your shell
   exec $SHELL

**Note:** This installs Nix (a package manager) - it won't interfere with your system Python.

Step 2: Enable Flakes
----------------------

.. code-block:: bash

   # Create Nix config directory
   mkdir -p ~/.config/nix
   
   # Enable flakes
   echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

**Troubleshooting:** If you get permission errors or need sudo:

.. code-block:: bash

   # Fix 1: Make sure you're in nix-users group
   sudo usermod -aG nix-users $USER
   
   # Fix 2: Start the Nix daemon
   sudo systemctl enable --now nix-daemon
   
   # Fix 3: Log out and back in (or reload shell)
   exec $SHELL
   
   # Test: Should work without sudo now
   nix --version

Step 3: Clone Ada
-----------------

.. code-block:: bash

   git clone https://github.com/luna-system/ada.git
   cd ada

Step 4: Enter Nix Environment
------------------------------

.. code-block:: bash

   nix develop

**Magic happens!** ✨ You now have:
- Python 3.13
- All Ada dependencies
- Ollama
- Development tools

Your shell prompt will change to show you're in the Nix environment.

Step 5: Install Ollama Model
-----------------------------

.. code-block:: bash

   # Start Ollama (in background)
   ollama serve > /dev/null 2>&1 &
   
   # Pull a model (choose one)
   ollama pull qwen2.5-coder:7b     # Recommended default
   ollama pull llama3.1:8b          # Good all-rounder, needs 6GB VRAM
   ollama pull qwen2.5:3b           # Lightweight, needs 3GB VRAM

Step 6: Run Ada Setup
----------------------

.. code-block:: bash

   # Now inside nix environment
   ada setup

Follow the interactive prompts to configure Ada.

Step 7: Start Ada
-----------------

.. code-block:: bash

   ada run

Ada is now running at **http://localhost:7000**! 🎉

Step 8: Test It
---------------

Open another terminal:

.. code-block:: bash

   cd ada
   nix develop  # Enter Nix environment again
   ada chat "Hello! What can you do?"

**Success!** You're chatting with Ada.

Step 9: Optional - Auto-activate with direnv
---------------------------------------------

Want the Nix environment to activate automatically when you ``cd`` into the Ada directory?

.. code-block:: bash

   # Install direnv (inside nix environment)
   nix profile install nixpkgs#direnv
   
   # Add to your shell config (~/.bashrc or ~/.zshrc)
   eval "$(direnv hook bash)"  # or 'zsh', 'fish', etc.
   
   # Allow direnv in Ada directory
   cd ada
   direnv allow

Now whenever you ``cd ada``, the environment activates automatically! ✨

.. _local-setup-fast:

Setup with Python 3.13 (Local Mode)
====================================

**Best for:** Users who already have Python 3.13 installed

**Time:** 5 minutes

Prerequisites Check
-------------------

.. code-block:: bash

   # Verify Python version
   python3 --version  # Should show 3.13.x
   
   # If not 3.13, go back and use Nix setup instead!

Step 1: Install Ollama
-----------------------

Download from https://ollama.ai and install for your platform.

.. code-block:: bash

   # Verify installation
   ollama --version

Step 2: Clone Ada
-----------------

.. code-block:: bash

   git clone https://github.com/luna-system/ada.git
   cd ada

Step 3: Run Setup
-----------------

.. code-block:: bash

   python3 ada_main.py setup

This will:
- Create a virtual environment
- Install all Python dependencies
- Create a ``.env`` configuration file
- Set up data directories

Step 4: Pull a Model
--------------------

.. code-block:: bash

   # Start Ollama if not running
   ollama serve > /dev/null 2>&1 &
   
   # Pull a model
   ollama pull qwen2.5-coder:7b

Step 5: Start Ada
-----------------

.. code-block:: bash

   ada run

Ada is now running at **http://localhost:7000**! 🎉

Step 6: Test It
---------------

.. code-block:: bash

   ada chat "Hello Ada!"

.. _docker-setup-fast:

Setup with Docker
=================

**Best for:** Users who want isolated containers or can't use Nix/local mode

**Time:** 10 minutes (includes image download)

Prerequisites
-------------

- Docker installed (get from https://docs.docker.com/get-docker/)
- Docker Compose installed (usually included with Docker Desktop)

Step 1: Clone Ada
-----------------

.. code-block:: bash

   git clone https://github.com/luna-system/ada.git
   cd ada

Step 2: Start Ada
-----------------

.. code-block:: bash

   docker compose up -d

This starts:
- Brain (Ada's API)
- Ollama (LLM runtime)
- ChromaDB (vector database)
- Web UI (optional)

Step 3: Pull a Model
--------------------

.. code-block:: bash

   docker compose exec ollama ollama pull qwen2.5-coder:7b

Step 4: Test It
---------------

Open http://localhost:5000 in your browser, or:

.. code-block:: bash

   curl http://localhost:8000/v1/healthz

Next Steps
==========

Now that Ada is running, you can:

- **Customize personality**: Edit ``persona.md`` or copy from ``examples/personas/``
- **Try the web UI**: http://localhost:5000 (if using Docker)
- **Use the CLI**: ``ada chat "your question"``
- **Interactive mode**: ``ada-cli`` for a REPL
- **Add specialists**: See :doc:`specialists`
- **Matrix integration**: See :doc:`matrix_integration`
- **MCP tools**: See ``ada-mcp/README.md``

Troubleshooting
===============

"nix: command not found"
-------------------------

You need to install Nix first. See :ref:`nix-setup-fast` Step 1.

"Python 3.13 not found"
------------------------

Don't run ``python3 ada_main.py`` directly! Use one of these instead:

1. **Nix**: ``nix develop`` then ``ada setup``
2. **Docker**: ``docker compose up``

"Ollama connection failed"
---------------------------

.. code-block:: bash

   # Start Ollama
   ollama serve &
   
   # Verify it's running
   curl http://localhost:11434/api/tags

"404 error in nix develop"
---------------------------

Your nixpkgs might be outdated. Update it:

.. code-block:: bash

   nix flake update
   nix develop

"ModuleNotFoundError"
---------------------

Make sure you're in the virtual environment:

.. code-block:: bash

   # If using Nix
   nix develop
   
   # If using local mode
   source .venv/bin/activate

Still Stuck?
============

- Check full docs: :doc:`getting_started`
- See detailed troubleshooting: :doc:`troubleshooting` (if it exists)
- Ask in GitHub Discussions: https://github.com/luna-system/ada/discussions

---

**You made it!** Welcome to Ada. Now go make something amazing. 🤖💙
