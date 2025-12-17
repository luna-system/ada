#!/usr/bin/env bash
# Validate commit message follows Conventional Commits
# Can be used as pre-commit hook or standalone validation

set -euo pipefail

COMMIT_MSG_FILE="${1:-}"

if [[ -z "$COMMIT_MSG_FILE" ]]; then
    echo "Usage: $0 <commit_msg_file>"
    echo "Or install as pre-commit hook:"
    echo "  ln -sf ../../scripts/validate-commit.sh .git/hooks/commit-msg"
    exit 1
fi

COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Allow merge commits
if echo "$COMMIT_MSG" | grep -qE "^Merge (branch|pull request)"; then
    exit 0
fi

# Allow revert commits
if echo "$COMMIT_MSG" | grep -qE "^Revert "; then
    exit 0
fi

# Validate Conventional Commits format
# Type: feat, fix, docs, style, refactor, perf, test, chore, ci, build
# Format: type(scope): subject
# Scope is optional
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\([a-z0-9-]+\))?: .+"; then
    cat <<EOF

❌ Invalid commit message format!

Your commit message must follow Conventional Commits:
  type(scope): subject

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  style:    Code style (formatting, no logic change)
  refactor: Code refactoring
  perf:     Performance improvements
  test:     Adding or updating tests
  chore:    Maintenance tasks
  ci:       CI/CD changes
  build:    Build system changes

Examples:
  feat: add Nix flake support
  fix(matrix): handle rate limiting
  docs: update getting started guide
  chore: bump version to v1.8.0

Scope is optional but recommended:
  feat(specialists): add Wikipedia search specialist
  fix(rag): improve memory retrieval accuracy

Your message:
  $COMMIT_MSG

EOF
    exit 1
fi

# Check subject line isn't too long (recommended 50 chars, max 72)
SUBJECT=$(echo "$COMMIT_MSG" | head -n1)
SUBJECT_LEN=${#SUBJECT}

if [[ $SUBJECT_LEN -gt 72 ]]; then
    echo "⚠️  Warning: Subject line is $SUBJECT_LEN chars (recommended max 72)"
    echo "   Consider making it more concise"
    echo
fi

# Check subject doesn't end with period
if echo "$SUBJECT" | grep -qE "\.$"; then
    echo "⚠️  Warning: Subject line shouldn't end with a period"
    echo
fi

# Check subject uses imperative mood (starts with lowercase)
TYPE=$(echo "$SUBJECT" | cut -d: -f1)
SUBJECT_TEXT=$(echo "$SUBJECT" | cut -d: -f2- | sed 's/^ *//')
FIRST_WORD=$(echo "$SUBJECT_TEXT" | awk '{print $1}')

if [[ "$FIRST_WORD" =~ ^[A-Z] ]]; then
    # Check if it's not an acronym or proper noun
    if [[ ${#FIRST_WORD} -gt 1 ]] && ! echo "$FIRST_WORD" | grep -qE "^[A-Z]+$"; then
        echo "⚠️  Warning: Use imperative mood (lowercase start) in subject"
        echo "   Try: ${TYPE}: $(echo "$FIRST_WORD" | tr '[:upper:]' '[:lower:]')${SUBJECT_TEXT#$FIRST_WORD}"
        echo
    fi
fi

exit 0
