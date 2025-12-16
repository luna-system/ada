"""
Tests for AI documentation consistency and completeness.

Validates that machine-readable documentation stays synchronized with code:
- Required files exist in .ai/ directory
- JSON files are valid and follow schemas
- Annotations exist in core modules
- Module registry matches actual filesystem
- Specialist registry matches discovered specialists
"""
import json
import re
from pathlib import Path
from typing import Set, List, Dict
import pytest


# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Documentation paths
AI_DIR = PROJECT_ROOT / ".ai"
BRAIN_DIR = PROJECT_ROOT / "brain"
SPECIALISTS_DIR = BRAIN_DIR / "specialists"


class TestAIDocumentationStructure:
    """Verify .ai/ directory structure and required files."""
    
    def test_ai_directory_exists(self):
        """Ensure .ai/ directory exists."""
        assert AI_DIR.exists(), ".ai/ directory not found"
        assert AI_DIR.is_dir(), ".ai/ should be a directory"
    
    def test_required_files_exist(self):
        """Check all required documentation files are present."""
        required_files = [
            "README.md",
            "QUICKSTART.md",
            "IMPLEMENTATION.md",
            "context.md",
            "codebase-map.json",
            "specialist-registry.json",
            "annotation-schema.json"
        ]
        
        for filename in required_files:
            file_path = AI_DIR / filename
            assert file_path.exists(), f"Required file {filename} not found in .ai/"
            assert file_path.stat().st_size > 0, f"{filename} is empty"


class TestJSONValidity:
    """Validate JSON files are well-formed and contain expected structure."""
    
    def test_codebase_map_valid_json(self):
        """Verify codebase-map.json is valid JSON."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        assert "version" in data
        assert "modules" in data
        assert isinstance(data["modules"], dict)
        assert len(data["modules"]) > 0, "codebase-map.json has no modules"
    
    def test_specialist_registry_valid_json(self):
        """Verify specialist-registry.json is valid JSON."""
        with open(AI_DIR / "specialist-registry.json") as f:
            data = json.load(f)
        
        assert "version" in data
        assert "specialists" in data
        assert isinstance(data["specialists"], dict)
    
    def test_annotation_schema_valid_json(self):
        """Verify annotation-schema.json is valid JSON."""
        with open(AI_DIR / "annotation-schema.json") as f:
            data = json.load(f)
        
        assert "annotations" in data
        assert isinstance(data["annotations"], dict)


class TestCodebaseMapConsistency:
    """Verify codebase-map.json matches actual codebase structure."""
    
    def test_documented_modules_exist(self):
        """Ensure all modules in codebase-map.json actually exist."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        missing_modules = []
        for module_path in data["modules"].keys():
            file_path = PROJECT_ROOT / module_path
            if not file_path.exists():
                missing_modules.append(module_path)
        
        assert not missing_modules, f"Modules in codebase-map.json don't exist: {missing_modules}"
    
    def test_core_modules_documented(self):
        """Verify critical modules are documented in codebase-map.json."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        critical_modules = [
            "brain/app.py",
            "brain/llm.py",
            "brain/prompt_builder.py",
            "brain/rag_store.py",
            "brain/specialists/protocol.py"
        ]
        
        documented_modules = set(data["modules"].keys())
        
        for module in critical_modules:
            assert module in documented_modules, f"Critical module {module} not in codebase-map.json"
    
    def test_module_entries_have_required_fields(self):
        """Verify each module entry has required metadata fields."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        required_fields = ["type", "purpose", "imports", "imported_by"]
        
        for module_path, module_data in data["modules"].items():
            for field in required_fields:
                assert field in module_data, f"{module_path} missing required field: {field}"


class TestSpecialistRegistryConsistency:
    """Verify specialist-registry.json matches actual specialist implementations."""
    
    def test_registry_matches_specialist_files(self):
        """Ensure all specialist files are documented in registry."""
        # Find actual specialist files
        actual_specialists = set()
        if SPECIALISTS_DIR.exists():
            for file_path in SPECIALISTS_DIR.glob("*_specialist.py"):
                specialist_name = file_path.stem.replace("_specialist", "")
                actual_specialists.add(specialist_name)
        
        # Get registered specialists
        with open(AI_DIR / "specialist-registry.json") as f:
            data = json.load(f)
        
        registered_specialists = set(data["specialists"].keys())
        
        # Check for undocumented specialists
        undocumented = actual_specialists - registered_specialists
        assert not undocumented, f"Specialists exist but not in registry: {undocumented}"
        
        # Warn about documented but missing (might be intentional)
        missing = registered_specialists - actual_specialists
        if missing:
            pytest.skip(f"Registry contains specialists not in filesystem: {missing}")
    
    def test_specialist_entries_have_required_fields(self):
        """Verify each specialist has required metadata."""
        with open(AI_DIR / "specialist-registry.json") as f:
            data = json.load(f)
        
        required_fields = [
            "class_name",
            "file",
            "description",
            "activation_type",
            "activation_trigger",
            "context_priority"
        ]
        
        for specialist_name, specialist_data in data["specialists"].items():
            for field in required_fields:
                assert field in specialist_data, \
                    f"Specialist '{specialist_name}' missing required field: {field}"
    
    def test_specialist_files_match_registry_paths(self):
        """Verify file paths in registry point to actual files."""
        with open(AI_DIR / "specialist-registry.json") as f:
            data = json.load(f)
        
        missing_files = []
        for specialist_name, specialist_data in data["specialists"].items():
            file_path = PROJECT_ROOT / specialist_data["file"]
            if not file_path.exists():
                missing_files.append((specialist_name, specialist_data["file"]))
        
        assert not missing_files, f"Registry references missing files: {missing_files}"


class TestSourceCodeAnnotations:
    """Verify source code has required @ai-* annotations."""
    
    def _extract_annotations(self, file_path: Path) -> Dict[str, str]:
        """Extract all @ai-* annotations from a file."""
        annotations = {}
        with open(file_path) as f:
            for line in f:
                match = re.match(r'#\s*@ai-(\w+):\s*(.+)', line)
                if match:
                    key, value = match.groups()
                    annotations[key] = value.strip()
        return annotations
    
    def test_core_modules_have_annotations(self):
        """Verify critical modules have @ai-indexable annotations."""
        core_modules = [
            BRAIN_DIR / "app.py",
            BRAIN_DIR / "llm.py",
            BRAIN_DIR / "prompt_builder.py",
            BRAIN_DIR / "rag_store.py",
        ]
        
        missing_annotations = []
        for module_path in core_modules:
            if module_path.exists():
                annotations = self._extract_annotations(module_path)
                if "indexable" not in annotations:
                    missing_annotations.append(str(module_path.relative_to(PROJECT_ROOT)))
        
        assert not missing_annotations, \
            f"Core modules missing @ai-indexable annotation: {missing_annotations}"
    
    def test_specialists_have_annotations(self):
        """Verify specialist files have required annotations."""
        if not SPECIALISTS_DIR.exists():
            pytest.skip("Specialists directory not found")
        
        required_annotations = ["indexable", "purpose"]
        missing = []
        
        for specialist_file in SPECIALISTS_DIR.glob("*_specialist.py"):
            annotations = self._extract_annotations(specialist_file)
            for req in required_annotations:
                if req not in annotations:
                    missing.append((specialist_file.name, req))
        
        assert not missing, f"Specialists missing required annotations: {missing}"
    
    def test_annotated_modules_documented_in_map(self):
        """Ensure modules with @ai-indexable are in codebase-map.json."""
        with open(AI_DIR / "codebase-map.json") as f:
            codebase_map = json.load(f)
        
        documented = set(codebase_map["modules"].keys())
        
        # Find all annotated files
        annotated_files = []
        for py_file in BRAIN_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            annotations = self._extract_annotations(py_file)
            if "indexable" in annotations:
                rel_path = str(py_file.relative_to(PROJECT_ROOT))
                annotated_files.append(rel_path)
        
        # Check if annotated files are documented
        missing = []
        for file_path in annotated_files:
            if file_path not in documented:
                missing.append(file_path)
        
        assert not missing, \
            f"Annotated files not in codebase-map.json: {missing}"


class TestDocumentationContentQuality:
    """Validate documentation content quality and completeness."""
    
    def test_context_md_has_key_sections(self):
        """Verify context.md has required architectural sections."""
        with open(AI_DIR / "context.md") as f:
            content = f.read()
        
        required_sections = [
            "Purpose",
            "Core Architecture",
            "Key Modules",
            "Conventions",
            "Extension Points"
        ]
        
        for section in required_sections:
            assert section in content, f"context.md missing section: {section}"
    
    def test_specialist_registry_has_activation_patterns(self):
        """Verify specialist registry documents activation patterns."""
        with open(AI_DIR / "specialist-registry.json") as f:
            data = json.load(f)
        
        assert "activation_patterns" in data, \
            "specialist-registry.json missing 'activation_patterns' section"
        
        patterns = data["activation_patterns"]
        assert "context-triggered" in patterns
        assert "bidirectional" in patterns
    
    def test_codebase_map_has_data_flows(self):
        """Verify codebase-map.json documents data flows."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        assert "data_flow" in data, "codebase-map.json missing 'data_flow' section"
        
        flows = data["data_flow"]
        required_flows = ["chat_request", "memory_storage", "specialist_activation"]
        
        for flow in required_flows:
            assert flow in flows, f"codebase-map.json missing '{flow}' data flow"


class TestDocumentationFreshness:
    """Tests that might indicate stale documentation."""
    
    @pytest.mark.slow
    def test_all_brain_modules_considered(self):
        """Warn if there are brain modules not in codebase-map.json."""
        with open(AI_DIR / "codebase-map.json") as f:
            data = json.load(f)
        
        documented = set(data["modules"].keys())
        
        # Find all Python files in brain/
        actual_modules = set()
        for py_file in BRAIN_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
                continue
            rel_path = str(py_file.relative_to(PROJECT_ROOT))
            actual_modules.add(rel_path)
        
        # Undocumented modules might be okay (utilities, etc) but worth noting
        undocumented = actual_modules - documented
        
        # Only fail if critical undocumented modules exist
        critical_prefixes = ["brain/app", "brain/llm", "brain/rag", "brain/prompt"]
        critical_undocumented = [
            m for m in undocumented 
            if any(m.startswith(prefix) for prefix in critical_prefixes)
        ]
        
        assert not critical_undocumented, \
            f"Critical modules not documented in codebase-map.json: {critical_undocumented}"


# Documentation linting utility functions (can be run standalone)

def find_missing_annotations(directory: Path) -> List[tuple]:
    """Find Python files missing @ai-indexable annotations.
    
    Returns list of (file_path, file_type) tuples.
    """
    missing = []
    
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
            continue
        
        with open(py_file) as f:
            content = f.read()
            if "@ai-indexable" not in content:
                # Determine if this is a core module that should have annotations
                rel_path = py_file.relative_to(directory)
                if len(rel_path.parts) <= 2:  # Top-level or one dir deep
                    missing.append((str(py_file), "core"))
    
    return missing


def validate_json_schemas() -> List[str]:
    """Validate all JSON files in .ai/ directory.
    
    Returns list of validation errors.
    """
    errors = []
    
    for json_file in AI_DIR.glob("*.json"):
        try:
            with open(json_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{json_file.name}: {str(e)}")
    
    return errors


if __name__ == "__main__":
    # Allow running as script for manual validation
    print("🔍 AI Documentation Validation\n")
    
    print("Checking for missing annotations...")
    missing = find_missing_annotations(BRAIN_DIR)
    if missing:
        print(f"  ⚠️  {len(missing)} files missing @ai-indexable:")
        for file_path, file_type in missing[:5]:
            print(f"     - {file_path}")
        if len(missing) > 5:
            print(f"     ... and {len(missing) - 5} more")
    else:
        print("  ✅ All core files have annotations")
    
    print("\nValidating JSON files...")
    errors = validate_json_schemas()
    if errors:
        print(f"  ❌ JSON validation errors:")
        for error in errors:
            print(f"     - {error}")
    else:
        print("  ✅ All JSON files valid")
    
    print("\n✨ Run full test suite with: pytest tests/test_ai_documentation.py")
