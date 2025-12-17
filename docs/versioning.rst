======================
Version Management
======================

Ada uses **Semantic Versioning** with **Conventional Commits** for automated changelog generation and version management.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
========

Version Format
--------------

Ada follows `Semantic Versioning 2.0.0 <https://semver.org/>`_:

**MAJOR.MINOR.PATCH**

- **MAJOR**: Breaking changes (API incompatibility)
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Examples: ``1.8.0``, ``2.0.1``, ``1.9.12``

Conventional Commits
--------------------

Commit messages follow `Conventional Commits <https://www.conventionalcommits.org/>`_:

**Format**::

   type(scope): subject
   
   Optional body with more details.
   
   Optional footer with BREAKING CHANGE: description

**Types**:

- ``feat``: New feature → MINOR bump
- ``fix``: Bug fix → PATCH bump
- ``docs``: Documentation → PATCH bump
- ``style``: Code style (formatting) → PATCH bump
- ``refactor``: Code refactoring → PATCH bump
- ``perf``: Performance improvement → MINOR bump
- ``test``: Test changes → PATCH bump
- ``chore``: Maintenance → PATCH bump
- ``ci``: CI/CD changes → PATCH bump
- ``build``: Build system → PATCH bump

**BREAKING CHANGE** in commit body → MAJOR bump

Examples
~~~~~~~~

Good commit messages::

   feat: add Nix flake support
   fix(matrix): handle rate limiting errors
   docs: update getting started guide
   feat(specialists)!: change specialist API

   BREAKING CHANGE: SpecialistProtocol now requires async methods
   chore: bump version to v1.9.0

Bad commit messages::

   updated stuff
   Fix bug
   WIP
   asdf

Version Management Tools
========================

Ada provides three scripts for version management:

version.sh
----------

Main version management tool.

**Commands**::

   ./scripts/version.sh current        # Show current version
   ./scripts/version.sh suggest        # Suggest next version based on commits
   ./scripts/version.sh changelog      # Generate changelog preview
   ./scripts/version.sh bump <type>    # Bump version and create tag
   ./scripts/version.sh check          # Check for untagged commits
   ./scripts/version.sh tag <version>  # Create tag without bumping files

**Examples**::

   # Check what version we're at
   $ ./scripts/version.sh current
   1.8.0
   
   # Analyze commits and suggest next version
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
   
   # Preview changelog for next release
   $ ./scripts/version.sh changelog
   
   # Bump version and create tag
   $ ./scripts/version.sh bump minor "Changelog Automation"
   Bumping version: 1.8.0 → 1.9.0
   ✓ Updated version to 1.9.0 in:
     - pyproject.toml
     - ada_main.py
   ✓ Created tag v1.9.0
   
   Done! Version bumped to v1.9.0
   Push with: git push origin trunk --tags

changelog.sh
------------

Generate formatted changelog from git commits.

**Usage**::

   ./scripts/changelog.sh [from_version] [to_version]

**Examples**::

   # Generate changelog since last tag
   $ ./scripts/changelog.sh v1.8.0 HEAD
   
   ## [HEAD] - 2025-12-16
   
   ### ✨ Features
   - add changelog automation with Conventional Commits
   
   ### 📚 Documentation
   - create version management guide
   
   ---
   Total commits: 2
     Features: 1 | Fixes: 0 | Docs: 1
   
   # Update CHANGELOG.md with new section
   $ ./scripts/changelog.sh v1.8.0 v1.9.0 | cat - CHANGELOG.md > CHANGELOG.md.tmp
   $ mv CHANGELOG.md.tmp CHANGELOG.md

validate-commit.sh
------------------

Validate commit messages follow Conventional Commits format.

**Usage**::

   # Validate a commit message file
   ./scripts/validate-commit.sh .git/COMMIT_EDITMSG
   
   # Install as git hook
   ln -sf ../../scripts/validate-commit.sh .git/hooks/commit-msg

**What it checks**:

- ✅ Type is valid (feat, fix, docs, etc.)
- ✅ Format is correct (type: subject or type(scope): subject)
- ⚠️ Subject isn't too long (warns >72 chars)
- ⚠️ Subject doesn't end with period
- ⚠️ Subject uses imperative mood (lowercase start)
- ✅ Allows merge commits and reverts

**Example validation**::

   $ echo "feat: add new feature" > /tmp/msg
   $ ./scripts/validate-commit.sh /tmp/msg
   ✓ Valid!
   
   $ echo "Added new feature" > /tmp/msg
   $ ./scripts/validate-commit.sh /tmp/msg
   ❌ Invalid commit message format!
   
   Your commit message must follow Conventional Commits:
     type(scope): subject
   
   Examples:
     feat: add Nix flake support
     fix(matrix): handle rate limiting
     docs: update getting started guide

Workflow
========

Complete Release Workflow
--------------------------

1. **Develop features with conventional commits**::

      git checkout -b feature/new-thing
      git commit -m "feat: add amazing new feature"
      git commit -m "fix: handle edge case"
      git commit -m "docs: update API reference"

2. **Check status before release**::

      # What untagged commits do we have?
      ./scripts/version.sh check
      
      # What version should we bump to?
      ./scripts/version.sh suggest

3. **Preview changelog**::

      ./scripts/version.sh changelog

4. **Bump version and create tag**::

      # Automatically suggests minor for features
      ./scripts/version.sh bump minor "Amazing New Feature"

5. **Update CHANGELOG.md**::

      # Generate and prepend to changelog
      ./scripts/changelog.sh v1.8.0 v1.9.0 > /tmp/new_section.md
      cat /tmp/new_section.md CHANGELOG.md > CHANGELOG.md.tmp
      mv CHANGELOG.md.tmp CHANGELOG.md
      git add CHANGELOG.md
      git commit -m "docs: update CHANGELOG for v1.9.0"

6. **Push release**::

      git push origin trunk --tags

7. **Create GitHub release** (optional)::

      # Use changelog content as release notes
      gh release create v1.9.0 --title "v1.9.0" --notes-file /tmp/new_section.md

Quick Release (Automated)
--------------------------

For simple releases with good commit messages::

   # One-liner: suggest, bump, and update changelog
   VERSION=$(./scripts/version.sh suggest | grep "Suggestion" | cut -d→ -f2 | xargs)
   ./scripts/version.sh bump minor "Version $VERSION"
   ./scripts/changelog.sh v1.8.0 v$VERSION | cat - CHANGELOG.md > CHANGELOG.md.tmp
   mv CHANGELOG.md.tmp CHANGELOG.md
   git add CHANGELOG.md
   git commit --amend --no-edit
   git push origin trunk --tags

Git Hook Setup
--------------

Automatically validate commit messages::

   # Install commit-msg hook
   ln -sf ../../scripts/validate-commit.sh .git/hooks/commit-msg
   
   # Now invalid commits will be rejected:
   $ git commit -m "fixed bug"
   ❌ Invalid commit message format!
   
   $ git commit -m "fix: correct handling of edge case"
   ✓ Success!

Skip validation when needed::

   git commit --no-verify -m "WIP: experimenting"

Best Practices
==============

Commit Messages
---------------

**Do**:

- Start with lowercase: ``feat: add feature`` ✅
- Use imperative mood: ``fix: resolve issue`` ✅
- Be specific: ``fix(rag): improve memory retrieval`` ✅
- Include scope: ``feat(specialists): add wiki lookup`` ✅
- Keep subject <72 chars ✅

**Don't**:

- Start with uppercase: ``feat: Add feature`` ❌
- Use past tense: ``feat: added feature`` ❌
- Be vague: ``fix: fixed bug`` ❌
- End with period: ``feat: add feature.`` ❌
- Write novels: ``feat: this adds a really long feature description...`` ❌

Version Bumps
-------------

**When to bump MAJOR** (breaking changes):

- API changes requiring code updates
- Removing features
- Changing behavior incompatibly
- Architectural shifts

**When to bump MINOR** (new features):

- New features (backwards compatible)
- New specialists
- Performance improvements
- Deprecations (not removals)

**When to bump PATCH** (bug fixes):

- Bug fixes
- Documentation updates
- Code refactoring (no behavior change)
- Security patches

Scopes
------

Common scopes in Ada:

- ``specialists``: Specialist system changes
- ``rag``: RAG/memory system
- ``matrix``: Matrix bridge
- ``cli``: CLI interface
- ``web``: Web UI
- ``api``: API changes
- ``llm``: LLM integration
- ``docs``: Documentation
- ``build``: Build system
- ``ci``: CI/CD

Example: ``feat(specialists): add Wikipedia lookup``

Breaking Changes
----------------

Mark breaking changes explicitly::

   feat(api)!: change chat endpoint response format
   
   BREAKING CHANGE: ChatResponse now returns 'messages' array
   instead of 'text' string. Update all API clients.
   
   Migration:
     Before: response.text
     After: response.messages[0].content

This triggers a MAJOR version bump.

Automation
==========

CI/CD Integration
-----------------

Validate commits in CI::

   # .github/workflows/validate.yml
   - name: Validate Commit Messages
     run: |
       git log --pretty=format:"%s" origin/trunk..HEAD | \
       while read msg; do
         echo "$msg" | ./scripts/validate-commit.sh /dev/stdin || exit 1
       done

Auto-suggest version on PR::

   # .github/workflows/suggest-version.yml
   - name: Suggest Version
     run: ./scripts/version.sh suggest

Pre-commit Hook
---------------

Install for all developers::

   # In repository
   echo '#!/bin/sh' > .git/hooks/commit-msg
   echo 'exec ./scripts/validate-commit.sh "$1"' >> .git/hooks/commit-msg
   chmod +x .git/hooks/commit-msg

Or use `pre-commit <https://pre-commit.com/>`_ framework::

   # .pre-commit-config.yaml
   repos:
     - repo: local
       hooks:
         - id: validate-commit
           name: Validate Commit Message
           entry: ./scripts/validate-commit.sh
           language: script
           stages: [commit-msg]

Troubleshooting
===============

"No tags found"
---------------

If you see "No tags found" errors::

   # Create initial tag
   git tag -a v1.0.0 -m "Initial version"
   git push origin v1.0.0

Wrong version suggested
-----------------------

The script analyzes commits since last tag. If suggestion is wrong::

   # Check what commits it's seeing
   ./scripts/version.sh check
   
   # Manually specify version
   ./scripts/version.sh bump patch "Fix version"

Can't push tags
---------------

If ``git push --tags`` fails::

   # Push branch and tags separately
   git push origin trunk
   git push origin --tags
   
   # Or force if needed (careful!)
   git push origin v1.9.0 --force

Want to change last tag
------------------------

If you tagged wrong version::

   # Delete tag locally and remotely
   git tag -d v1.9.0
   git push origin :refs/tags/v1.9.0
   
   # Create correct tag
   ./scripts/version.sh tag 1.9.0 "Correct version"
   git push origin v1.9.0

Forgot to use conventional commits
-----------------------------------

It's okay! You can::

   1. Use ``suggest`` command anyway (will suggest patch bump)
   2. Manually specify version: ``./scripts/version.sh bump minor "Summary"``
   3. Start using conventional commits going forward

Reference
=========

Links
-----

- `Semantic Versioning <https://semver.org/>`_
- `Conventional Commits <https://www.conventionalcommits.org/>`_
- `Keep a Changelog <https://keepachangelog.com/>`_

Ada Scripts
-----------

- ``scripts/version.sh`` - Version management
- ``scripts/changelog.sh`` - Changelog generation
- ``scripts/validate-commit.sh`` - Commit message validation

Files
-----

- ``pyproject.toml`` - Contains ``version = "X.Y.Z"``
- ``ada_main.py`` - Contains ``@click.version_option(version="X.Y.Z")``
- ``CHANGELOG.md`` - Human-readable changelog
- ``.git/hooks/commit-msg`` - Optional commit validation hook

---

**Last Updated:** 2025-12-16  
**Ada Version:** 1.8.0
