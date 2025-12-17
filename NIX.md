# Nix Flake Support for Ada

This directory contains Nix flake configuration for reproducible development and deployment.

## Quick Start

**First time with Nix?** See [docs/zero_to_ada.rst](docs/zero_to_ada.rst) for complete setup guide!

```bash
# 1. Install Nix (one-time)
curl -L https://nixos.org/nix/install | sh

# 2. Enable flakes (one-time)
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# 3. Enter development shell
nix develop

# Or with automatic activation
direnv allow
cd ada-v1  # Environment loads automatically

# 4. Run Ada
ada setup
ada run
```

## Troubleshooting

**404 error?** Update the flake:
```bash
nix flake update
nix develop
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
