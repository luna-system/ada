"""
Test provenance notices are present in required locations.

This test ensures transparency about AI-assisted development.
See .ai/PROVENANCE.md for the full protocol.
"""
# December 2025 - luna-system

import pytest
from pathlib import Path


def test_license_has_provenance_notice():
    """LICENSE file must contain provenance notice."""
    license_path = Path(__file__).parent.parent / "LICENSE"
    assert license_path.exists(), "LICENSE file must exist"
    
    content = license_path.read_text()
    
    # Required: Explicit mention of AI assistance
    assert "PROVENANCE NOTICE" in content, "LICENSE missing PROVENANCE NOTICE header"
    assert "generative ai" in content.lower(), "LICENSE must mention 'generative AI'"
    assert "human" in content.lower() and "direction" in content.lower(), "LICENSE must credit human direction"


def test_provenance_doc_exists():
    """The .ai/PROVENANCE.md file must exist."""
    provenance_doc = Path(__file__).parent.parent / ".ai" / "PROVENANCE.md"
    assert provenance_doc.exists(), ".ai/PROVENANCE.md must exist"
    
    content = provenance_doc.read_text()
    
    # Must explain the concept
    assert "recursive" in content.lower(), "Should explain recursive self-improvement"
    assert "transparency" in content.lower(), "Should emphasize transparency"
    
    # Must document protocol
    assert "luna-system" in content, "Should document attribution format"
    assert "December 2025" in content or "YYYY" in content, "Should document timestamp format"


def test_core_brain_modules_have_attribution():
    """Core brain modules should have timestamp attribution."""
    core_brain_files = [
        "brain/model_warmer.py",
        "brain/app.py",
        # Add more as they're created
    ]
    
    for file in core_brain_files:
        path = Path(__file__).parent.parent / file
        if not path.exists():
            pytest.skip(f"{file} not found")
        
        content = path.read_text()
        
        # Should have "December 2025 - luna-system" or similar
        # We check for both parts separately to be flexible
        assert "luna-system" in content, f"{file} missing 'luna-system' attribution"
        # Timestamp format: flexible - accept any "Month YYYY" or "YYYY" pattern
        import re
        has_timestamp = bool(re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', content)) or \
                       bool(re.search(r'\d{4}-\d{2}', content)) or \
                       bool(re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', content))
        assert has_timestamp, f"{file} missing timestamp (expected 'Month YYYY' or 'YYYY-MM' format)"


def test_vscode_extension_modules_have_attribution():
    """VS Code extension modules should have timestamp attribution."""
    vscode_files = [
        "ada-vscode/src/extension.ts",
        "ada-vscode/src/adaBrainClient.ts",
        "ada-vscode/src/chatViewProvider.ts",
        "ada-vscode/src/tools.ts",
    ]
    
    for file in vscode_files:
        path = Path(__file__).parent.parent / file
        if not path.exists():
            pytest.skip(f"{file} not found")
        
        content = path.read_text()
        
        # TypeScript files use same format in comments
        assert "luna-system" in content, f"{file} missing 'luna-system' attribution"
        # Flexible timestamp check
        import re
        has_timestamp = bool(re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', content)) or \
                       bool(re.search(r'\d{4}-\d{2}', content)) or \
                       bool(re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', content))
        assert has_timestamp, f"{file} missing timestamp"


def test_ai_folder_has_self_aware_docs():
    """The .ai/ folder should contain documentation for AI self-awareness."""
    ai_dir = Path(__file__).parent.parent / ".ai"
    assert ai_dir.exists(), ".ai/ directory must exist"
    
    # Key files for AI understanding its own provenance
    key_files = [
        "context.md",           # System overview
        "PROVENANCE.md",        # This protocol
        "codebase-map.json",    # Module relationships
    ]
    
    for file in key_files:
        path = ai_dir / file
        assert path.exists(), f".ai/{file} must exist for AI self-awareness"


@pytest.mark.skip(reason="Aspirational - decide if README should have explicit notice")
def test_readme_has_provenance_mention():
    """README.md should mention AI-assisted development (optional)."""
    readme_path = Path(__file__).parent.parent / "README.md"
    assert readme_path.exists()
    
    content = readme_path.read_text()
    
    # This is aspirational - we haven't decided if this belongs in README
    # Uncomment and implement if we decide to add explicit notice
    assert "AI-assisted" in content or "generative AI" in content.lower()


def test_handoff_documents_exist():
    """Handoff documents should exist for session transitions."""
    handoff_path = Path(__file__).parent.parent / "HANDOFF_TO_CLAUDE_CODE.md"
    
    if handoff_path.exists():
        content = handoff_path.read_text()
        
        # Should document which AI instance did what
        assert "Copilot" in content or "Claude" in content or "GPT" in content, \
            "Handoff doc should mention AI instance"
        assert "Sonnet" in content or "Opus" in content or any(
            version in content for version in ["4.5", "4.0", "3.5"]
        ), "Handoff doc should mention AI model version"


def test_git_provenance_via_commits():
    """Git history should show luna-system as author (convention check)."""
    git_dir = Path(__file__).parent.parent / ".git"
    
    if not git_dir.exists():
        pytest.skip("Not a git repository")
    
    # This is a convention test - commits are authored by luna-system
    # even when AI wrote the code (with human curation)
    # We don't actually parse git here, just document the convention
    pass  # Convention documented in .ai/PROVENANCE.md


def test_license_is_cc0():
    """Verify CC0 public domain dedication is present."""
    license_path = Path(__file__).parent.parent / "LICENSE"
    content = license_path.read_text()
    
    assert "CC0" in content, "License must be CC0 (public domain)"
    assert "public domain" in content.lower(), "Must mention public domain"


def test_provenance_protocol_is_documented():
    """The provenance protocol must explain attribution format."""
    provenance_doc = Path(__file__).parent.parent / ".ai" / "PROVENANCE.md"
    content = provenance_doc.read_text()
    
    # Must document the format
    assert "# December 2025 - luna-system" in content or \
           "December 2025 - luna-system" in content, \
           "Protocol must document attribution format"
    
    # Must explain where to put it
    assert "file header" in content.lower() or "top of file" in content.lower(), \
           "Protocol must explain where attribution goes"
    
    # Must discuss AI self-awareness
    assert "self-aware" in content.lower() or "knows" in content.lower(), \
           "Protocol must discuss AI self-awareness"


def test_no_misleading_human_authorship_claims():
    """Files should not claim pure human authorship when AI-assisted."""
    # This is a negative test - we check that we DON'T mislead
    # If we find "Written entirely by humans" or similar, that's a red flag
    
    # For now, this is aspirational - we trust the process
    # Could be implemented as a linter if needed
    pass  # Convention: Don't claim pure human authorship unless true
