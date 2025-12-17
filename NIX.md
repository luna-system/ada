# Nix Flake Support for Ada

This directory contains Nix flake configuration for reproducible development and deployment.

## Quick Start

```bash
# Enter development shell
nix develop

# Or with automatic activation
direnv allow
cd ada-v1  # Environment loads automatically

# Build Ada package
nix build

# Run Ada directly
nix run . -- chat "Hello!"
```

## What's Included

- **flake.nix** - Main flake definition with:
  - Development shell (`nix develop`)
  - Ada package (`nix build`)
  - Apps for direct execution (`nix run`)
  - NixOS module for system service

- **.envrc** - direnv configuration for automatic shell activation

- **flake.lock** - Locked dependencies (commit this for reproducibility)

## See Also

- Full documentation: `docs/nix.rst`
- Getting Started: `docs/getting_started.rst`
- NixOS deployment: See NixOS module in `flake.nix`

## Why Nix?

- **Solves version mismatches**: Python 3.13 not in your distro? Nix provides it instantly!
- **Reproducible**: Same dependencies everywhere
- **Declarative**: All deps in `flake.nix`
- **Cross-platform**: Linux, macOS, WSL
- **Composable**: Integrate with larger Nix configs
- **Cutting edge**: Flakes are the future of Nix

### Perfect for Ubuntu Users

Ubuntu 22.04 LTS maxes at Python 3.10, Ubuntu 24.04 LTS at Python 3.12.  
Rather than compiling Python 3.13 from source, just use Nix:

```bash
nix develop  # Instant Python 3.13 environment!
```

Ada + Nix = Reproducible AI for everyone! 🤖❄️
