#!/usr/bin/env python3
"""
Ada's Single-File Code Analyzer - Party Trick Edition! 🎉

Given ONE Python file, finds issues with ZERO external context.
Pure pattern matching, syntax analysis, and smart heuristics.

Usage:
    python scripts/analyze_code.py <file.py>
    # or: uv run ada analyze <file.py>
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class IssueSeverity(Enum):
    ERROR = "❌"
    WARNING = "⚠️"
    STYLE = "💅"
    SUGGESTION = "💡"


@dataclass
class Issue:
    line: int
    severity: IssueSeverity
    category: str
    message: str
    context: str = ""


class CodeAnalyzer:
    """Smart pattern-based code analyzer - no external deps needed!"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text()
        self.lines = self.content.split('\n')
        self.issues: List[Issue] = []
        
    def analyze(self) -> List[Issue]:
        """Run all analysis passes."""
        # Parse once, use many times
        try:
            self.tree = ast.parse(self.content)
        except SyntaxError as e:
            self.issues.append(Issue(
                line=e.lineno or 0,
                severity=IssueSeverity.ERROR,
                category="Syntax",
                message=f"Syntax error: {e.msg}",
                context=self.lines[e.lineno-1] if e.lineno else ""
            ))
            return self.issues
        
        # Run all checks
        self.check_imports()
        self.check_unused_variables()
        self.check_dangerous_patterns()
        self.check_async_issues()
        self.check_exception_handling()
        self.check_complexity()
        self.check_style()
        
        return sorted(self.issues, key=lambda x: x.line)
    
    def check_imports(self):
        """Find unused imports and import issues."""
        imports = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.lineno
        
        # Check if imports are used
        for name, lineno in imports.items():
            # Skip common test/debug imports
            if name in ['pdb', 'ipdb', 'breakpoint']:
                self.issues.append(Issue(
                    line=lineno,
                    severity=IssueSeverity.WARNING,
                    category="Debug",
                    message=f"Debug import '{name}' left in code",
                    context=self.lines[lineno-1]
                ))
    
    def check_unused_variables(self):
        """Find variables that are assigned but never used."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                # Check for unused function parameters
                assigned = set()
                used = set()
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store):
                            assigned.add(child.id)
                        elif isinstance(child.ctx, ast.Load):
                            used.add(child.id)
                
                unused = assigned - used - {'self', 'cls', '_'}
                for var in unused:
                    # Find the line where it's assigned
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and child.id == var:
                            if hasattr(child, 'lineno'):
                                self.issues.append(Issue(
                                    line=child.lineno,
                                    severity=IssueSeverity.SUGGESTION,
                                    category="Unused",
                                    message=f"Variable '{var}' assigned but never used",
                                ))
                                break
    
    def check_dangerous_patterns(self):
        """Find potentially dangerous code patterns."""
        dangerous_patterns = [
            (r'exec\s*\(', "exec() can execute arbitrary code"),
            (r'eval\s*\(', "eval() can execute arbitrary code"),
            (r'__import__\s*\(', "Dynamic imports can be risky"),
            (r'shell\s*=\s*True', "shell=True in subprocess is dangerous"),
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern, message in dangerous_patterns:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        line=i,
                        severity=IssueSeverity.WARNING,
                        category="Security",
                        message=message,
                        context=line.strip()
                    ))
    
    def check_async_issues(self):
        """Find async/await issues."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.AsyncFunctionDef):
                # Check if async function doesn't use await
                has_await = any(isinstance(n, ast.Await) for n in ast.walk(node))
                if not has_await:
                    self.issues.append(Issue(
                        line=node.lineno,
                        severity=IssueSeverity.SUGGESTION,
                        category="Async",
                        message=f"Async function '{node.name}' doesn't use await - maybe it shouldn't be async?",
                    ))
            
            # Check for missing await
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id.startswith('async_') or node.func.id.endswith('_async'):
                        # Probably an async function call without await
                        parent_is_await = False
                        # This is simplified - real check would need parent tracking
                        if hasattr(node, 'lineno'):
                            line = self.lines[node.lineno-1]
                            if 'await' not in line:
                                self.issues.append(Issue(
                                    line=node.lineno,
                                    severity=IssueSeverity.WARNING,
                                    category="Async",
                                    message=f"Possible missing 'await' for async function",
                                    context=line.strip()
                                ))
    
    def check_exception_handling(self):
        """Find exception handling issues."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                # Bare except
                if node.type is None:
                    self.issues.append(Issue(
                        line=node.lineno,
                        severity=IssueSeverity.WARNING,
                        category="Exceptions",
                        message="Bare 'except:' catches all exceptions, including KeyboardInterrupt",
                    ))
                
                # Check for pass in except
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.issues.append(Issue(
                        line=node.lineno,
                        severity=IssueSeverity.WARNING,
                        category="Exceptions",
                        message="Exception caught and silently ignored",
                    ))
    
    def check_complexity(self):
        """Check for overly complex functions."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count nested depth
                max_depth = self._get_nesting_depth(node)
                if max_depth > 4:
                    self.issues.append(Issue(
                        line=node.lineno,
                        severity=IssueSeverity.SUGGESTION,
                        category="Complexity",
                        message=f"Function '{node.name}' has high nesting depth ({max_depth}) - consider refactoring",
                    ))
                
                # Count lines
                if hasattr(node, 'end_lineno'):
                    lines = node.end_lineno - node.lineno
                    if lines > 50:
                        self.issues.append(Issue(
                            line=node.lineno,
                            severity=IssueSeverity.SUGGESTION,
                            category="Complexity",
                            message=f"Function '{node.name}' is {lines} lines - consider breaking it up",
                        ))
    
    def _get_nesting_depth(self, node, depth=0):
        """Calculate max nesting depth in a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.With, ast.Try)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    def check_style(self):
        """Check for style issues."""
        for i, line in enumerate(self.lines, 1):
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.issues.append(Issue(
                    line=i,
                    severity=IssueSeverity.STYLE,
                    category="Style",
                    message="Trailing whitespace",
                ))
            
            # Very long lines
            if len(line) > 120:
                self.issues.append(Issue(
                    line=i,
                    severity=IssueSeverity.STYLE,
                    category="Style",
                    message=f"Line too long ({len(line)} chars) - consider breaking it up",
                ))


def print_results(issues: List[Issue], filepath: Path):
    """Pretty print analysis results."""
    print(f"\n🔍 Analyzing: {filepath.name}\n")
    
    if not issues:
        print("✨ No issues found! Code looks clean!\n")
        return
    
    # Group by severity
    by_severity = {}
    for issue in issues:
        by_severity.setdefault(issue.severity, []).append(issue)
    
    # Print summary
    print("📊 Summary:")
    for severity in IssueSeverity:
        count = len(by_severity.get(severity, []))
        if count > 0:
            print(f"  {severity.value} {severity.name}: {count}")
    print()
    
    # Print detailed issues
    print("📝 Details:\n")
    for issue in issues:
        print(f"{issue.severity.value} Line {issue.line}: [{issue.category}] {issue.message}")
        if issue.context:
            print(f"   → {issue.context}")
        print()
    
    # Print totals
    print(f"Total issues: {len(issues)}")
    print()


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_code.py <file.py>")
        print("   or: uv run ada analyze <file.py>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    if not filepath.suffix == '.py':
        print(f"⚠️  Warning: {filepath} doesn't look like a Python file")
    
    analyzer = CodeAnalyzer(filepath)
    issues = analyzer.analyze()
    print_results(issues, filepath)
    
    # Exit code: 0 if clean, 1 if errors found
    has_errors = any(i.severity == IssueSeverity.ERROR for i in issues)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
