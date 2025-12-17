Nix & Flakes Support
====================

Ada provides first-class support for `Nix <https://nixos.org/>`_ and Nix flakes, offering declarative, reproducible development and deployment environments.

Why Nix?
--------

**Solves Version Mismatches**
   Your distro doesn't have Python 3.13 yet? Nix provides it instantly, no compilation needed.
   Ubuntu 22.04/24.04 users: This is your easiest path to Python 3.13!

**Reproducibility**
   Nix ensures everyone gets the exact same dependencies, eliminating "works on my machine" issues.

**Declarative**
   All dependencies declared in ``flake.nix`` - Python packages, system libraries, tools.

**Cross-platform**
   Works on Linux, macOS, and Windows (via WSL). Perfect for teams with mixed environments.

**Composable**
   Integrate Ada into larger Nix configurations, NixOS modules, or home-manager.

**Cutting Edge**
   Nix flakes are at the forefront of reproducible software development.

Quick Start
-----------

Prerequisites
^^^^^^^^^^^^^

Install Nix with flakes enabled:

.. code-block:: bash

   # Install Nix (official installer)
   curl -L https://nixos.org/nix/install | sh
   
   # Enable flakes (add to ~/.config/nix/nix.conf or /etc/nix/nix.conf)
   experimental-features = nix-command flakes

Development Shell
^^^^^^^^^^^^^^^^^

Enter a development environment with all dependencies:

.. code-block:: bash

   cd ada-v1
   nix develop
   
   # Shell hook displays available commands
   # 🤖 Ada development environment
   # Available commands: ada, ollama, python, pytest...

Now you're in a shell with:

- Python 3.13 with all Ada dependencies
- Ollama LLM runtime
- Tesseract OCR
- Development tools (uv, ruff, pytest)
- Pre-configured environment variables

Run Ada in development mode:

.. code-block:: bash

   # Inside nix develop shell
   ada setup
   ollama serve &
   ollama pull deepseek-r1:latest
   ada run

Build Ada Package
^^^^^^^^^^^^^^^^^

Build Ada as a standalone package:

.. code-block:: bash

   # Build Ada
   nix build
   
   # Result in ./result/bin/ada
   ./result/bin/ada --version

Run Ada Directly
^^^^^^^^^^^^^^^^

Run Ada without building or entering dev shell:

.. code-block:: bash

   # Run from flake
   nix run github:luna-system/ada
   
   # Or locally
   nix run . -- chat "Hello Ada"
   
   # Specific commands
   nix run .#ada-doctor
   nix run .#ada-setup

direnv Integration
^^^^^^^^^^^^^^^^^^

Automatically activate Nix environment when entering directory:

.. code-block:: bash

   # Install direnv
   nix profile install nixpkgs#direnv
   
   # Hook into your shell (add to ~/.bashrc or ~/.zshrc)
   eval "$(direnv hook bash)"  # or zsh, fish, etc.
   
   # Allow direnv in Ada directory
   cd ada-v1
   direnv allow

Now the Nix environment activates automatically when you ``cd`` into the Ada directory! 🎉

NixOS Module
------------

Deploy Ada as a system service on NixOS:

.. code-block:: nix

   # In your configuration.nix or flake
   {
     inputs.ada.url = "github:luna-system/ada";
     
     outputs = { self, nixpkgs, ada }: {
       nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
         system = "x86_64-linux";
         modules = [
           ada.nixosModules.default
           {
             services.ada = {
               enable = true;
               port = 8000;
               ollamaUrl = "http://localhost:11434";
               dataDir = "/var/lib/ada";
             };
             
             # Ollama automatically enabled by default
             services.ollama.enable = true;
           }
         ];
       };
     };
   }

Module Options
^^^^^^^^^^^^^^

.. code-block:: nix

   services.ada = {
     enable = true;           # Enable Ada service
     package = pkgs.ada;      # Package to use (override if needed)
     dataDir = "/var/lib/ada"; # Data directory
     ollamaUrl = "http://localhost:11434"; # Ollama endpoint
     port = 8000;             # API port
     user = "ada";            # Service user
     group = "ada";           # Service group
   };

Service Management
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Start Ada
   sudo systemctl start ada
   
   # Enable on boot
   sudo systemctl enable ada
   
   # Check status
   sudo systemctl status ada
   
   # View logs
   sudo journalctl -u ada -f

Home Manager Integration
------------------------

Include Ada in your personal environment:

.. code-block:: nix

   # In home.nix
   { pkgs, ... }:
   {
     home.packages = [
       (pkgs.callPackage /path/to/ada/flake.nix {}).packages.${pkgs.system}.default
     ];
   }

Or as a flake input:

.. code-block:: nix

   {
     inputs.ada.url = "github:luna-system/ada";
     
     outputs = { self, nixpkgs, home-manager, ada }: {
       homeConfigurations."user@host" = home-manager.lib.homeManagerConfiguration {
         pkgs = nixpkgs.legacyPackages.x86_64-linux;
         modules = [
           {
             home.packages = [ ada.packages.x86_64-linux.default ];
           }
         ];
       };
     };
   }

Customization
-------------

Override Flake Inputs
^^^^^^^^^^^^^^^^^^^^^

Use specific nixpkgs version or overlays:

.. code-block:: bash

   nix develop --override-input nixpkgs github:NixOS/nixpkgs/nixos-24.11

Custom Python Version
^^^^^^^^^^^^^^^^^^^^^

Edit ``flake.nix`` to use different Python:

.. code-block:: nix

   let
     python = pkgs.python312;  # Change from python313
   in
   # ... rest of flake

Add Extra Dependencies
^^^^^^^^^^^^^^^^^^^^^^

Add packages to ``devShells.default.buildInputs``:

.. code-block:: nix

   devShells.default = pkgs.mkShell {
     buildInputs = with pkgs; [
       adaPythonEnv
       tesseract
       # Add your tools
       ripgrep
       fd
       neovim
     ];
   };

Flake Structure
---------------

The Ada flake provides:

**Development Shell** (``nix develop``)
   Complete development environment with all dependencies and tools.

**Package** (``nix build``)
   Standalone Ada package that can be installed system-wide.

**Apps** (``nix run``)
   - ``ada`` - Main command
   - ``ada-setup`` - Setup wizard
   - ``ada-doctor`` - Health check

**NixOS Module**
   System service configuration for NixOS deployments.

Flake Outputs
^^^^^^^^^^^^^

.. code-block:: bash

   # List all outputs
   nix flake show
   
   # Output structure:
   # ├── devShells.x86_64-linux.default
   # ├── packages.x86_64-linux.default
   # ├── apps.x86_64-linux
   # │   ├── default (ada)
   # │   ├── ada-setup
   # │   └── ada-doctor
   # └── nixosModules.default

GPU Support
-----------

For GPU acceleration (NVIDIA CUDA):

.. code-block:: nix

   # In flake.nix or overlay
   let
     pkgs = import nixpkgs {
       config.allowUnfree = true;  # CUDA is unfree
       config.cudaSupport = true;
     };
   in
   # ... use pkgs

Or enable system-wide on NixOS:

.. code-block:: nix

   # configuration.nix
   {
     nixpkgs.config.allowUnfree = true;
     services.xserver.videoDrivers = [ "nvidia" ];
     hardware.opengl.enable = true;
   }

Troubleshooting
---------------

**Flakes not enabled**

.. code-block:: bash

   # Add to ~/.config/nix/nix.conf
   experimental-features = nix-command flakes

**Permission issues**

.. code-block:: bash

   # Ensure you're in nix-users group
   groups | grep nix-users
   
   # Restart nix-daemon
   sudo systemctl restart nix-daemon

**direnv not activating**

.. code-block:: bash

   # Check direnv is hooked
   direnv status
   
   # Re-allow
   direnv allow

**Python import errors**

.. code-block:: bash

   # Ensure PYTHONPATH is set (automatic in dev shell)
   echo $PYTHONPATH
   
   # If missing:
   export PYTHONPATH="$PWD:$PYTHONPATH"

Comparison with Other Methods
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - Nix Flake
     - Docker
     - Python venv
     - System Install
   * - Reproducibility
     - ✅ Perfect
     - ✅ Very Good
     - ⚠️  Partial
     - ❌ Poor
   * - Cross-platform
     - ✅ Linux/macOS/WSL
     - ✅ Linux/macOS/Win
     - ✅ All platforms
     - ⚠️  Linux/macOS
   * - Disk Usage
     - ⚠️  Moderate
     - ⚠️  Large
     - ✅ Minimal
     - ✅ Minimal
   * - Isolation
     - ✅ Strong
     - ✅ Strong
     - ⚠️  Python only
     - ❌ None
   * - Speed
     - ✅ Native
     - ⚠️  Overhead
     - ✅ Native
     - ✅ Native
   * - Setup Time
     - ⚠️  First time slow
     - ⚠️  Pull images
     - ✅ Fast
     - ✅ Fast
   * - System Impact
     - ✅ Minimal
     - ⚠️  Daemon
     - ✅ Minimal
     - ⚠️  Packages
   * - Declarative
     - ✅ Yes
     - ✅ Yes
     - ❌ No
     - ❌ No
   * - Composability
     - ✅ Excellent
     - ⚠️  Limited
     - ❌ No
     - ❌ No

Best Practices
--------------

**Development**: Use ``nix develop`` with ``direnv`` for automatic environment activation.

**CI/CD**: Use ``nix build`` for reproducible builds across different machines.

**Production (NixOS)**: Use the NixOS module for system service deployment.

**Production (Other)**: Use ``nix build`` then copy ``result/`` to target system.

**Teams**: Pin flake inputs with ``flake.lock`` for consistent environments.

**Updates**: Run ``nix flake update`` to update dependencies, commit ``flake.lock``.

Integration Examples
--------------------

GitHub Actions
^^^^^^^^^^^^^^

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: cachix/install-nix-action@v27
           with:
             extra_nix_config: |
               experimental-features = nix-command flakes
         - run: nix build
         - run: nix run . -- doctor

GitLab CI
^^^^^^^^^

.. code-block:: yaml

   # .gitlab-ci.yml
   test:
     image: nixos/nix:latest
     before_script:
       - nix --version
     script:
       - nix build
       - nix run . -- doctor

With Docker (Nix-built)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Build Docker image from Nix package
   nix build .#dockerImage
   docker load < result
   docker run -p 8000:8000 ada:latest

Philosophy
----------

Nix support aligns with Ada's core values:

**Reproducibility = Accessibility**
   Everyone can run Ada in the exact same environment, regardless of their system.

**Declarative = Hackable**
   The entire environment is defined in ``flake.nix`` - read it, understand it, modify it.

**Local-first = Control**
   No cloud services, no Docker daemon required - just Nix and your code.

**Standards-based = Composable**
   Nix flakes are a standard, allowing Ada to integrate into larger Nix ecosystems.

Resources
---------

- `Official Nix Documentation <https://nixos.org/manual/nix/stable/>`_
- `Nix Flakes Tutorial <https://nixos.wiki/wiki/Flakes>`_
- `NixOS Module System <https://nixos.org/manual/nixos/stable/>`_
- `direnv Documentation <https://direnv.net/>`_
- `Nix Pills <https://nixos.org/guides/nix-pills/>`_ (deep dive)

Community
---------

- **NixOS Discourse**: https://discourse.nixos.org/
- **Nix Matrix**: #nix:nixos.org
- **r/NixOS**: https://reddit.com/r/NixOS

Contributing
------------

To improve Ada's Nix support:

1. Test flake on different platforms (Linux, macOS, NixOS)
2. Report issues with ``nix flake show`` output
3. Suggest additional packages for dev shell
4. Improve NixOS module options
5. Share your Nix configurations!

See ``docs/development.rst`` for contribution guidelines.

---

**Ada + Nix**: Reproducible AI for everyone. 🤖❄️
