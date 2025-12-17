# Changelog Automation

Declarative programmatic change management for Ada using **Conventional Commits** and **Semantic Versioning**.

## What This Is

A complete system for managing versions, generating changelogs, and validating commit messages — all automatically.

**The Problem:** Manual version management is error-prone. You forget to tag, changelogs get out of sync, commit messages are inconsistent.

**The Solution:** Structured commit messages + automation tools = automatic version suggestions, generated changelogs, and validated commits.

## Quick Start

### 1. Write good commit messages

```bash
git commit -m "feat: add new specialist"
git commit -m "fix(matrix): handle rate limiting"
git commit -m "docs: update API reference"
```

### 2. Let tooling suggest the version

```bash
$ ./scripts/version.sh suggest
Analyzing commits to suggest next version...

Current version: 1.8.0
Latest tag: v1.8.0

Commit analysis:
  Breaking changes: 0
  Features: 1
  Fixes: 0
  Performance: 0

Suggestion: MINOR bump → 1.9.0
Reason: New features or performance improvements

To apply:
  ./scripts/version.sh bump minor "Version 1.9.0"
```

### 3. Preview changelog

```bash
$ ./scripts/version.sh changelog
Generating changelog for next release...

Changelog since v1.8.0:
================================

## [HEAD] - 2025-12-16

### ✨ Features
- add changelog automation with Conventional Commits

### 📚 Documentation
- add comprehensive version management guide
- add versioning guide to documentation index

---
Total commits: 3
  Features: 1 | Fixes: 0 | Docs: 2
```

### 4. Bump version

```bash
$ ./scripts/version.sh bump minor "Changelog Automation"
Bumping version: 1.8.0 → 1.9.0
✓ Updated version to 1.9.0 in:
  - pyproject.toml
  - ada_main.py
✓ Created tag v1.9.0

Done! Version bumped to v1.9.0
Push with: git push origin trunk --tags
```

## Tools

### [`scripts/version.sh`](scripts/version.sh)

Main version management tool.

```bash
./scripts/version.sh current    # Show current version
./scripts/version.sh suggest    # Suggest next version based on commits
./scripts/version.sh changelog  # Preview changelog
./scripts/version.sh bump <type> "Message"  # Bump and tag
./scripts/version.sh check      # Check for untagged commits
```

### [`scripts/changelog.sh`](scripts/changelog.sh)

Generate formatted changelogs from git history.

```bash
./scripts/changelog.sh v1.8.0 HEAD  # Generate changelog between versions
./scripts/changelog.sh v1.8.0 HEAD >> CHANGELOG.md  # Append to file
```

### [`scripts/validate-commit.sh`](scripts/validate-commit.sh)

Validate commit messages follow Conventional Commits.

```bash
# Standalone validation
./scripts/validate-commit.sh .git/COMMIT_EDITMSG

# Install as git hook
ln -sf ../../scripts/validate-commit.sh .git/hooks/commit-msg
```

## Conventional Commits

Structured commit message format:

```
type(scope): subject

Optional body

Optional footer
```

**Types:**

- `feat`: New feature → **MINOR** version bump
- `fix`: Bug fix → **PATCH** version bump
- `docs`: Documentation → **PATCH** version bump
- `perf`: Performance → **MINOR** version bump
- `refactor`: Refactoring → **PATCH** version bump
- `test`: Tests → **PATCH** version bump
- `chore`: Maintenance → **PATCH** version bump
- `BREAKING CHANGE`: in body → **MAJOR** version bump

**Examples:**

```bash
# Feature (MINOR bump: 1.8.0 → 1.9.0)
git commit -m "feat: add Wikipedia specialist"
git commit -m "feat(specialists): add web search capability"

# Fix (PATCH bump: 1.8.0 → 1.8.1)
git commit -m "fix: resolve memory leak"
git commit -m "fix(matrix): handle rate limiting"

# Breaking change (MAJOR bump: 1.8.0 → 2.0.0)
git commit -m "feat!: change specialist API

BREAKING CHANGE: SpecialistProtocol now requires async methods.
Update all specialists to use async/await."

# Documentation (PATCH bump)
git commit -m "docs: update getting started guide"
git commit -m "docs(api): add examples to API reference"
```

## Semantic Versioning

Ada follows [SemVer 2.0.0](https://semver.org/):

**MAJOR.MINOR.PATCH**

- **MAJOR**: Breaking changes (API incompatibility)
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

**When to bump:**

| Change Type | Example | Bump |
|------------|---------|------|
| Breaking API change | Remove endpoint | MAJOR |
| New feature | Add specialist | MINOR |
| Performance improvement | Optimize memory | MINOR |
| Bug fix | Fix crash | PATCH |
| Documentation | Update guide | PATCH |
| Refactoring | Clean up code | PATCH |

## Complete Workflow

### Development

1. **Create feature branch:**
   ```bash
   git checkout -b feature/amazing-thing
   ```

2. **Make changes with good commits:**
   ```bash
   git commit -m "feat: add amazing feature"
   git commit -m "fix: handle edge case"
   git commit -m "docs: update documentation"
   git commit -m "test: add test coverage"
   ```

3. **Merge to trunk:**
   ```bash
   git checkout trunk
   git merge feature/amazing-thing
   git push origin trunk
   ```

### Release

1. **Check status:**
   ```bash
   ./scripts/version.sh check      # What commits are untagged?
   ./scripts/version.sh suggest    # What version should we bump to?
   ```

2. **Preview changelog:**
   ```bash
   ./scripts/version.sh changelog
   ```

3. **Bump version:**
   ```bash
   ./scripts/version.sh bump minor "Amazing Feature"
   ```

4. **Update CHANGELOG.md:**
   ```bash
   ./scripts/changelog.sh v1.8.0 v1.9.0 > /tmp/section.md
   cat /tmp/section.md CHANGELOG.md > CHANGELOG.md.tmp
   mv CHANGELOG.md.tmp CHANGELOG.md
   git add CHANGELOG.md
   git commit -m "docs: update CHANGELOG for v1.9.0"
   ```

5. **Push:**
   ```bash
   git push origin trunk --tags
   ```

6. **Create GitHub release** (optional):
   ```bash
   gh release create v1.9.0 \
     --title "v1.9.0 - Amazing Feature" \
     --notes-file /tmp/section.md
   ```

## Automation

### Git Hook

Automatically validate commits:

```bash
ln -sf ../../scripts/validate-commit.sh .git/hooks/commit-msg
```

Now invalid commits are rejected:

```bash
$ git commit -m "fixed bug"
❌ Invalid commit message format!

Your commit message must follow Conventional Commits:
  type(scope): subject

Examples:
  feat: add Nix flake support
  fix(matrix): handle rate limiting
  docs: update getting started guide
```

### CI/CD

Validate all commits in CI:

```yaml
# .github/workflows/validate.yml
- name: Validate Commits
  run: |
    git log --pretty=format:"%s" origin/trunk..HEAD | \
    while read msg; do
      echo "$msg" | ./scripts/validate-commit.sh /dev/stdin || exit 1
    done

- name: Suggest Version
  run: ./scripts/version.sh suggest
```

## Philosophy

This aligns with Ada's xenofeminist principles:

- **Accessibility:** Anyone can understand version changes from changelog
- **Automation:** Reduce manual work and human error
- **Transparency:** Clear history of what changed and why
- **Standards:** Use established conventions (SemVer, Conventional Commits)
- **Hackability:** Simple bash scripts, easy to modify

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Comprehensive documentation](docs/versioning.rst)

## Files

- `scripts/version.sh` - Version management
- `scripts/changelog.sh` - Changelog generation
- `scripts/validate-commit.sh` - Commit validation
- `CHANGELOG.md` - Human-readable changelog
- `docs/versioning.rst` - Full documentation
- `pyproject.toml` - Contains version number
- `ada_main.py` - Contains version number

---

**Status:** ✅ Complete and production-ready  
**Version:** 1.0.0  
**Last Updated:** 2025-12-16
