# Documentation Cleanup Notes

## Status: 2025-12-16

### Markdown Files in docs/

The following Markdown files exist in `docs/` but should ideally be RST for Sphinx consistency:

- `SPECIALISTS.md` → Should be `specialists.rst` (already exists!)
- `BIDIRECTIONAL_SPECIALISTS.md` → Content should be in `specialists.rst`
- `SPECIALIST_RAG_DOCS.md` → Content should be in `specialists.rst`
- `WEB_SEARCH_SPECIALIST.md` → Content should be in `specialists.rst`

**Recommendation:** These appear to be working notes that have been superseded by the proper `specialists.rst` file. Consider:
1. Consolidating unique content into `specialists.rst`
2. Removing the `.md` files
3. Or moving them to a `docs/notes/` directory if they're drafts

### Current State

✅ **Well-Organized:**
- Main Sphinx docs are in `.rst` format
- Machine docs properly in `.ai/`
- Source annotations in place
- Testing infrastructure complete

⚠️  **Minor Cleanup:**
- Duplicate content in `.md` files in `docs/`
- Could consolidate specialist documentation

### Action Items (Optional)

**Low Priority:**
1. Review `.md` files in `docs/` for unique content
2. Merge into appropriate `.rst` files
3. Remove duplicates
4. Update any internal references

**No Rush:** The existing `.rst` files are comprehensive. The `.md` files appear to be historical drafts.

---

**Note:** This is informational only. System is fully functional as-is. Cleanup is for consistency, not correctness.
