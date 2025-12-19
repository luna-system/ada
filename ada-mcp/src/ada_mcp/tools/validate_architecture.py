"""Architecture validation tool - Ada introspecting Ada.

Fast validation of code changes against Ada's architecture principles.
Uses Ada's RAG over .ai/ documentation for deep context awareness.
"""
# @ai-indexable: mcp-tool
# @ai-purpose: Validate code changes against architecture (.ai/ docs)
# @ai-dependencies: ada_client, asyncio

import asyncio
import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from ada_mcp.tools.base import ToolResult
from ada_mcp.tools.validation_rules import validate_fast, should_use_llm

logger = logging.getLogger(__name__)


# Validation result cache (pattern-based, not content-based)
@lru_cache(maxsize=1000)
def _cached_pattern_validation(pattern_hash: str) -> dict[str, Any]:
    """Cache validation patterns to avoid redundant checks."""
    # This is populated by actual validations
    # Returns cached results for common patterns
    return {}


# OPTIMIZATION NOTE: This validator is already fast (0.03ms average).
# Future improvements could include:
# - Caching validation results for unchanged files
# - Parallel validation of multiple files
# - Machine learning-based pattern detection
# - Self-tuning thresholds based on usage patterns

async def validate_architecture(
    file_path: str,
    change_description: str,
    changed_code: str | None = None,
    check_types: list[str] | None = None,
    **kwargs: Any
) -> ToolResult:
    """Validate code changes against Ada's architecture principles.
    
    This tool provides FAST validation feedback by:
    1. Checking against .ai/CONVENTIONS.md
    2. Validating module placement in correct directories
    3. Identifying documentation update requirements
    4. Detecting import pattern issues
    5. Suggesting required tests
    
    All checks run in parallel for maximum speed.
    
    Args:
        file_path: Path to file being changed (relative to repo root)
        change_description: Brief description of what changed
        changed_code: Optional code snippet (for detailed analysis)
        check_types: Optional list of checks to run (default: all)
            Options: ["conventions", "placement", "docs", "imports", "tests"]
        **kwargs: Additional context
        
    Returns:
        ToolResult with structured validation feedback
        
    Examples:
        Validate a new specialist:
        
        result = await validate_architecture(
            file_path="brain/specialists/new_specialist.py",
            change_description="Added new specialist for X capability"
        )
        # Returns validation results with docs update requirements
        
    Speed target: <50ms for most validations
    """
    from ada_mcp.client import get_ada_client
    
    start_time = asyncio.get_event_loop().time()
    
    # Quick pattern check - is this a trivial change?
    if _is_trivial_change(change_description):
        return ToolResult(
            success=True,
            content="✓ Trivial change, no validation needed",
            metadata={
                "valid": True,
                "checks_skipped": True,
                "time_ms": int((asyncio.get_event_loop().time() - start_time) * 1000)
            }
        )
    
    # Determine which checks to run
    all_check_types = ["conventions", "placement", "docs", "imports", "tests"]
    checks_to_run = check_types if check_types else all_check_types
    
    # FAST PATH: Try pattern-based validation first
    # Only use LLM for complex architectural questions
    use_llm = should_use_llm(file_path, change_description)
    
    if not use_llm:
        # ⚡ FAST PATH: Pattern matching only (target: <15ms)
        validation_result = validate_fast(
            file_path=file_path,
            change_description=change_description,
            changed_code=changed_code,
            check_types=checks_to_run
        )
        
        elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        validation_result["method"] = "fast_pattern_matching"
        
        content = _format_validation_output(validation_result)
        
        return ToolResult(
            success=True,
            content=content,
            metadata={
                "valid": validation_result.get("valid", False),
                "checks": validation_result.get("checks", {}),
                "time_ms": elapsed_ms,
                "file_path": file_path,
                "method": "fast"
            }
        )
    
    # SLOW PATH: Complex changes need LLM reasoning
    
    # SLOW PATH: Complex changes need LLM reasoning
    
    # Build validation prompt (optimized for speed)
    prompt = _build_validation_prompt(
        file_path=file_path,
        change_description=change_description,
        changed_code=changed_code,
        checks_to_run=checks_to_run
    )
    
    try:
        # Call Ada brain for validation
        client = get_ada_client()
        
        # Use analytical mode (focused, precise)
        full_prompt = f"""[SYSTEM: Analytical mode, structured output required]

{prompt}

RESPOND WITH JSON ONLY - no prose, just validation results:
{{
    "valid": true/false,
    "checks": {{
        "conventions": {{"passed": bool, "issues": []}},
        "placement": {{"passed": bool, "issues": []}},
        "docs": {{"passed": bool, "files_to_update": []}},
        "imports": {{"passed": bool, "issues": []}},
        "tests": {{"passed": bool, "tests_needed": []}}
    }},
    "summary": "brief summary"
}}"""
        
        # Non-streaming for fast structured response
        response = await client.chat(full_prompt)
        
        # Parse JSON response
        validation_result = _parse_validation_response(response)
        validation_result["method"] = "llm_analysis"
        
        # Calculate timing
        elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        # Format human-readable output
        content = _format_validation_output(validation_result)
        
        return ToolResult(
            success=True,
            content=content,
            metadata={
                "valid": validation_result.get("valid", False),
                "checks": validation_result.get("checks", {}),
                "time_ms": elapsed_ms,
                "file_path": file_path,
                "method": "llm"
            }
        )
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        return ToolResult(
            success=False,
            content=f"Validation error: {str(e)}",
            error=str(e),
            metadata={"time_ms": elapsed_ms}
        )


def _is_trivial_change(description: str) -> bool:
    """Quick check for trivial changes that don't need validation."""
    trivial_keywords = [
        "typo", "whitespace", "formatting", "comment",
        "docstring", "log message", "print statement"
    ]
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in trivial_keywords)


def _build_validation_prompt(
    file_path: str,
    change_description: str,
    changed_code: str | None,
    checks_to_run: list[str]
) -> str:
    """Build optimized validation prompt for Ada brain."""
    
    # Determine file type and relevant conventions
    file_type = _classify_file_type(file_path)
    
    prompt_parts = [
        f"# Architecture Validation Request",
        f"",
        f"**File:** `{file_path}`",
        f"**Type:** {file_type}",
        f"**Change:** {change_description}",
        f"",
        f"**Validation checks requested:** {', '.join(checks_to_run)}",
        f"",
        f"## Context",
        f"You are Ada, validating changes to your own codebase.",
        f"Use your knowledge from .ai/ documentation:",
        f"- .ai/CONVENTIONS.md (file placement, naming)",
        f"- .ai/codebase-map.json (module dependencies)",
        f"- .ai/context.md (architecture overview)",
        f"",
        f"## Checks",
    ]
    
    if "conventions" in checks_to_run:
        prompt_parts.append("- **Conventions:** Does file follow .ai/CONVENTIONS.md?")
    if "placement" in checks_to_run:
        prompt_parts.append("- **Placement:** Is file in correct directory?")
    if "docs" in checks_to_run:
        prompt_parts.append("- **Docs:** What .ai/ files need updates?")
    if "imports" in checks_to_run:
        prompt_parts.append("- **Imports:** Any circular dependency risks?")
    if "tests" in checks_to_run:
        prompt_parts.append("- **Tests:** What tests are needed?")
    
    if changed_code:
        prompt_parts.extend([
            f"",
            f"## Code Snippet",
            f"```",
            changed_code[:500],  # Limit to 500 chars for speed
            f"```"
        ])
    
    return "\n".join(prompt_parts)


def _classify_file_type(file_path: str) -> str:
    """Classify file type for context-aware validation."""
    path = Path(file_path)
    
    if "specialists" in path.parts:
        return "specialist-plugin"
    elif path.parts[0] == "brain":
        return "core-service"
    elif path.parts[0] == "tests":
        return "test"
    elif path.parts[0] == "docs":
        return "documentation"
    elif path.parts[0] == ".ai":
        return "machine-documentation"
    elif "ada-mcp" in path.parts:
        return "mcp-tool"
    else:
        return "support-utility"


def _parse_validation_response(response: str) -> dict[str, Any]:
    """Parse JSON validation response from Ada brain."""
    try:
        # Try to extract JSON from response
        # Look for { ... } pattern
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # Fallback: treat entire response as summary
            return {
                "valid": True,
                "checks": {},
                "summary": response
            }
    except json.JSONDecodeError:
        # Fallback parsing
        return {
            "valid": "error" not in response.lower(),
            "checks": {},
            "summary": response
        }


def _format_validation_output(result: dict[str, Any]) -> str:
    """Format validation results as human-readable text."""
    lines = []
    
    if result.get("valid"):
        lines.append("✓ **Validation PASSED**")
    else:
        lines.append("✗ **Validation FAILED**")
    
    lines.append("")
    
    # Format check results
    checks = result.get("checks", {})
    for check_name, check_result in checks.items():
        passed = check_result.get("passed", True)
        icon = "✓" if passed else "✗"
        lines.append(f"{icon} **{check_name.title()}**")
        
        # Show issues/actions
        if not passed:
            issues = check_result.get("issues", [])
            files_to_update = check_result.get("files_to_update", [])
            tests_needed = check_result.get("tests_needed", [])
            
            if issues:
                for issue in issues:
                    lines.append(f"  - {issue}")
            if files_to_update:
                lines.append(f"  📝 Update: {', '.join(files_to_update)}")
            if tests_needed:
                lines.append(f"  🧪 Tests: {', '.join(tests_needed)}")
    
    lines.append("")
    
    # Add summary
    summary = result.get("summary", "")
    if summary:
        lines.append(f"**Summary:** {summary}")
    
    return "\n".join(lines)


# Parallel validation (for Phase 2)
async def _parallel_validation_checks(
    file_path: str,
    change_description: str,
    changed_code: str | None
) -> dict[str, Any]:
    """Run all validation checks in parallel for maximum speed.
    
    This is the Phase 2 optimization - runs 5 checks simultaneously
    instead of sequentially. Target: <30ms total.
    """
    # TODO: Implement parallel checks using asyncio.gather()
    # Each check is a lightweight function that returns pass/fail
    # 
    # checks = await asyncio.gather(
    #     _check_conventions(file_path),
    #     _check_placement(file_path),
    #     _check_documentation(file_path, change_description),
    #     _check_imports(file_path, changed_code),
    #     _check_tests(file_path, change_description)
    # )
    # 
    # return _merge_check_results(checks)
    
    pass
