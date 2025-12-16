#!/usr/bin/env bash
# Pre-commit hook to validate AI documentation consistency
#
# Install this hook by copying to .git/hooks/pre-commit:
#   cp scripts/pre-commit-ai-docs.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Or symlink it:
#   ln -s ../../scripts/pre-commit-ai-docs.sh .git/hooks/pre-commit

set -e

echo "🔍 Validating AI documentation..."

# Check if any brain modules or documentation changed
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

BRAIN_CHANGED=$(echo "$CHANGED_FILES" | grep -q "^brain/" && echo "yes" || echo "no")
AI_DOCS_CHANGED=$(echo "$CHANGED_FILES" | grep -q "^\.ai/" && echo "yes" || echo "no")

if [ "$BRAIN_CHANGED" = "yes" ] || [ "$AI_DOCS_CHANGED" = "yes" ]; then
    echo "  Brain modules or .ai/ docs changed, running validation..."
    
    # Run the linter
    if python scripts/lint_ai_docs.py --quiet; then
        echo "  ✅ Documentation validation passed"
    else
        echo "  ❌ Documentation validation failed!"
        echo ""
        echo "  Run 'python scripts/lint_ai_docs.py' for details"
        echo "  or skip with: git commit --no-verify"
        exit 1
    fi
else
    echo "  ℹ️  No brain modules or docs changed, skipping validation"
fi

echo "✅ Pre-commit checks passed"
