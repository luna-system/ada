# Quick Issue Creation Guide

## Using GitHub CLI (gh)

```bash
# Install gh if needed
# https://github.com/cli/cli#installation

# Authenticate
gh auth login

# Create issue from template
gh issue create --template plugin_system.md

# Or quick issue
gh issue create --title "Your title" --body "Description"

# With labels
gh issue create --title "Fix typo" --body "Found a typo" --label bug,documentation
```

## Using Web UI

1. Go to: https://github.com/luna-system/ada/issues/new/choose
2. Select template
3. Fill in details
4. Submit!

## Current Planned Issues

### Phase 2 Features (Post-MVP)
- [ ] **Dual-Layer Plugin System** (use `plugin_system.md` template)
  - Labels: `enhancement`, `architecture`, `phase-2`
  - Milestone: v2.0
  
- [ ] **Discord Interface**
  - After plugin system is implemented
  - Labels: `enhancement`, `interface`, `phase-3`
  
- [ ] **Telegram Interface**
  - After plugin system is implemented
  - Labels: `enhancement`, `interface`, `phase-3`

### Matrix Bridge Enhancements (Phase 2)
- [ ] **Matrix: Image OCR Support**
  - Upload images in Matrix, get OCR
  - Labels: `enhancement`, `matrix`, `phase-2`
  
- [ ] **Matrix: Reaction Acknowledgments**
  - 👍 when processing, ✅ when done
  - Labels: `enhancement`, `matrix`, `phase-2`
  
- [ ] **Matrix: Thread Support**
  - Respond in threads
  - Labels: `enhancement`, `matrix`, `phase-2`
  
- [ ] **Matrix: Admin Commands**
  - `!ada clear`, `!ada rooms`, etc.
  - Labels: `enhancement`, `matrix`, `phase-2`

### Documentation
- [ ] **Document Interface vs Capability Pattern**
  - Add to architecture.rst
  - Labels: `documentation`, `architecture`

### Infrastructure
- [ ] **Automated Dependency Updates** (Dependabot/Renovate)
  - Track matrix-nio, httpx, etc.
  - Labels: `infrastructure`, `dependencies`

## Quick Commands

```bash
# Create the dual-layer plugin system issue
gh issue create \
  --title "Architecture: Dual-Layer Plugin System (Interfaces + Capabilities)" \
  --body-file .github/ISSUE_TEMPLATE/plugin_system.md \
  --label "enhancement,architecture,phase-2"

# List all open issues
gh issue list

# View issue #1
gh issue view 1

# Close issue
gh issue close 1
```

## Integration with AI Assistants

When working with GitHub Copilot or other AI assistants, reference issues:

```
"Let's work on #42 - the dual-layer plugin system"
```

This helps maintain context across sessions!
