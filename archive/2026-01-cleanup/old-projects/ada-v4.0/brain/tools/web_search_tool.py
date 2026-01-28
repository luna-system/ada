"""
Web Search Tool - Real-time web search via SearxNG.

Provides access to current information from the web when the LLM realizes
it needs up-to-date facts, news, or information not in its training data.
"""
# @ai-indexable: tool-plugin
# @ai-purpose: Execute web searches when LLM requests current information via <web_search> XML tag
# @ai-activation-trigger: Bidirectional - LLM outputs <web_search>query</web_search> during generation
# @ai-priority: MEDIUM
# @ai-dependencies: httpx, SearxNG metasearch engine
# @ai-related: brain/tools/bidirectional.py, brain/prompt_builder.py
# @ai-tool-use-pattern: LLM emits XML tag mid-response → tool executes → results injected → LLM continues

import logging
import httpx
from typing import Dict, Any, Optional
from brain.tools.protocol import (
    BaseTool,
    ToolCapability,
    ToolResult,
    ToolPriority
)

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Web search tool using SearxNG metasearch engine.
    
    Executes web searches and returns formatted results when the LLM
    needs current information, news, or facts beyond its training data.
    """
    
    def __init__(self, searxng_url: Optional[str] = None):
        """
        Initialize web search tool.
        
        Args:
            searxng_url: Base URL for SearxNG instance (e.g., http://searxng:8080)
        """
        self.searxng_url = searxng_url
        self._capability = ToolCapability(
            name="web_search",
            description="Search the web for current information, news, facts, and real-time data",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
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
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    },
                    "query": {"type": "string"}
                }
            },
            context_priority=ToolPriority.HIGH,
            context_icon="🔍",
            tags=["web", "search", "current-events", "real-time"]
        )
    
    @property
    def capability(self) -> ToolCapability:
        return self._capability
    
    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """
        Web search is bidirectional only - activated by explicit request.
        
        Returns False for auto-activation since we don't want to search
        on every query. The LLM will request search when needed.
        """
        return False
    
    async def process(self, request_context: Dict[str, Any]) -> ToolResult:
        """
        Execute web search via SearxNG.
        
        Args:
            request_context: Must contain 'query' for search terms
            
        Returns:
            ToolResult with formatted search results
        """
        if not self.searxng_url:
            return self.error_result(
                "Web search is not configured. Set SEARXNG_URL environment variable.",
                request_context
            )
        
        query = request_context.get('query', '').strip()
        if not query:
            return self.error_result("Search query is required", request_context)
        
        num_results = request_context.get('num_results', 5)
        
        try:
            # Execute search via SearxNG JSON API
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.searxng_url}/search",
                    params={
                        'q': query,
                        'format': 'json',
                        'language': 'en',
                        'safesearch': 1  # Moderate safe search
                    },
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract results
            results = data.get('results', [])[:num_results]
            
            if not results:
                return self.success_result(
                    context_text=self.format_context({
                        'query': query,
                        'results': []
                    }),
                    data={'query': query, 'results': [], 'message': 'No results found'},
                    metadata={'search_engine': 'SearxNG', 'result_count': 0}
                )
            
            # Format results for LLM consumption
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', 'No title'),
                    'url': result.get('url', ''),
                    'content': result.get('content', '')[:300]  # Truncate to 300 chars
                })
            
            context_text = self.format_context({
                'query': query,
                'results': formatted_results
            })
            
            return self.success_result(
                context_text=context_text,
                data={'query': query, 'results': formatted_results},
                metadata={
                    'search_engine': 'SearxNG',
                    'result_count': len(formatted_results)
                }
            )
            
        except httpx.TimeoutException:
            logger.error(f"[WEB_SEARCH] Timeout searching for: {query}")
            return self.error_result(
                f"Search request timed out for query: {query}",
                request_context
            )
        except httpx.HTTPError as e:
            logger.error(f"[WEB_SEARCH] HTTP error: {e}")
            return self.error_result(
                f"Search service error: {str(e)}",
                request_context
            )
        except Exception as e:
            logger.error(f"[WEB_SEARCH] Unexpected error: {e}")
            return self.error_result(
                f"Search failed: {str(e)}",
                request_context
            )
    
    def format_context(self, data: Dict[str, Any]) -> str:
        """
        Format search results for LLM context injection.
        
        Args:
            data: Dict with 'query' and 'results' keys
            
        Returns:
            Formatted string for prompt injection
        """
        query = data.get('query', '')
        results = data.get('results', [])
        
        if not results:
            return f"🔍 Web Search Results for '{query}':\nNo results found."
        
        lines = [f"🔍 Web Search Results for '{query}':"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('url', '')
            content = result.get('content', '').strip()
            
            lines.append(f"\n{i}. {title}")
            if url:
                lines.append(f"   URL: {url}")
            if content:
                lines.append(f"   {content}")
        
        return "\n".join(lines)


# Lazy initialization - only create if SearxNG is configured
_web_search_instance = None

def get_web_search_tool() -> Optional[WebSearchTool]:
    """Get or create web search tool instance."""
    global _web_search_instance
    
    if _web_search_instance is None:
        import os
        searxng_url = os.getenv("SEARXNG_URL")
        if searxng_url:
            _web_search_instance = WebSearchTool(searxng_url)
            logger.info(f"[WEB_SEARCH] Initialized with SearxNG at {searxng_url}")
    
    return _web_search_instance


# Auto-register if configured
searxng_url = None
try:
    import os
    searxng_url = os.getenv("SEARXNG_URL")
except:
    pass

if searxng_url:
    # Create instance for auto-discovery
    web_search = WebSearchTool(searxng_url)
