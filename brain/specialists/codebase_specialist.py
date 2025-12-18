"""
Codebase Specialist - Ada's self-awareness of her own code.

Phase 1 MVP: Keyword-based function and class lookup using AST parsing.
Enables Ada to look up her own functions, classes, and implementation details.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Look up functions and classes in Ada's codebase for self-reference
# @ai-activation-trigger: Bidirectional - LLM outputs <code_lookup>name</code_lookup>
# @ai-priority: HIGH
# @ai-dependencies: ast (stdlib), pathlib (stdlib)
# @ai-related: brain/specialists/docs_specialist.py, brain/specialists/bidirectional.py
# @ai-tool-use-pattern: LLM emits <code_lookup> tag → searches code index → returns definition + docstring → LLM continues

import ast
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class CodeIndexer:
    """Parses Python files and builds an index of functions and classes."""
    
    def __init__(self, root_dir: Path):
        """
        Initialize code indexer.
        
        Args:
            root_dir: Root directory to index (typically brain/)
        """
        self.root_dir = root_dir
        self.index: Dict[str, List[Dict[str, Any]]] = {}
    
    def build_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Walk directory tree and index all Python files.
        
        Returns:
            Dict mapping names to list of locations where they're defined
        """
        logger.info(f"Building code index from {self.root_dir}")
        
        # Walk the directory tree
        for py_file in self.root_dir.rglob("*.py"):
            # Skip test files
            if 'test_' in py_file.name or '/tests/' in str(py_file):
                continue
            
            # Skip __pycache__ and other generated dirs
            if '__pycache__' in str(py_file):
                continue
            
            try:
                self._index_file(py_file)
            except Exception as e:
                logger.warning(f"Failed to index {py_file}: {e}")
                continue
        
        logger.info(f"Indexed {len(self.index)} names from {self.root_dir}")
        return self.index
    
    def _index_file(self, file_path: Path):
        """
        Parse a single Python file and extract definitions.
        
        Args:
            file_path: Path to Python file to parse
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return
        
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return
        
        # Extract all function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._index_function(node, file_path, source)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._index_function(node, file_path, source)
            elif isinstance(node, ast.ClassDef):
                self._index_class(node, file_path, source)
    
    def _index_function(self, node: ast.FunctionDef, file_path: Path, source: str):
        """Index a function definition."""
        name = node.name
        
        # Get docstring if present
        docstring = ast.get_docstring(node)
        
        # Get function source code
        try:
            # Get line range for the function
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            
            # Extract source lines
            source_lines = source.split('\n')
            func_source = '\n'.join(source_lines[start_line-1:end_line])
        except Exception as e:
            logger.debug(f"Could not extract source for {name}: {e}")
            func_source = f"def {name}(...)"
        
        # Add to index
        if name not in self.index:
            self.index[name] = []
        
        self.index[name].append({
            'type': 'function',
            'name': name,
            'file': str(file_path.relative_to(self.root_dir.parent)),
            'line': node.lineno,
            'docstring': docstring,
            'code': func_source,
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        })
    
    def _index_class(self, node: ast.ClassDef, file_path: Path, source: str):
        """Index a class definition."""
        name = node.name
        
        # Get docstring if present
        docstring = ast.get_docstring(node)
        
        # Get class source code (just the class definition line and docstring)
        try:
            start_line = node.lineno
            # For classes, we'll extract just the first few lines (class def + docstring)
            # Not the entire class body (which could be huge)
            source_lines = source.split('\n')
            
            # Get class definition line
            class_def_line = source_lines[start_line-1]
            
            # Get up to next 10 lines or until we hit a method/large body
            preview_lines = [class_def_line]
            for i in range(start_line, min(start_line + 10, len(source_lines))):
                line = source_lines[i]
                # Stop if we hit a method definition
                if line.strip().startswith('def ') or line.strip().startswith('async def '):
                    break
                preview_lines.append(line)
            
            class_source = '\n'.join(preview_lines)
        except Exception as e:
            logger.debug(f"Could not extract source for class {name}: {e}")
            class_source = f"class {name}:"
        
        # Add to index
        if name not in self.index:
            self.index[name] = []
        
        # Get base classes
        bases = [ast.unparse(base) if hasattr(ast, 'unparse') else 'object' for base in node.bases]
        
        self.index[name].append({
            'type': 'class',
            'name': name,
            'file': str(file_path.relative_to(self.root_dir.parent)),
            'line': node.lineno,
            'docstring': docstring,
            'code': class_source,
            'bases': bases
        })


class CodebaseSpecialist(BaseSpecialist):
    """
    Codebase specialist - enables Ada to look up her own code.
    
    Phase 1 MVP: Keyword-based lookup of functions and classes using AST parsing.
    """
    
    def __init__(self, code_dir: Optional[Path] = None):
        """
        Initialize codebase specialist.
        
        Args:
            code_dir: Directory to index (defaults to brain/)
        """
        if code_dir is None:
            # Default to brain/ directory
            project_root = Path(__file__).parent.parent.parent
            code_dir = project_root / "brain"
        
        self.code_dir = Path(code_dir)
        
        # Build index of all functions and classes
        indexer = CodeIndexer(self.code_dir)
        self.index = indexer.build_index()
        
        self._capability = SpecialistCapability(
            name="codebase",
            description="Look up functions and classes in Ada's codebase for self-reference and introspection",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Function or class name to look up"
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "file": {"type": "string"},
                                "line": {"type": "integer"},
                                "code": {"type": "string"},
                                "docstring": {"type": "string"}
                            }
                        }
                    },
                    "query": {"type": "string"}
                }
            },
            context_priority=SpecialistPriority.HIGH,
            context_icon="💻",
            tags=["codebase", "self-reference", "introspection", "code-lookup"]
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        return self._capability
    
    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """
        Codebase lookup is bidirectional only - activated by explicit request.
        
        Returns False for auto-activation. Only activated when LLM explicitly
        requests a code lookup via <code_lookup> tags.
        """
        return False
    
    async def process(self, request_context: Dict[str, Any]) -> SpecialistResult:
        """
        Look up a function or class by name.
        
        Args:
            request_context: Must contain 'query' with function/class name
            
        Returns:
            SpecialistResult with code definition and docstring
        """
        query = request_context.get('query', '').strip()
        
        if not query:
            return self.error_result(
                "Query is required for code lookup (empty query provided)",
                request_context
            )
        
        # Search index
        results = self.index.get(query, [])
        
        if not results:
            return self.error_result(
                f"Code item '{query}' not found in codebase index",
                request_context
            )
        
        # Format results for LLM context
        context_text = self._format_results(query, results)
        
        return SpecialistResult(
            success=True,
            specialist_name="codebase",
            context_text=context_text,
            data={
                "query": query,
                "results": results,
                "count": len(results)
            }
        )
    
    def _format_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Format code lookup results for LLM context.
        
        Args:
            query: Original query
            results: List of matching code items
            
        Returns:
            Formatted string for LLM context injection
        """
        if len(results) == 1:
            # Single result - detailed format
            item = results[0]
            parts = [
                f"💻 Code Lookup: {query}",
                f"",
                f"**Type:** {item['type'].title()}",
                f"**File:** {item['file']}",
                f"**Line:** {item['line']}",
                f""
            ]
            
            if item.get('docstring'):
                parts.append(f"**Documentation:**")
                parts.append(item['docstring'])
                parts.append("")
            
            parts.append(f"**Code:**")
            parts.append("```python")
            parts.append(item['code'])
            parts.append("```")
            
            return '\n'.join(parts)
        
        else:
            # Multiple results - summarized format
            parts = [
                f"💻 Code Lookup: {query}",
                f"",
                f"Found {len(results)} definitions:",
                ""
            ]
            
            for i, item in enumerate(results, 1):
                parts.append(f"### {i}. {item['type'].title()} in {item['file']}:{item['line']}")
                
                if item.get('docstring'):
                    # First line of docstring only for multiple results
                    first_line = item['docstring'].split('\n')[0]
                    parts.append(f"   {first_line}")
                
                parts.append("")
                parts.append("```python")
                parts.append(item['code'][:300] + "..." if len(item['code']) > 300 else item['code'])
                parts.append("```")
                parts.append("")
            
            return '\n'.join(parts)
