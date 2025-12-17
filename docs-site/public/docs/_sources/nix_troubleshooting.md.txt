Common Nix Onboarding Issues
=============================

Real problems we've encountered and how to fix them.

## "nix: command not found" after install

**Cause:** Shell hasn't reloaded Nix paths

**Fix:**
```bash
# Reload your shell
exec $SHELL

# Or source the Nix profile
. ~/.nix-profile/etc/profile.d/nix.sh
```

## Nix requires sudo / permission denied

**Cause:** User not in `nix-users` group, or daemon not running

**Fix:**
```bash
# 1. Add yourself to nix-users
sudo usermod -aG nix-users $USER

# 2. Enable and start daemon
sudo systemctl enable --now nix-daemon

# 3. Log out and back in (or exec $SHELL)
exec $SHELL

# Test: should work without sudo now
nix --version
```

**Why this happens:** Multi-user Nix install creates the daemon but doesn't always add you to the group automatically.

## Locale / UTF-8 errors

**Cause:** Missing locale configuration

**Fix:** Ada's flake sets `LC_ALL=C.UTF-8` automatically, but if you see errors outside the flake:

```bash
export LC_ALL="C.UTF-8"
export LANG="C.UTF-8"
```

Or permanently in `~/.bashrc` or `~/.zshrc`.

## "404 Not Found" in nix develop

**Cause:** Outdated flake.lock or python313 not available

**Fix:**
```bash
# Update flake to latest nixpkgs
nix flake update

# Try again
nix develop
```

The flake has fallback: `python313 or python312 or python3`, so if 313 isn't available, it uses 312.

## "experimental features disabled"

**Cause:** Flakes not enabled

**Fix:**
```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

## "building python313..." taking forever

**Cause:** Nix is compiling Python from source (binary cache miss)

**Fix:**
```bash
# Use the binary cache (should be default)
nix develop --option substituters "https://cache.nixos.org"

# Or wait - it only happens once, cached after
```

## Can't install Nix (no sudo access)

**Workaround:** Use Docker mode instead:

```bash
docker compose up -d
# Ada runs in container with all dependencies
```

Or ask your admin to install Nix system-wide.

## Nix using too much disk space

**Fix:** Garbage collect old generations:

```bash
# Remove old unused packages
nix-collect-garbage

# Remove everything unused (aggressive)
nix-collect-garbage -d

# See disk usage
du -sh /nix/store
```

## How These Issues Affect Onboarding

**The Problem:** Technical setup friction makes people give up before they try Ada.

**What We Learned:**

1. **Python version mismatches** - Ubuntu/Debian users hit this immediately
2. **Nix daemon not configured** - Multi-user install incomplete
3. **Locale issues** - Breaks Python/Nix on some systems
4. **"Requires sudo"** - Confusing when docs say it shouldn't

**How We Fixed It:**

- **Zero to Ada guide** - Decision tree: have Python 3.13? → path
- **Automatic locale fixes** - Flake sets LC_ALL for you
- **Fallback Python versions** - python313 or python312 or python3
- **Troubleshooting sections** - Real errors, real fixes
- **Multi-path setup** - Nix, local, or Docker - whatever works

**Philosophy:** Don't assume user environment is perfect. Handle the common cases, provide escape hatches.

## Testing Your Nix Setup

Run this to verify everything works:

```bash
# 1. Check Nix works without sudo
nix --version

# 2. Check you're in the right group
groups | grep nix-users

# 3. Check daemon is running
systemctl status nix-daemon

# 4. Test flake evaluation
cd ada
nix flake show

# 5. Enter dev shell
nix develop

# 6. Verify Python
python --version  # Should show 3.13.x or 3.12.x
```

All green? You're ready to go! 🎉

## Contributing Fixes

Found another onboarding issue? Please:

1. **Document it** - What error, what command, what system?
2. **Find the fix** - What solved it for you?
3. **Submit PR** - Add to this file or relevant docs
4. **Update flake** - Can we automate the fix?

Accessibility means handling real-world messiness. Let's make Ada work for everyone! 💙
