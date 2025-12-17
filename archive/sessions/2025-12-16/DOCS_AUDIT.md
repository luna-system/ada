# Ada Documentation Audit & Recommendations
**Date:** December 16, 2025  
**Branch:** feature/matrix-specialist

## Executive Summary

Found **40+ markdown files** across the repository. Many root-level docs should move to Sphinx, some are duplicates, and organization could be improved.

## 📊 Current State

### Root-Level Markdown (12 files)
```
AI.md                       - Pointer to .ai/ folder (54 lines)
API_DOCUMENTATION.md        - API docs (needs checking)
API_QUICK_REFERENCE.md      - API reference (needs checking)
BUILD_SETUP.md              - Build instructions (needs checking)
BUILDX_QUICKREF.md          - Docker buildx reference (needs checking)
COMMUNITY_GUIDELINES.md     - Full community guidelines (119 lines)
COMMUNITY_QUICK.md          - Quick version (25 lines)
GITHUB_SEO.md               - Meta: GitHub optimization
INTEGRATION_PLUGINS_PLAN.md - Working doc: specialist system plans
PRINCIPLES.md               - Project philosophy (needs checking)
prompt.md                   - Old persona file? (34 lines)
TESTING.md                  - Testing guide (needs checking)
```

### Existing Sphinx Docs (28 RST files)
```
✅ api_reference.rst        - Already exists!
✅ api_usage.rst            - Already exists!
✅ build_system.rst         - Already exists!
✅ testing.rst              - Already exists!
✅ architecture.rst         - Already exists!
✅ development.rst          - Already exists!
... and 22 more
```

### Package-Level Markdown (Correct)
```
ada-mcp/README.md           ✅ Package readme
ada-mcp/QUICKSTART.md       ✅ Quick start guide
ada-mcp/TESTING.md          ✅ Testing specific to package
matrix-bridge/README.md     ✅ Bridge readme
adapters/cli/README.md      ✅ Adapter readme
scripts/README.md           ✅ Scripts readme
```

## 🔍 Detailed Analysis

### 1. Duplicate Content (HIGH PRIORITY)

#### Root TESTING.md vs docs/testing.rst
**Action:** Check for overlap, merge, remove root file

#### API_DOCUMENTATION.md vs API_QUICK_REFERENCE.md vs docs/api_*.rst
**Action:** Check all four files, consolidate into docs/

#### COMMUNITY_GUIDELINES.md vs COMMUNITY_QUICK.md
**Status:** COMMUNITY_QUICK.md is intentional summary (25 lines)  
**Action:** Keep both OR move full version to docs/ and keep Quick in root

#### BUILD_SETUP.md vs BUILDX_QUICKREF.md vs docs/build_system.rst
**Action:** Check for overlap, merge into docs/build_system.rst

### 2. Files That Should Move to docs/ as RST

**High Priority:**
- [ ] **API_DOCUMENTATION.md** → Check vs docs/api_reference.rst
- [ ] **API_QUICK_REFERENCE.md** → Check vs docs/api_usage.rst  
- [ ] **BUILD_SETUP.md** → Merge into docs/build_system.rst
- [ ] **BUILDX_QUICKREF.md** → Merge into docs/build_system.rst
- [ ] **TESTING.md** → Merge into docs/testing.rst
- [ ] **PRINCIPLES.md** → docs/project_philosophy.rst (new)

**Medium Priority:**
- [ ] **docs/buildx_adoption_notes.md** → Convert to RST or integrate

### 3. Files to Review for Content

#### AI.md (54 lines)
**Current:** Pointer to .ai/ folder for AI assistants  
**Status:** Good! Links to machine docs  
**Action:** Keep as-is, it's useful

#### prompt.md (34 lines)
**Current:** Old persona definition?  
**Compare:** persona.md (runtime config)  
**Action:** Check if redundant with persona.md, possibly archive

#### INTEGRATION_PLUGINS_PLAN.md
**Current:** Working document for specialist system  
**Status:** Likely superseded by .ai/ docs  
**Action:** Archive or remove (info is in .ai/specialist-registry.json)

#### GITHUB_SEO.md
**Current:** Meta documentation about GitHub optimization  
**Action:** Keep (meta/process doc) OR move to .github/

### 4. Files That Are Fine ✅

**GitHub Configuration:**
- .github/copilot-instructions.md
- .github/ISSUES.md
- .github/ISSUE_TEMPLATE/*.md

**Package Documentation:**
- All README.md files in packages
- Package-specific QUICKSTART.md
- Package-specific TESTING.md

**Runtime Configuration:**
- persona.md (loaded by brain at runtime)

**Working Documents:**
- TODO.md (task tracking)

**Community Files:**
- COMMUNITY_GUIDELINES.md (or move to docs/)
- COMMUNITY_QUICK.md (intentional summary)

## 📋 Recommended Actions

### Phase 1: Immediate Cleanup (30 min)

1. **Check for duplicate content:**
   ```bash
   diff API_DOCUMENTATION.md docs/api_reference.rst
   diff API_QUICK_REFERENCE.md docs/api_usage.rst
   diff BUILD_SETUP.md docs/build_system.rst
   diff TESTING.md docs/testing.rst
   ```

2. **Archive working docs:**
   ```bash
   mkdir -p archive/
   mv INTEGRATION_PLUGINS_PLAN.md archive/
   ```

3. **Remove if redundant:**
   ```bash
   # After checking content
   git rm prompt.md  # If duplicate of persona.md
   ```

### Phase 2: Convert & Consolidate (1-2 hours)

1. **Convert PRINCIPLES.md to RST:**
   ```bash
   pandoc PRINCIPLES.md -f markdown -t rst -o docs/project_philosophy.rst
   # Edit for Sphinx formatting
   git rm PRINCIPLES.md
   ```

2. **Merge build docs:**
   - Integrate BUILD_SETUP.md content into docs/build_system.rst
   - Integrate BUILDX_QUICKREF.md content into docs/build_system.rst
   - Remove root files

3. **Consolidate API docs:**
   - Review all API documentation files
   - Ensure docs/api_reference.rst has all API spec content
   - Ensure docs/api_usage.rst has all usage examples
   - Remove redundant root files

4. **Update index.rst:**
   - Add project_philosophy.rst if created
   - Update TOC as needed

### Phase 3: Organization (30 min)

1. **Convert docs/buildx_adoption_notes.md:**
   ```bash
   cd docs/
   pandoc buildx_adoption_notes.md -t rst -o buildx_adoption_notes.rst
   # Add to build_system.rst as appendix
   git rm buildx_adoption_notes.md
   ```

2. **Move community guidelines** (optional):
   - Keep COMMUNITY_QUICK.md in root (GitHub best practice)
   - Move COMMUNITY_GUIDELINES.md → docs/community_guidelines.rst
   - Or keep both in root (also valid)

3. **Clean up GitHub meta docs:**
   ```bash
   mv GITHUB_SEO.md .github/SEO.md
   ```

## 🎯 Final Structure (Proposed)

```
/
├── README.md                        # Main readme (GitHub)
├── persona.md                       # Runtime config
├── TODO.md                          # Working doc
├── COMMUNITY_QUICK.md               # Quick guidelines (GitHub)
├── AI.md                            # Pointer to .ai/
│
├── .ai/                             # Machine-readable docs ✅
│   ├── *.md, *.json
│
├── docs/                            # Human-readable docs (Sphinx)
│   ├── getting_started.rst
│   ├── api_reference.rst            # Consolidated API spec
│   ├── api_usage.rst                # Consolidated API examples
│   ├── build_system.rst             # Consolidated build docs
│   ├── testing.rst                  # Consolidated testing
│   ├── project_philosophy.rst       # New: from PRINCIPLES.md
│   ├── community_guidelines.rst     # Optional: from root
│   └── ... (28 existing files)
│
├── .github/
│   ├── copilot-instructions.md
│   ├── ISSUES.md
│   ├── SEO.md                       # Moved from root
│   └── ISSUE_TEMPLATE/
│
├── ada-mcp/
│   ├── README.md                    ✅ Keep
│   ├── QUICKSTART.md                ✅ Keep
│   └── TESTING.md                   ✅ Keep
│
├── matrix-bridge/
│   ├── README.md                    ✅ Keep
│   └── QUICKSTART.md                ✅ Keep
│
└── archive/                         # Historical working docs
    └── INTEGRATION_PLUGINS_PLAN.md
```

## 🚦 Priority Levels

### 🔴 High Priority (Do First)
1. Check for duplicate content in API/BUILD/TESTING docs
2. Archive INTEGRATION_PLUGINS_PLAN.md (superseded)
3. Check if prompt.md is redundant

### 🟡 Medium Priority (Do Soon)
4. Convert PRINCIPLES.md → docs/project_philosophy.rst
5. Consolidate build documentation
6. Convert docs/buildx_adoption_notes.md

### 🟢 Low Priority (Nice to Have)
7. Move GITHUB_SEO.md → .github/SEO.md
8. Consider moving COMMUNITY_GUIDELINES.md to docs/

## 📝 Notes

### Why Sphinx (RST) for Main Docs?
- ✅ Cross-referencing between docs
- ✅ Search functionality
- ✅ Versioning support
- ✅ Professional rendering at /docs/
- ✅ PDF export capability
- ✅ Consistent with Python ecosystem

### Why Keep Some Markdown?
- ✅ GitHub renders markdown in repo browser
- ✅ Package README.md is standard practice
- ✅ Issue templates require markdown
- ✅ Some files are runtime configs

### What About .ai/ Folder?
- ✅ Keep all as markdown/JSON
- ✅ Optimized for machine parsing
- ✅ Different audience than docs/

## 🔧 Quick Commands

```bash
# Find duplicates
diff -u API_DOCUMENTATION.md docs/api_reference.rst | head -20

# Convert markdown to RST
pandoc INPUT.md -f markdown -t rst -o OUTPUT.rst

# Check file sizes
wc -l *.md | sort -n

# Find all markdown files
find . -name "*.md" -not -path "./.ai/*" -not -path "./node_modules/*"

# Rebuild Sphinx docs after changes
cd docs/ && make clean && make html
```

## ✅ Success Criteria

After cleanup:
- [ ] No duplicate documentation
- [ ] All user-facing docs in docs/ as RST
- [ ] All package docs remain as README.md
- [ ] Clear separation: docs/ (human) vs .ai/ (machine)
- [ ] Sphinx docs build without warnings
- [ ] Main README.md points to docs/ for details

---

**Next Steps:** Review this audit, then execute Phase 1 to identify duplicates!
