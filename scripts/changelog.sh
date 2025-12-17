#!/usr/bin/env bash
# Changelog generation from Conventional Commits
# Usage: ./scripts/changelog.sh [from_version] [to_version]
# Example: ./scripts/changelog.sh v1.7.0 v1.8.0

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to latest tag if not specified
FROM_VERSION="${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo "")}"
TO_VERSION="${2:-HEAD}"

if [[ -z "$FROM_VERSION" ]]; then
    echo -e "${RED}Error: No tags found. Please specify a from_version.${NC}"
    exit 1
fi

echo -e "${BLUE}Generating changelog from ${FROM_VERSION} to ${TO_VERSION}${NC}"
echo

# Function to extract commits by type
get_commits_by_type() {
    local type="$1"
    local prefix="$2"
    git log --pretty=format:"%s" "${FROM_VERSION}..${TO_VERSION}" \
        | grep "^${type}:" \
        | sed "s/^${type}: //" \
        | sed "s/^/${prefix}/"
}

# Function to get commit count
count_commits_by_type() {
    local type="$1"
    git log --pretty=format:"%s" "${FROM_VERSION}..${TO_VERSION}" \
        | grep "^${type}:" | wc -l
}

# Generate changelog sections
echo "## [$TO_VERSION] - $(date +%Y-%m-%d)"
echo

# Features
FEAT_COUNT=$(count_commits_by_type "feat")
if [[ "$FEAT_COUNT" -gt 0 ]]; then
    echo "### ✨ Features"
    get_commits_by_type "feat" "- "
    echo
fi

# Fixes
FIX_COUNT=$(count_commits_by_type "fix")
if [[ "$FIX_COUNT" -gt 0 ]]; then
    echo "### 🐛 Bug Fixes"
    get_commits_by_type "fix" "- "
    echo
fi

# Documentation
DOCS_COUNT=$(count_commits_by_type "docs")
if [[ "$DOCS_COUNT" -gt 0 ]]; then
    echo "### 📚 Documentation"
    get_commits_by_type "docs" "- "
    echo
fi

# Performance
PERF_COUNT=$(count_commits_by_type "perf")
if [[ "$PERF_COUNT" -gt 0 ]]; then
    echo "### ⚡ Performance"
    get_commits_by_type "perf" "- "
    echo
fi

# Refactoring
REFACTOR_COUNT=$(count_commits_by_type "refactor")
if [[ "$REFACTOR_COUNT" -gt 0 ]]; then
    echo "### ♻️ Refactoring"
    get_commits_by_type "refactor" "- "
    echo
fi

# Tests
TEST_COUNT=$(count_commits_by_type "test")
if [[ "$TEST_COUNT" -gt 0 ]]; then
    echo "### 🧪 Tests"
    get_commits_by_type "test" "- "
    echo
fi

# Chores
CHORE_COUNT=$(count_commits_by_type "chore")
if [[ "$CHORE_COUNT" -gt 0 ]]; then
    echo "### 🔧 Maintenance"
    get_commits_by_type "chore" "- "
    echo
fi

# Summary
TOTAL=$((FEAT_COUNT + FIX_COUNT + DOCS_COUNT + PERF_COUNT + REFACTOR_COUNT + TEST_COUNT + CHORE_COUNT))
echo "---"
echo -e "${GREEN}Total commits: $TOTAL${NC}"
echo -e "  Features: $FEAT_COUNT | Fixes: $FIX_COUNT | Docs: $DOCS_COUNT"
echo -e "  Perf: $PERF_COUNT | Refactor: $REFACTOR_COUNT | Tests: $TEST_COUNT | Chores: $CHORE_COUNT"
