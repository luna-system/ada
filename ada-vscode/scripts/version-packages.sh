#!/bin/bash
# Version all packages in monorepo atomically
# Usage: ./version-packages.sh [major|minor|patch]

set -e

BUMP_TYPE="${1:-patch}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔢 Versioning Ada VS Code monorepo packages ($BUMP_TYPE bump)..."

cd "$MONOREPO_ROOT"

# Get current version from root package.json
CURRENT_VERSION=$(jq -r '.version' package.json)
echo "Current version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

case "$BUMP_TYPE" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
  *)
    echo "❌ Invalid bump type: $BUMP_TYPE"
    echo "Usage: $0 [major|minor|patch]"
    exit 1
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update root package.json
echo "📝 Updating root package.json..."
jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
mv package.json.tmp package.json

# Update workspace packages
for PKG_DIR in packages/*/; do
  if [ -f "$PKG_DIR/package.json" ]; then
    PKG_NAME=$(basename "$PKG_DIR")
    echo "📝 Updating $PKG_NAME..."
    
    cd "$PKG_DIR"
    jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
    mv package.json.tmp package.json
    cd "$MONOREPO_ROOT"
  fi
done

echo "✅ All packages bumped to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Build: pnpm build"
echo "  3. Commit: git commit -am \"chore: bump to v$NEW_VERSION\""
echo "  4. Tag: git tag -a v$NEW_VERSION -m \"Release v$NEW_VERSION\""
echo "  5. Push: git push && git push --tags"
