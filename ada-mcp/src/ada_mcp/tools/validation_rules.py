"""Fast validation rules - no LLM required.

Pattern-based validation using direct .ai/ file parsing.
Target: <20ms for most validations.
"""
# @ai-indexable: mcp-utility
# @ai-purpose: Lightning-fast validation rules (no LLM)

import json
from pathlib import Path
from typing import Any


# Repository structure conventions
BRAIN_MODULES = {
    "specialists": "brain/specialists/",
    "core": "brain/",
    "adapters": "adapters/",
    "mcp_tools": "ada-mcp/src/ada_mcp/tools/",
    "tests": "tests/",
    "docs": "docs/",
    "ai_docs": ".ai/",
}

# Files that need updates when adding modules
DOC_UPDATE_REQUIREMENTS = {
    "brain/specialists/*.py": [
        ".ai/codebase-map.json",
        ".ai/specialist-registry.json",
    ],
    "brain/*.py": [
        ".ai/codebase-map.json",
    ],
    "ada-mcp/src/ada_mcp/tools/*.py": [
        ".ai/codebase-map.json",
        "ada-mcp/src/ada_mcp/tools/__init__.py",
    ],
    "tests/*.py": [],  # Tests don't require doc updates
    "docs/*.rst": [
        "docs/index.rst",  # Update TOC
    ],
}


def check_conventions_fast(file_path: str, change_description: str) -> dict[str, Any]:
    """Fast convention checking via pattern matching.
    
    Target: <5ms
    """
    issues = []
    
    path = Path(file_path)
    
    # Check naming conventions
    if path.suffix == ".py":
        # Python files should use snake_case
        if not path.stem.replace("_", "").islower():
            issues.append(f"Python files should use snake_case: {path.name}")
        
        # Specialists should end in _specialist.py
        if "specialists" in path.parts and not path.stem.endswith("_specialist"):
            if path.stem not in ["__init__", "protocol", "bidirectional"]:
                issues.append(f"Specialist files should end with _specialist.py: {path.name}")
    
    # Check directory structure
    if path.parts[0] == "brain" and len(path.parts) > 2:
        valid_subdirs = ["specialists", "prompt_builder", "__pycache__"]
        if path.parts[1] not in valid_subdirs and not path.parts[1].endswith(".py"):
            issues.append(f"Unexpected brain subdirectory: {path.parts[1]}")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_placement_fast(file_path: str) -> dict[str, Any]:
    """Fast placement validation via path rules.
    
    Target: <2ms
    """
    issues = []
    
    path = Path(file_path)
    
    # Specialists must be in brain/specialists/
    if "_specialist.py" in file_path and "brain/specialists/" not in file_path:
        issues.append(f"Specialist files must be in brain/specialists/: {file_path}")
    
    # Tests must be in tests/
    if file_path.startswith("test_") and not file_path.startswith("tests/"):
        issues.append(f"Test files must be in tests/ directory: {file_path}")
    
    # Core brain modules must be in brain/ (not subdirs except specialists/prompt_builder)
    if file_path.startswith("brain/") and path.suffix == ".py":
        if len(path.parts) > 2:
            valid_subdirs = ["specialists", "prompt_builder"]
            if path.parts[1] not in valid_subdirs:
                issues.append(f"Core brain modules should be in brain/ root: {file_path}")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_docs_requirements_fast(file_path: str, change_description: str) -> dict[str, Any]:
    """Fast documentation requirement detection.
    
    Target: <3ms
    """
    files_to_update = []
    
    # Check if adding new module
    is_new_file = "new" in change_description.lower() or "add" in change_description.lower()
    
    if not is_new_file:
        # Existing file modifications usually don't need doc updates
        return {
            "passed": True,
            "files_to_update": []
        }
    
    # Match file pattern to required docs
    for pattern, required_docs in DOC_UPDATE_REQUIREMENTS.items():
        # Simple glob matching
        pattern_path = Path(pattern)
        file_path_obj = Path(file_path)
        
        # Check if pattern matches
        if pattern_path.parts[0] == file_path_obj.parts[0]:
            if "*" in pattern:
                # Wildcard match
                if pattern.endswith("*.py") and file_path.endswith(".py"):
                    files_to_update.extend(required_docs)
            else:
                # Exact match
                if file_path == pattern:
                    files_to_update.extend(required_docs)
    
    return {
        "passed": len(files_to_update) == 0,
        "files_to_update": list(set(files_to_update))  # Deduplicate
    }


def check_imports_fast(file_path: str, changed_code: str | None) -> dict[str, Any]:
    """Fast import validation via pattern detection.
    
    Target: <3ms
    """
    issues = []
    
    if not changed_code:
        return {"passed": True, "issues": []}
    
    # Check for known circular dependency patterns
    if "brain/prompt_builder" in file_path and "from brain.specialists" in changed_code:
        issues.append("Potential circular dependency: prompt_builder importing specialists")
    
    if "brain/specialists" in file_path and "from brain.llm" in changed_code:
        issues.append("Specialists should not directly import brain.llm")
    
    # Check for relative imports in ada-mcp
    if "ada-mcp" in file_path and changed_code:
        if "from .." in changed_code or "import .." in changed_code:
            # Relative imports are OK within ada-mcp
            pass
        elif "from brain" in changed_code:
            issues.append("ada-mcp should not directly import brain modules (use ada-client)")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_tests_requirements_fast(file_path: str, change_description: str) -> dict[str, Any]:
    """Fast test requirement detection.
    
    Target: <2ms
    """
    tests_needed = []
    
    # New modules need tests
    if "new" in change_description.lower() or "add" in change_description.lower():
        if file_path.endswith(".py") and not file_path.startswith("tests/"):
            # Suggest test file name
            path = Path(file_path)
            test_name = f"tests/test_{path.stem}.py"
            tests_needed.append(test_name)
    
    # Core functionality changes need tests
    if any(keyword in change_description.lower() for keyword in ["validate", "parse", "process", "analyze"]):
        if not file_path.startswith("tests/"):
            tests_needed.append(f"Integration test for {change_description}")
    
    return {
        "passed": len(tests_needed) == 0,
        "tests_needed": tests_needed
    }


def validate_fast(
    file_path: str,
    change_description: str,
    changed_code: str | None = None,
    check_types: list[str] | None = None
) -> dict[str, Any]:
    """Fast validation using pattern matching only.
    
    NO LLM calls. Pure pattern matching and rule-based validation.
    Target: <15ms total for all checks.
    
    Returns:
        Validation results dict with same structure as LLM validator
    """
    all_checks = check_types or ["conventions", "placement", "docs", "imports", "tests"]
    
    results = {
        "valid": True,
        "checks": {},
        "summary": ""
    }
    
    # Run requested checks
    if "conventions" in all_checks:
        results["checks"]["conventions"] = check_conventions_fast(file_path, change_description)
        if not results["checks"]["conventions"]["passed"]:
            results["valid"] = False
    
    if "placement" in all_checks:
        results["checks"]["placement"] = check_placement_fast(file_path)
        if not results["checks"]["placement"]["passed"]:
            results["valid"] = False
    
    if "docs" in all_checks:
        results["checks"]["docs"] = check_docs_requirements_fast(file_path, change_description)
        if not results["checks"]["docs"]["passed"]:
            results["valid"] = False
    
    if "imports" in all_checks:
        results["checks"]["imports"] = check_imports_fast(file_path, changed_code)
        if not results["checks"]["imports"]["passed"]:
            results["valid"] = False
    
    if "tests" in all_checks:
        results["checks"]["tests"] = check_tests_requirements_fast(file_path, change_description)
        if not results["checks"]["tests"]["passed"]:
            results["valid"] = False
    
    # Generate summary
    failed_checks = [name for name, result in results["checks"].items() if not result.get("passed", True)]
    if failed_checks:
        results["summary"] = f"Failed checks: {', '.join(failed_checks)}"
    else:
        results["summary"] = "All checks passed"
    
    return results


def should_use_llm(file_path: str, change_description: str) -> bool:
    """Determine if LLM validation is needed.
    
    Most changes can be validated with fast pattern matching.
    Only complex architectural questions need LLM.
    
    Returns:
        True if LLM validation recommended
    """
    # Complex keywords that might need LLM reasoning
    complex_keywords = [
        "refactor", "redesign", "architecture", "pattern",
        "optimize", "migrate", "restructure"
    ]
    
    desc_lower = change_description.lower()
    
    # Use LLM for complex changes
    if any(keyword in desc_lower for keyword in complex_keywords):
        return True
    
    # Use LLM for core architectural files
    core_files = [
        "brain/app.py",
        "brain/llm.py",
        "brain/prompt_builder",
        "brain/rag_store.py",
    ]
    
    if any(core in file_path for core in core_files):
        return True
    
    # Fast path for everything else
    return False
