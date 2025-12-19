#!/usr/bin/env python3
"""
Question generation for external codebase validation.

Questions designed to test different aspects of codebase comprehension:
- Architecture: Overall structure and design
- Module: What specific files/modules do
- Dataflow: How data moves through the system
- Debugging: Where to look for issues
- Feature: How to implement new functionality

December 19, 2025
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ComprehensionQuestion:
    """A question about a codebase."""
    question: str
    category: str  # architecture, module, dataflow, debugging, feature
    difficulty: str  # easy, medium, hard
    expected_keywords: list[str]  # Keywords that should appear in good answers
    ground_truth: Optional[str] = None  # If we know the exact answer


# ============================================================================
# Generic questions that work for ANY codebase
# ============================================================================

def generate_architecture_questions() -> list[ComprehensionQuestion]:
    """
    Generate generic architecture questions.
    
    These should work for any codebase.
    """
    return [
        ComprehensionQuestion(
            question="What is the main entry point of this application?",
            category="architecture",
            difficulty="easy",
            expected_keywords=["main", "entry", "app", "start", "__main__", "index"],
        ),
        ComprehensionQuestion(
            question="What is the overall architecture pattern used in this codebase?",
            category="architecture", 
            difficulty="medium",
            expected_keywords=["pattern", "structure", "layer", "module", "component"],
        ),
        ComprehensionQuestion(
            question="What are the main dependencies or external libraries used?",
            category="architecture",
            difficulty="easy",
            expected_keywords=["dependency", "library", "import", "package", "require"],
        ),
        ComprehensionQuestion(
            question="How is the codebase organized into directories/modules?",
            category="architecture",
            difficulty="medium",
            expected_keywords=["directory", "folder", "module", "organize", "structure"],
        ),
        ComprehensionQuestion(
            question="What configuration files exist and what do they control?",
            category="architecture",
            difficulty="medium",
            expected_keywords=["config", "setting", "environment", "yaml", "json", "toml"],
        ),
    ]


def generate_module_questions(modules: list[str]) -> list[ComprehensionQuestion]:
    """
    Generate questions about specific modules.
    
    Args:
        modules: List of module names/paths found in the codebase
    """
    questions = []
    
    for module in modules:
        # Clean up module name for display
        module_name = module.replace("/", ".").replace(".py", "")
        
        questions.append(ComprehensionQuestion(
            question=f"What is the purpose of the '{module}' module?",
            category="module",
            difficulty="medium",
            expected_keywords=["purpose", "function", "responsible", module_name.split(".")[-1]],
        ))
        
        questions.append(ComprehensionQuestion(
            question=f"What are the main functions or classes in '{module}'?",
            category="module",
            difficulty="medium",
            expected_keywords=["function", "class", "def", "method"],
        ))
    
    return questions


def generate_dataflow_questions() -> list[ComprehensionQuestion]:
    """
    Generate questions about data flow.
    """
    return [
        ComprehensionQuestion(
            question="How does data flow through the main request/response cycle?",
            category="dataflow",
            difficulty="hard",
            expected_keywords=["request", "response", "flow", "handler", "process"],
        ),
        ComprehensionQuestion(
            question="What is the data storage mechanism used?",
            category="dataflow",
            difficulty="medium",
            expected_keywords=["storage", "database", "file", "persist", "save", "store"],
        ),
        ComprehensionQuestion(
            question="How is state managed across the application?",
            category="dataflow",
            difficulty="hard",
            expected_keywords=["state", "manage", "global", "session", "context"],
        ),
    ]


def generate_debugging_questions() -> list[ComprehensionQuestion]:
    """
    Generate questions about debugging/troubleshooting.
    """
    return [
        ComprehensionQuestion(
            question="Where would you look to debug issues with the main functionality?",
            category="debugging",
            difficulty="medium",
            expected_keywords=["log", "debug", "error", "trace", "exception"],
        ),
        ComprehensionQuestion(
            question="How are errors handled in this codebase?",
            category="debugging",
            difficulty="medium",
            expected_keywords=["error", "exception", "handle", "catch", "try"],
        ),
        ComprehensionQuestion(
            question="What testing infrastructure exists?",
            category="debugging",
            difficulty="easy",
            expected_keywords=["test", "pytest", "unittest", "spec", "coverage"],
        ),
    ]


def generate_feature_questions() -> list[ComprehensionQuestion]:
    """
    Generate questions about implementing new features.
    """
    return [
        ComprehensionQuestion(
            question="If I wanted to add a new API endpoint, where would I do that?",
            category="feature",
            difficulty="medium",
            expected_keywords=["endpoint", "route", "api", "handler", "controller"],
        ),
        ComprehensionQuestion(
            question="How would I extend the core functionality with a new module?",
            category="feature",
            difficulty="hard",
            expected_keywords=["extend", "add", "module", "import", "plugin"],
        ),
        ComprehensionQuestion(
            question="What patterns should I follow when adding new code?",
            category="feature",
            difficulty="hard",
            expected_keywords=["pattern", "convention", "style", "follow", "consistent"],
        ),
    ]


def generate_all_questions(modules: list[str] = None) -> list[ComprehensionQuestion]:
    """
    Generate a complete set of questions for a codebase.
    
    Args:
        modules: Optional list of discovered modules
        
    Returns:
        List of all comprehension questions
    """
    questions = []
    
    questions.extend(generate_architecture_questions())
    questions.extend(generate_dataflow_questions())
    questions.extend(generate_debugging_questions())
    questions.extend(generate_feature_questions())
    
    if modules:
        # Limit to first 5 modules to avoid explosion
        questions.extend(generate_module_questions(modules[:5]))
    
    return questions


def get_question_by_difficulty(
    questions: list[ComprehensionQuestion],
    difficulty: str
) -> list[ComprehensionQuestion]:
    """Filter questions by difficulty level."""
    return [q for q in questions if q.difficulty == difficulty]


def get_question_by_category(
    questions: list[ComprehensionQuestion],
    category: str
) -> list[ComprehensionQuestion]:
    """Filter questions by category."""
    return [q for q in questions if q.category == category]
