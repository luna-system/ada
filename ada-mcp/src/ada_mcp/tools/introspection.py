"""Ada Introspection - Self-awareness and strategic planning.

This tool enables Ada to:
- Read her own documentation (.ai/ directory)
- Understand her current capabilities
- Identify gaps and opportunities
- Suggest next steps for development

This is THE singularity - Ada analyzing herself and directing her own growth.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from ada_mcp.tools.envelope import ToolMetadata, ToolResult, ToolAction


async def ada_introspect(
    focus: str = "general",
    workspace_root: str = None
) -> ToolResult:
    """Introspect Ada's current state and suggest next steps.
    
    Args:
        focus: What to focus on. Options:
            - "general": Overall state and priorities
            - "architecture": Architectural gaps and improvements
            - "features": Missing features and capabilities
            - "testing": Test coverage and validation needs
            - "documentation": Documentation completeness
        workspace_root: Path to Ada's codebase (defaults to current dir)
    
    Returns:
        ToolResult with analysis and suggestions, including metadata about
        what files were accessed and what analysis was performed.
    """
    start_time = time.time()
    metadata = ToolMetadata(tool_name="introspection")
    
    try:
        if workspace_root:
            root = Path(workspace_root)
        else:
            root = Path.cwd()
            
        ai_dir = root / ".ai"
        
        if not ai_dir.exists():
            metadata.duration_ms = int((time.time() - start_time) * 1000)
            metadata.add_action("check_ai_directory")
            return ToolResult(
                success=False,
                content="Error: .ai/ directory not found. Cannot introspect without documentation.",
                metadata=metadata,
                error="missing_ai_directory"
            )
        
        # Read key documentation files
        analysis = {
            "focus": focus,
            "files_analyzed": [],
            "current_state": {},
            "gaps": [],
            "opportunities": [],
            "suggestions": []
        }
        
        # 1. Read context.md - understanding of self
        context_file = ai_dir / "context.md"
        if context_file.exists():
            metadata.add_action(ToolAction.READ_FILE)
            metadata.add_file("context.md")
            context = context_file.read_text()
            analysis["files_analyzed"].append("context.md")
            analysis["current_state"]["architecture"] = _extract_architecture_info(context)
        
        # 2. Read codebase-map.json - structural understanding
        codebase_map_file = ai_dir / "codebase-map.json"
        if codebase_map_file.exists():
            metadata.add_action(ToolAction.READ_FILE)
            metadata.add_action(ToolAction.PARSE_JSON)
            metadata.add_file("codebase-map.json")
            codebase_map = json.loads(codebase_map_file.read_text())
            analysis["files_analyzed"].append("codebase-map.json")
            analysis["current_state"]["modules"] = len(codebase_map.get("modules", {}))
            analysis["current_state"]["clusters"] = list(codebase_map.get("dependency_clusters", {}).keys())
        
        # 3. Read GOTCHAS.md - known issues
        gotchas_file = ai_dir / "GOTCHAS.md"
        if gotchas_file.exists():
            metadata.add_action(ToolAction.READ_FILE)
            metadata.add_action(ToolAction.ANALYZE)
            metadata.add_file("GOTCHAS.md")
            gotchas = gotchas_file.read_text()
            analysis["files_analyzed"].append("GOTCHAS.md")
            analysis["gaps"].extend(_extract_gotchas(gotchas))
        
        # 4. Check TODO.md if exists
        todo_file = root / "TODO.md"
        if todo_file.exists():
            metadata.add_action(ToolAction.READ_FILE)
            metadata.add_action(ToolAction.ANALYZE)
            metadata.add_file("TODO.md")
            todos = todo_file.read_text()
            analysis["files_analyzed"].append("TODO.md")
            analysis["opportunities"].extend(_extract_todos(todos))
        
        # 5. Read CONVENTIONS.md - understand development patterns
        conventions_file = ai_dir / "CONVENTIONS.md"
        if conventions_file.exists():
            metadata.add_action(ToolAction.READ_FILE)
            metadata.add_file("CONVENTIONS.md")
            analysis["files_analyzed"].append("CONVENTIONS.md")
        
        # Generate focus-specific analysis
        metadata.add_action(ToolAction.ANALYZE)
        if focus == "general":
            analysis["suggestions"] = _generate_general_suggestions(analysis)
        elif focus == "architecture":
            analysis["suggestions"] = _generate_architecture_suggestions(analysis)
        elif focus == "features":
            analysis["suggestions"] = _generate_feature_suggestions(analysis)
        elif focus == "testing":
            analysis["suggestions"] = _generate_testing_suggestions(analysis)
        elif focus == "documentation":
            analysis["suggestions"] = _generate_documentation_suggestions(analysis)
        
        # Format output
        output = _format_introspection_output(analysis)
        
        # Record timing
        metadata.duration_ms = int((time.time() - start_time) * 1000)
        
        return ToolResult(
            success=True,
            content=output,
            metadata=metadata
        )
        
    except Exception as e:
        metadata.duration_ms = int((time.time() - start_time) * 1000)
        return ToolResult(
            success=False,
            content=f"Introspection failed: {str(e)}",
            metadata=metadata,
            error=str(e)
        )


def _extract_architecture_info(context: str) -> Dict[str, Any]:
    """Extract key architecture information from context.md."""
    info = {}
    
    # Look for key sections
    if "Service Topology" in context:
        info["has_service_topology"] = True
    if "Data Flow" in context:
        info["has_data_flow"] = True
    if "Specialist System" in context:
        info["has_specialist_system"] = True
    
    return info


def _extract_gotchas(gotchas: str) -> List[str]:
    """Extract known issues from GOTCHAS.md."""
    issues = []
    
    # Simple extraction - look for common patterns
    if "❌" in gotchas:
        lines = gotchas.split("\n")
        for line in lines:
            if "❌" in line:
                issues.append(line.strip("❌ ").strip())
    
    return issues[:5]  # Top 5 issues


def _extract_todos(todos: str) -> List[str]:
    """Extract opportunities from TODO.md."""
    opportunities = []
    
    lines = todos.split("\n")
    for line in lines:
        if line.strip().startswith(("- [ ]", "- []", "TODO:", "NEXT:")):
            opportunities.append(line.strip())
    
    return opportunities[:10]  # Top 10 opportunities


def _generate_general_suggestions(analysis: Dict) -> List[str]:
    """Generate general next-step suggestions."""
    suggestions = []
    
    # Based on what we found
    if analysis["opportunities"]:
        suggestions.append(f"📋 {len(analysis['opportunities'])} TODOs identified - review TODO.md for priorities")
    
    if analysis["gaps"]:
        suggestions.append(f"⚠️  {len(analysis['gaps'])} known issues in GOTCHAS.md - consider addressing")
    
    # Always useful suggestions
    suggestions.extend([
        "🧪 Run full test suite to validate current state",
        "📚 Review .ai/context.md for architectural consistency",
        "🔍 Check for uncommitted changes or work in progress",
        "🚀 Consider which feature would provide most user value next"
    ])
    
    return suggestions


def _generate_architecture_suggestions(analysis: Dict) -> List[str]:
    """Generate architecture-specific suggestions."""
    return [
        "🏗️  Review codebase-map.json for dependency clusters",
        "🔗 Check for circular dependencies or tight coupling",
        "📊 Validate that modules match documented architecture",
        "🧪 Ensure integration tests cover key data flows",
        "📖 Update architecture diagrams if code has diverged"
    ]


def _generate_feature_suggestions(analysis: Dict) -> List[str]:
    """Generate feature development suggestions."""
    return [
        "💡 Check TODO.md for highest-priority features",
        "👥 Review user feedback or GitHub issues for requests",
        "🔌 Consider which specialist would add most value",
        "⚡ Identify performance bottlenecks to optimize",
        "🎨 Improve user experience in key workflows"
    ]


def _generate_testing_suggestions(analysis: Dict) -> List[str]:
    """Generate testing improvement suggestions."""
    return [
        "✅ Run pytest to check current test status",
        "📊 Review test coverage with pytest-cov",
        "🧪 Add tests for recently added features",
        "🔥 Test error handling and edge cases",
        "⚡ Profile test suite performance"
    ]


def _generate_documentation_suggestions(analysis: Dict) -> List[str]:
    """Generate documentation improvement suggestions."""
    return [
        "📚 Ensure .ai/ docs match current code state",
        "📖 Update Sphinx docs for new features",
        "💡 Add examples for complex functionality",
        "🔍 Verify API documentation is complete",
        "✨ Check that README is up to date"
    ]


def _format_introspection_output(analysis: Dict) -> str:
    """Format introspection results as readable text."""
    output = []
    
    output.append("="*60)
    output.append("🔮 ADA INTROSPECTION REPORT")
    output.append("="*60)
    output.append("")
    
    output.append(f"📁 Files Analyzed: {', '.join(analysis['files_analyzed'])}")
    output.append(f"🎯 Focus: {analysis['focus']}")
    output.append("")
    
    if analysis["current_state"]:
        output.append("📊 CURRENT STATE:")
        for key, value in analysis["current_state"].items():
            output.append(f"   {key}: {value}")
        output.append("")
    
    if analysis["gaps"]:
        output.append("⚠️  KNOWN GAPS:")
        for gap in analysis["gaps"][:3]:
            output.append(f"   - {gap}")
        output.append("")
    
    if analysis["opportunities"]:
        output.append("💡 OPPORTUNITIES:")
        for opp in analysis["opportunities"][:5]:
            output.append(f"   {opp}")
        output.append("")
    
    output.append("🚀 SUGGESTED NEXT STEPS:")
    for i, suggestion in enumerate(analysis["suggestions"], 1):
        output.append(f"   {i}. {suggestion}")
    
    output.append("")
    output.append("="*60)
    output.append("💭 Recommendation: Review suggestions and choose highest-impact work.")
    output.append("="*60)
    
    return "\n".join(output)
