"""
Wiki Specialist - Look up information from MediaWiki-based wikis.

Provides access to wiki content from Wikipedia, Fandom wikis, and other
MediaWiki-powered sites. Perfect for answering questions about specific
topics, fandoms, games, shows, and more.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Fetch and parse MediaWiki wiki pages when LLM requests information via <wiki_lookup> XML tag
# @ai-activation-trigger: Bidirectional - LLM outputs <wiki_lookup wiki="..." page="..."/> during generation
# @ai-priority: MEDIUM
# @ai-dependencies: httpx
# @ai-related: brain/specialists/bidirectional.py, brain/prompt_builder.py
# @ai-tool-use-pattern: LLM emits XML tag mid-response → specialist executes → wiki content injected → LLM continues

import logging
import httpx
import re
from typing import Dict, Any, Optional, List
from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)

# Predefined wiki configurations
WIKI_CONFIGS = {
    "wikipedia": {
        "name": "Wikipedia",
        "api_url": "https://en.wikipedia.org/w/api.php",
        "base_url": "https://en.wikipedia.org/wiki/"
    },
    "bfdi": {
        "name": "Battle for Dream Island Wiki",
        "api_url": "https://battlefordreamisland.fandom.com/api.php",
        "base_url": "https://battlefordreamisland.fandom.com/wiki/"
    },
    "objectshowfanonpedia": {
        "name": "Object Show Fanonpedia",
        "api_url": "https://objectshowfanonpedia.fandom.com/api.php",
        "base_url": "https://objectshowfanonpedia.fandom.com/wiki/"
    },
    "objectshows": {
        "name": "Object Shows Community",
        "api_url": "https://objectshows.fandom.com/api.php",
        "base_url": "https://objectshows.fandom.com/wiki/"
    },
}


class WikiSpecialist(BaseSpecialist):
    """
    Wiki specialist for MediaWiki-based sites.
    
    Fetches and parses wiki pages from Wikipedia, Fandom, and other
    MediaWiki sites. Handles page lookups, redirects, and text extraction.
    """
    
    def __init__(self):
        """Initialize wiki specialist with predefined wiki configurations."""
        self._capability = SpecialistCapability(
            name="wiki_lookup",
            description="Look up information from MediaWiki-based wikis (Wikipedia, Fandom, etc.)",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "wiki": {
                        "type": "string",
                        "description": "Wiki to search (wikipedia, bfdi, objectshowfanonpedia, objectshows, or custom URL)",
                        "enum": list(WIKI_CONFIGS.keys())
                    },
                    "page": {
                        "type": "string",
                        "description": "Page title to look up"
                    },
                    "search": {
                        "type": "boolean",
                        "description": "If true and page not found, search for similar pages",
                        "default": True
                    }
                },
                "required": ["wiki", "page"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "extract": {"type": "string"},
                    "url": {"type": "string"},
                    "wiki": {"type": "string"}
                }
            },
            context_priority=SpecialistPriority.MEDIUM
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        """Return specialist capability metadata."""
        return self._capability
    
    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """
        This is a bidirectional specialist - activation handled by prompt_builder.
        
        The LLM can request wiki lookups by outputting:
        <wiki_lookup wiki="wikipedia" page="Article Title"/>
        
        Args:
            request_context: Request context (unused for bidirectional specialists)
            
        Returns:
            False (bidirectional specialists don't auto-activate)
        """
        return False
    
    def process(self, request_context: Dict[str, Any]) -> SpecialistResult:
        """
        Process wiki lookup request from LLM.
        
        Args:
            request_context: Must contain 'wiki' and 'page' keys
            
        Returns:
            SpecialistResult with wiki page content or error
        """
        wiki_name = request_context.get("wiki", "wikipedia")
        page_title = request_context.get("page", "")
        do_search = request_context.get("search", True)
        
        if not page_title:
            return SpecialistResult(
                success=False,
                specialist_name=self.capability.name,
                context_text="❌ No page title provided",
                error="No page title provided",
                error_code="missing_page_title"
            )
        
        try:
            # Get wiki config
            if wiki_name not in WIKI_CONFIGS:
                return SpecialistResult(
                    success=False,
                    specialist_name=self.capability.name,
                    context_text=f"❌ Unknown wiki: {wiki_name}. Available: {', '.join(WIKI_CONFIGS.keys())}",
                    error=f"Unknown wiki: {wiki_name}",
                    error_code="unknown_wiki",
                    metadata={"wiki": wiki_name}
                )
            
            wiki_config = WIKI_CONFIGS[wiki_name]
            
            # Fetch page content
            page_data = self._fetch_page(wiki_config, page_title)
            
            if page_data:
                # Successfully found page
                formatted_content = self._format_wiki_result(page_data, wiki_config)
                
                return SpecialistResult(
                    success=True,
                    specialist_name=self.capability.name,
                    context_text=formatted_content,
                    data=page_data,
                    metadata={
                        "wiki": wiki_name,
                        "wiki_display_name": wiki_config["name"],
                        "page_title": page_data["title"],
                        "page_url": page_data["url"],
                        "extract_length": len(page_data["extract"])
                    }
                )
            elif do_search:
                # Page not found, try searching
                search_results = self._search_wiki(wiki_config, page_title)
                
                if search_results:
                    suggestions = ", ".join([f'"{r}"' for r in search_results[:5]])
                    return SpecialistResult(
                        success=False,
                        specialist_name=self.capability.name,
                        context_text=f"❓ Page '{page_title}' not found on {wiki_config['name']}. Did you mean: {suggestions}?",
                        error="Page not found",
                        error_code="not_found_with_suggestions",
                        metadata={
                            "wiki": wiki_name,
                            "search_query": page_title,
                            "suggestions": search_results[:5]
                        }
                    )
            
            # Nothing found
            return SpecialistResult(
                success=False,
                specialist_name=self.capability.name,
                context_text=f"❌ Page '{page_title}' not found on {wiki_config['name']}.",
                error="Page not found",
                error_code="not_found",
                metadata={"wiki": wiki_name, "page_title": page_title}
            )
            
        except Exception as e:
            logger.error(f"Wiki lookup error: {e}", exc_info=True)
            return SpecialistResult(
                success=False,
                specialist_name=self.capability.name,
                context_text=f"❌ Failed to look up '{page_title}' on {wiki_name}: {str(e)}",
                error=str(e),
                error_code="lookup_failed",
                metadata={"wiki": wiki_name, "page_title": page_title}
            )
    
    def _fetch_page(self, wiki_config: Dict[str, str], page_title: str) -> Optional[Dict[str, str]]:
        """
        Fetch page content from MediaWiki API.
        
        Args:
            wiki_config: Wiki configuration with api_url and base_url
            page_title: Page title to fetch
            
        Returns:
            Dict with title, extract, and url, or None if not found
        """
        try:
            params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "extracts|info",
                "exintro": True,  # Only intro section
                "explaintext": True,  # Plain text, no HTML
                "redirects": 1,  # Follow redirects
                "inprop": "url"
            }
            
            headers = {
                "User-Agent": "Ada/1.3.0 (https://github.com/luna-system/ada) Python/httpx"
            }
            
            with httpx.Client(timeout=10.0, headers=headers) as client:
                response = client.get(wiki_config["api_url"], params=params)
                response.raise_for_status()
                data = response.json()
            
            # Extract page data
            pages = data.get("query", {}).get("pages", {})
            
            if not pages:
                return None
            
            # Get first (and should be only) page
            page = next(iter(pages.values()))
            
            # Check if page exists
            if "missing" in page or "invalid" in page:
                return None
            
            # Extract text (limit to ~1000 chars for context)
            extract = page.get("extract", "")
            if len(extract) > 1000:
                # Truncate at sentence boundary
                extract = extract[:1000]
                last_period = extract.rfind(".")
                if last_period > 500:  # Only truncate if we have a good break point
                    extract = extract[:last_period + 1]
                extract += "..."
            
            return {
                "title": page.get("title", page_title),
                "extract": extract,
                "url": page.get("fullurl", f"{wiki_config['base_url']}{page_title.replace(' ', '_')}")
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch page '{page_title}' from {wiki_config['name']}: {e}")
            return None
    
    def _search_wiki(self, wiki_config: Dict[str, str], query: str) -> List[str]:
        """
        Search wiki for pages matching query.
        
        Args:
            wiki_config: Wiki configuration
            query: Search query
            
        Returns:
            List of page titles matching query
        """
        try:
            params = {
                "action": "opensearch",
                "format": "json",
                "search": query,
                "limit": 5
            }
            
            headers = {
                "User-Agent": "Ada/1.3.0 (https://github.com/luna-system/ada) Python/httpx"
            }
            
            with httpx.Client(timeout=10.0, headers=headers) as client:
                response = client.get(wiki_config["api_url"], params=params)
                response.raise_for_status()
                data = response.json()
            
            # OpenSearch returns [query, [titles], [descriptions], [urls]]
            if len(data) >= 2 and isinstance(data[1], list):
                return data[1]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to search {wiki_config['name']}: {e}")
            return []
    
    def _format_wiki_result(self, page_data: Dict[str, str], wiki_config: Dict[str, str]) -> str:
        """
        Format wiki page data for inclusion in prompt.
        
        Args:
            page_data: Page data with title, extract, url
            wiki_config: Wiki configuration
            
        Returns:
            Formatted wiki content string
        """
        return f"""📖 **{page_data['title']}** (from {wiki_config['name']})

{page_data['extract']}

Source: {page_data['url']}"""


# Export for auto-discovery
__all__ = ["WikiSpecialist"]
