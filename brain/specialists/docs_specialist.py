"""
Documentation Specialist - Ada reads her own documentation.

Provides access to the built Sphinx documentation so Ada can look up
her own capabilities, API details, and usage instructions.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Search and retrieve Sphinx documentation content for self-reference
# @ai-activation-trigger: Bidirectional - LLM outputs <docs>topic</docs> during generation
# @ai-priority: HIGH
# @ai-dependencies: pathlib, html.parser (stdlib)
# @ai-related: brain/specialists/bidirectional.py, brain/prompt_builder.py, docs/
# @ai-tool-use-pattern: LLM emits <docs_lookup> tag → searches built HTML → returns relevant docs → LLM continues

import logging
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional, Tuple
from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class HTMLTextExtractor(HTMLParser):
    """Simple HTML parser that extracts clean text content."""
    
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.current_heading = None
        self.in_code_block = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['h1', 'h2', 'h3', 'h4']:
            self.current_heading = tag
        elif tag in ['pre', 'code']:
            self.in_code_block = True
    
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4']:
            self.current_heading = None
        elif tag in ['pre', 'code']:
            self.in_code_block = False
    
    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.text_chunks.append(cleaned)
    
    def get_text(self) -> str:
        return '\n'.join(self.text_chunks)


class DocumentationSpecialist(BaseSpecialist):
    """
    Documentation specialist - enables Ada to read her own docs.
    
    Searches the built Sphinx HTML documentation and returns relevant
    sections when Ada needs to reference her own capabilities.
    """
    
    def __init__(self, docs_dir: Optional[Path] = None):
        """
        Initialize documentation specialist.
        
        Args:
            docs_dir: Path to built docs directory (defaults to docs/_build/html)
        """
        if docs_dir is None:
            # Default to docs/_build/html relative to project root
            project_root = Path(__file__).parent.parent.parent
            docs_dir = project_root / "docs" / "_build" / "html"
        
        self.docs_dir = Path(docs_dir)
        self._capability = SpecialistCapability(
            name="docs",
            description="Search and retrieve Ada's own Sphinx documentation for self-reference",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic or keyword to look up in documentation"
                    },
                    "section": {
                        "type": "string",
                        "description": "Specific documentation section (e.g., 'api_usage', 'specialists')",
                        "default": None
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
                                "file": {"type": "string"},
                                "title": {"type": "string"},
                                "excerpt": {"type": "string"},
                                "relevance": {"type": "number"}
                            }
                        }
                    },
                    "query": {"type": "string"}
                }
            },
            context_priority=SpecialistPriority.HIGH,
            context_icon="📚",
            tags=["documentation", "self-reference", "introspection"]
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        return self._capability
    
    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """
        Documentation lookup is bidirectional only - activated by explicit request.
        
        Returns False for auto-activation.
        """
        return False
    
    async def process(self, request_context: Dict[str, Any]) -> SpecialistResult:
        """
        Search documentation and return relevant sections.
        
        Args:
            request_context: Must contain 'query' for search terms
            
        Returns:
            SpecialistResult with formatted documentation excerpts
        """
        query = request_context.get('query', '').strip()
        if not query:
            return self.error_result("Documentation query is required", request_context)
        
        section_filter = request_context.get('section')
        
        # Check if docs directory exists
        if not self.docs_dir.exists():
            return self.error_result(
                f"Documentation not built. Run 'cd docs && make html' to build docs.",
                request_context
            )
        
        try:
            # Search documentation files
            results = self._search_docs(query, section_filter)
            
            if not results:
                return self.success_result(
                    context_text=f"📚 Searched documentation for '{query}' but found no relevant sections.\n\n"
                                f"The documentation may not cover this topic yet.",
                    data={'query': query, 'results': [], 'message': 'No relevant sections found'},
                    metadata={'docs_dir': str(self.docs_dir), 'files_searched': 0}
                )
            
            # Format results for LLM
            context_text = self._format_results(query, results)
            
            return self.success_result(
                context_text=context_text,
                data={
                    'query': query,
                    'results': [
                        {
                            'file': r['file'],
                            'title': r['title'],
                            'excerpt': r['excerpt'],
                            'relevance': r['relevance']
                        }
                        for r in results
                    ]
                },
                metadata={
                    'docs_dir': str(self.docs_dir),
                    'result_count': len(results),
                    'section_filter': section_filter
                }
            )
            
        except Exception as e:
            logger.error(f"Documentation search error: {e}", exc_info=True)
            return self.error_result(f"Documentation search failed: {str(e)}", request_context)
    
    def _search_docs(self, query: str, section_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search HTML documentation files for query terms.
        
        Args:
            query: Search terms
            section_filter: Optional specific section to search
            
        Returns:
            List of result dicts with file, title, excerpt, relevance
        """
        query_terms = query.lower().split()
        results = []
        
        # Find HTML files to search
        html_files = list(self.docs_dir.glob("**/*.html"))
        
        for html_file in html_files:
            # Skip if section filter specified and doesn't match
            if section_filter and section_filter not in html_file.stem:
                continue
            
            # Skip navigation/index files that aren't content
            if html_file.stem in ['genindex', 'search', 'modindex']:
                continue
            
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Extract text content
                parser = HTMLTextExtractor()
                parser.feed(content)
                text = parser.get_text()
                
                # Calculate relevance score
                text_lower = text.lower()
                relevance = sum(text_lower.count(term) for term in query_terms)
                
                if relevance > 0:
                    # Extract title (first heading or filename)
                    title = self._extract_title(content, html_file.stem)
                    
                    # Extract relevant excerpt
                    excerpt = self._extract_excerpt(text, query_terms)
                    
                    results.append({
                        'file': html_file.stem,
                        'title': title,
                        'excerpt': excerpt,
                        'relevance': relevance,
                        'path': str(html_file.relative_to(self.docs_dir))
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing {html_file}: {e}")
                continue
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Return top 3 results
        return results[:3]
    
    def _extract_title(self, html_content: str, fallback: str) -> str:
        """Extract page title from HTML."""
        # Try <title> tag
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up "Ada v1 - " prefix if present
            title = re.sub(r'^Ada v1\s*[-—]\s*', '', title)
            return title
        
        # Try first h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            # Strip HTML tags from heading
            heading = re.sub(r'<[^>]+>', '', h1_match.group(1))
            return heading.strip()
        
        # Fallback to filename
        return fallback.replace('_', ' ').title()
    
    def _extract_excerpt(self, text: str, query_terms: List[str], context_chars: int = 200) -> str:
        """Extract relevant excerpt containing query terms."""
        text_lower = text.lower()
        
        # Find first occurrence of any query term
        best_pos = -1
        for term in query_terms:
            pos = text_lower.find(term)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        
        if best_pos == -1:
            # No terms found (shouldn't happen), return start
            return text[:context_chars] + "..."
        
        # Extract context around the term
        start = max(0, best_pos - context_chars // 2)
        end = min(len(text), best_pos + context_chars // 2)
        
        excerpt = text[start:end].strip()
        
        # Add ellipsis if truncated
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def _format_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM consumption."""
        lines = [
            f"📚 **Documentation Lookup: '{query}'**",
            f"Found {len(results)} relevant section(s):",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            lines.extend([
                f"**{i}. {result['title']}** (from `{result['file']}.rst`)",
                f"   {result['excerpt']}",
                ""
            ])
        
        lines.append("---")
        return '\n'.join(lines)
