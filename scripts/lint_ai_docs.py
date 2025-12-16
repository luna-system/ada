#!/usr/bin/env python3
"""
AI Documentation Linter

Validates that machine-readable documentation is consistent with code.
Can be run manually or integrated into CI/pre-commit hooks.

Usage:
    python scripts/lint_ai_docs.py              # Validate all
    python scripts/lint_ai_docs.py --fix        # Auto-fix where possible
    python scripts/lint_ai_docs.py --check-only # Exit with error code only
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import argparse


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
AI_DIR = PROJECT_ROOT / ".ai"
BRAIN_DIR = PROJECT_ROOT / "brain"
SPECIALISTS_DIR = BRAIN_DIR / "specialists"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def colored(text: str, color: str) -> str:
    """Return colored text for terminal."""
    return f"{color}{text}{Colors.RESET}"


class AIDocLinter:
    """Linter for AI documentation consistency."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def log(self, level: str, message: str):
        """Log a message at given level."""
        if level == "error":
            self.errors.append(message)
            if self.verbose:
                print(colored(f"  ❌ {message}", Colors.RED))
        elif level == "warning":
            self.warnings.append(message)
            if self.verbose:
                print(colored(f"  ⚠️  {message}", Colors.YELLOW))
        elif level == "info":
            self.info.append(message)
            if self.verbose:
                print(colored(f"  ℹ️  {message}", Colors.BLUE))
    
    def check_required_files(self) -> bool:
        """Verify all required documentation files exist."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Checking required files...{Colors.RESET}")
        
        required = [
            "README.md",
            "context.md",
            "codebase-map.json",
            "specialist-registry.json",
            "annotation-schema.json"
        ]
        
        all_exist = True
        for filename in required:
            path = AI_DIR / filename
            if not path.exists():
                self.log("error", f"Missing required file: .ai/{filename}")
                all_exist = False
            elif path.stat().st_size == 0:
                self.log("error", f"Empty file: .ai/{filename}")
                all_exist = False
        
        if all_exist and self.verbose:
            print(colored("  ✅ All required files present", Colors.GREEN))
        
        return all_exist
    
    def validate_json_files(self) -> bool:
        """Validate JSON syntax and structure."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Validating JSON files...{Colors.RESET}")
        
        all_valid = True
        
        for json_file in AI_DIR.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                # Check for version field
                if "version" not in data:
                    self.log("warning", f"{json_file.name} missing 'version' field")
                
            except json.JSONDecodeError as e:
                self.log("error", f"{json_file.name}: Invalid JSON - {e}")
                all_valid = False
        
        if all_valid and self.verbose:
            print(colored("  ✅ All JSON files valid", Colors.GREEN))
        
        return all_valid
    
    def check_codebase_map_consistency(self) -> bool:
        """Verify codebase-map.json matches actual files."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Checking codebase map consistency...{Colors.RESET}")
        
        try:
            with open(AI_DIR / "codebase-map.json") as f:
                codebase_map = json.load(f)
        except Exception as e:
            self.log("error", f"Cannot read codebase-map.json: {e}")
            return False
        
        all_consistent = True
        
        # Check documented modules exist
        for module_path in codebase_map["modules"].keys():
            file_path = PROJECT_ROOT / module_path
            if not file_path.exists():
                self.log("error", f"Documented module doesn't exist: {module_path}")
                all_consistent = False
        
        # Check critical modules are documented
        critical = ["brain/app.py", "brain/llm.py", "brain/rag_store.py", "brain/prompt_builder.py"]
        documented = set(codebase_map["modules"].keys())
        
        for module in critical:
            if module not in documented:
                self.log("error", f"Critical module not documented: {module}")
                all_consistent = False
        
        if all_consistent and self.verbose:
            print(colored("  ✅ Codebase map consistent", Colors.GREEN))
        
        return all_consistent
    
    def check_specialist_registry_consistency(self) -> bool:
        """Verify specialist-registry.json matches actual specialists."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Checking specialist registry...{Colors.RESET}")
        
        try:
            with open(AI_DIR / "specialist-registry.json") as f:
                registry = json.load(f)
        except Exception as e:
            self.log("error", f"Cannot read specialist-registry.json: {e}")
            return False
        
        all_consistent = True
        
        # Find actual specialist files
        actual_specialists = set()
        if SPECIALISTS_DIR.exists():
            for file_path in SPECIALISTS_DIR.glob("*_specialist.py"):
                specialist_name = file_path.stem.replace("_specialist", "")
                actual_specialists.add(specialist_name)
        
        registered = set(registry["specialists"].keys())
        
        # Check for undocumented specialists
        undocumented = actual_specialists - registered
        if undocumented:
            for name in undocumented:
                self.log("error", f"Specialist exists but not in registry: {name}")
            all_consistent = False
        
        # Check for registry entries without files
        missing = registered - actual_specialists
        if missing:
            for name in missing:
                self.log("warning", f"Registry has entry without file: {name}")
        
        # Verify file paths in registry
        for name, data in registry["specialists"].items():
            file_path = PROJECT_ROOT / data["file"]
            if not file_path.exists():
                self.log("error", f"Registry references missing file: {data['file']}")
                all_consistent = False
        
        if all_consistent and self.verbose:
            print(colored("  ✅ Specialist registry consistent", Colors.GREEN))
        
        return all_consistent
    
    def check_source_annotations(self) -> Tuple[bool, List[str]]:
        """Check for @ai-indexable annotations in core modules."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Checking source code annotations...{Colors.RESET}")
        
        core_modules = [
            "brain/app.py",
            "brain/llm.py",
            "brain/prompt_builder.py",
            "brain/rag_store.py",
        ]
        
        missing_annotations = []
        all_annotated = True
        
        for module_path in core_modules:
            file_path = PROJECT_ROOT / module_path
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read()
                    if "@ai-indexable" not in content:
                        self.log("error", f"Missing @ai-indexable: {module_path}")
                        missing_annotations.append(module_path)
                        all_annotated = False
        
        # Check specialists
        if SPECIALISTS_DIR.exists():
            for specialist_file in SPECIALISTS_DIR.glob("*_specialist.py"):
                with open(specialist_file) as f:
                    content = f.read()
                    if "@ai-indexable" not in content:
                        rel_path = str(specialist_file.relative_to(PROJECT_ROOT))
                        self.log("warning", f"Specialist missing annotation: {rel_path}")
                        missing_annotations.append(rel_path)
        
        if all_annotated and self.verbose:
            print(colored("  ✅ Core modules annotated", Colors.GREEN))
        
        return all_annotated, missing_annotations
    
    def find_unannotated_modules(self) -> List[str]:
        """Find Python modules that might need annotations."""
        if self.verbose:
            print(f"\n{Colors.BOLD}Scanning for unannotated modules...{Colors.RESET}")
        
        candidates = []
        
        for py_file in BRAIN_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
                continue
            
            # Check if it's a substantial file (more than imports)
            if py_file.stat().st_size < 500:  # Skip tiny files
                continue
            
            with open(py_file) as f:
                content = f.read()
                if "@ai-indexable" not in content:
                    rel_path = str(py_file.relative_to(PROJECT_ROOT))
                    candidates.append(rel_path)
        
        if candidates and self.verbose:
            print(colored(f"  ℹ️  Found {len(candidates)} unannotated modules (may be okay):", Colors.BLUE))
            for path in candidates[:5]:
                print(f"     - {path}")
            if len(candidates) > 5:
                print(f"     ... and {len(candidates) - 5} more")
        
        return candidates
    
    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        if self.verbose:
            print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}AI Documentation Validation{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        checks = [
            self.check_required_files(),
            self.validate_json_files(),
            self.check_codebase_map_consistency(),
            self.check_specialist_registry_consistency(),
            self.check_source_annotations()[0],
        ]
        
        # Informational only
        self.find_unannotated_modules()
        
        # Summary
        if self.verbose:
            print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}Summary:{Colors.RESET}")
            print(colored(f"  Errors: {len(self.errors)}", Colors.RED if self.errors else Colors.GREEN))
            print(colored(f"  Warnings: {len(self.warnings)}", Colors.YELLOW if self.warnings else Colors.GREEN))
            print(colored(f"  Info: {len(self.info)}", Colors.BLUE))
            print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        return all(checks) and len(self.errors) == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate AI documentation consistency")
    parser.add_argument("--check-only", action="store_true", help="Exit with error code, no output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    linter = AIDocLinter(verbose=not args.check_only and not args.quiet)
    success = linter.run_all_checks()
    
    if args.check_only:
        sys.exit(0 if success else 1)
    
    if success:
        print(colored("✨ All checks passed!", Colors.GREEN))
        sys.exit(0)
    else:
        print(colored("❌ Validation failed. Please fix errors above.", Colors.RED))
        sys.exit(1)


if __name__ == "__main__":
    main()
