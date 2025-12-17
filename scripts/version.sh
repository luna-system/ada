#!/usr/bin/env bash
# Ada Version Management Helper
# Automates version bumping and tagging according to semantic versioning

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PYPROJECT="pyproject.toml"
ADA_MAIN="ada_main.py"

# Get current version from pyproject.toml
get_current_version() {
    grep "^version = " "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/'
}

# Parse version into major.minor.patch
parse_version() {
    local version=$1
    IFS='.' read -r -a parts <<< "$version"
    echo "${parts[0]}" "${parts[1]}" "${parts[2]}"
}

# Bump version
bump_version() {
    local current=$1
    local bump_type=$2
    
    read major minor patch <<< $(parse_version "$current")
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Invalid bump type: $bump_type"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Update version in files
update_version_files() {
    local new_version=$1
    
    # Update pyproject.toml
    sed -i "s/^version = \".*\"/version = \"$new_version\"/" "$PYPROJECT"
    
    # Update ada_main.py if it has a version
    if grep -q "@click.version_option" "$ADA_MAIN"; then
        sed -i "s/@click.version_option(version=\".*\"/@click.version_option(version=\"$new_version\"/" "$ADA_MAIN"
    fi
    
    echo -e "${GREEN}✓${NC} Updated version to $new_version in:"
    echo "  - $PYPROJECT"
    echo "  - $ADA_MAIN"
}

# Create git tag
create_tag() {
    local version=$1
    local message=$2
    
    git add "$PYPROJECT" "$ADA_MAIN"
    git commit -m "chore: bump version to v$version

$message"
    
    git tag -a "v$version" -m "Version $version

$message"
    
    echo -e "${GREEN}✓${NC} Created tag v$version"
}

# Show usage
usage() {
    cat << EOF
${BLUE}Ada Version Management${NC}

Usage: $0 <command> [options]

Commands:
  current               Show current version
  bump <type> [msg]     Bump version and create tag
                        Types: major, minor, patch
  tag <version> [msg]   Create tag for specific version (without bumping files)
  check                 Check for untagged commits since last version
  suggest               Suggest next version based on commits
  changelog             Generate changelog for next release
  
Examples:
  $0 current
  $0 suggest
  $0 bump minor "Add Nix flake support"
  $0 changelog
  $0 bump patch "Fix locale issues"
  $0 tag 1.7.0 "Orchestration guides"
  $0 check

Semantic Versioning Guide:
  - ${YELLOW}major${NC}: Breaking changes (API incompatibility)
  - ${GREEN}minor${NC}: New features (backwards compatible)
  - ${BLUE}patch${NC}: Bug fixes (backwards compatible)

EOF
}

# Check for untagged commits
check_untagged() {
    local current_version=$(get_current_version)
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    
    if [ -z "$last_tag" ]; then
        echo -e "${YELLOW}⚠${NC} No tags found"
        return
    fi
    
    local commits_since=$(git log $last_tag..HEAD --oneline | wc -l)
    
    echo -e "${BLUE}Current version:${NC} $current_version"
    echo -e "${BLUE}Last tag:${NC} $last_tag"
    echo -e "${BLUE}Commits since tag:${NC} $commits_since"
    echo ""
    
    if [ $commits_since -gt 0 ]; then
        echo -e "${YELLOW}Untagged commits:${NC}"
        git log $last_tag..HEAD --oneline --pretty=format:"  %h %s"
        echo ""
        echo ""
        echo -e "${YELLOW}💡 Consider tagging a new version!${NC}"
    else
        echo -e "${GREEN}✓${NC} All commits are tagged"
    fi
}

suggest_version() {
    echo -e "${BLUE}Analyzing commits to suggest next version...${NC}"
    echo ""
    
    current=$(get_current_version)
    latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v${current}")
    
    echo "Current version: $current"
    echo "Latest tag: $latest_tag"
    echo ""
    
    # Count commit types since last tag
    breaking=$(git log --pretty=format:"%B" "${latest_tag}..HEAD" 2>/dev/null | grep "BREAKING CHANGE" | wc -l)
    feat=$(git log --pretty=format:"%s" "${latest_tag}..HEAD" 2>/dev/null | grep "^feat" | wc -l)
    fix=$(git log --pretty=format:"%s" "${latest_tag}..HEAD" 2>/dev/null | grep "^fix" | wc -l)
    perf=$(git log --pretty=format:"%s" "${latest_tag}..HEAD" 2>/dev/null | grep "^perf" | wc -l)
    
    echo "Commit analysis:"
    echo "  Breaking changes: $breaking"
    echo "  Features: $feat"
    echo "  Fixes: $fix"
    echo "  Performance: $perf"
    echo ""
    
    # Parse current version
    read major minor patch <<< $(parse_version "$current")
    
    # Suggest bump type
    if [[ $breaking -gt 0 ]]; then
        suggested_type="major"
        new_major=$((major + 1))
        suggested_version="${new_major}.0.0"
        echo -e "${GREEN}Suggestion: MAJOR bump → $suggested_version${NC}"
        echo "Reason: Breaking changes detected"
    elif [[ $feat -gt 0 ]] || [[ $perf -gt 0 ]]; then
        suggested_type="minor"
        new_minor=$((minor + 1))
        suggested_version="${major}.${new_minor}.0"
        echo -e "${GREEN}Suggestion: MINOR bump → $suggested_version${NC}"
        echo "Reason: New features or performance improvements"
    elif [[ $fix -gt 0 ]]; then
        suggested_type="patch"
        new_patch=$((patch + 1))
        suggested_version="${major}.${minor}.${new_patch}"
        echo -e "${GREEN}Suggestion: PATCH bump → $suggested_version${NC}"
        echo "Reason: Bug fixes only"
    else
        echo -e "${YELLOW}No version bump suggested (no feat/fix/perf commits)${NC}"
        return
    fi
    
    echo ""
    echo "To apply:"
    echo -e "  ${BLUE}./scripts/version.sh bump $suggested_type \"Version $suggested_version\"${NC}"
}

generate_changelog() {
    echo -e "${BLUE}Generating changelog for next release...${NC}"
    echo ""
    
    latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [[ -z "$latest_tag" ]]; then
        echo -e "${RED}Error: No tags found. Cannot generate changelog.${NC}"
        exit 1
    fi
    
    echo "Changelog since $latest_tag:"
    echo "================================"
    echo ""
    
    # Run the changelog script
    changelog_script="$(dirname "$0")/changelog.sh"
    if [[ -x "$changelog_script" ]]; then
        "$changelog_script" "$latest_tag" "HEAD"
    else
        echo -e "${RED}Error: scripts/changelog.sh not found or not executable${NC}"
        exit 1
    fi
    
    echo ""
    echo "To update CHANGELOG.md:"
    echo -e "  ${BLUE}./scripts/changelog.sh $latest_tag HEAD | cat - CHANGELOG.md > CHANGELOG.md.tmp${NC}"
    echo -e "  ${BLUE}mv CHANGELOG.md.tmp CHANGELOG.md${NC}"
}

# Main command dispatch
case "${1:-}" in
    current)
        echo $(get_current_version)
        ;;
    
    bump)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Bump type required${NC}"
            usage
            exit 1
        fi
        
        current=$(get_current_version)
        new=$(bump_version "$current" "$2")
        message="${3:-Version bump}"
        
        echo -e "${BLUE}Bumping version:${NC} $current → $new"
        update_version_files "$new"
        create_tag "$new" "$message"
        
        echo ""
        echo -e "${GREEN}✓ Done!${NC} Version bumped to v$new"
        echo "Push with: git push origin trunk --tags"
        ;;
    
    tag)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Version required${NC}"
            usage
            exit 1
        fi
        
        version="$2"
        message="${3:-Version $version}"
        
        echo -e "${BLUE}Creating tag:${NC} v$version"
        git tag -a "v$version" -m "$message"
        
        echo -e "${GREEN}✓${NC} Created tag v$version"
        echo "Push with: git push origin trunk --tags"
        ;;
    
    check)
        check_untagged
        ;;
    
    suggest)
        suggest_version
        ;;
    
    changelog)
        generate_changelog
        ;;
    
    *)
        usage
        exit 1
        ;;
esac
