"""
Ada v4.0 - Tool System

Clean plugin architecture with ONLY essential tools:
- web_search (SearxNG)
- wiki_lookup (Wikipedia/MediaWiki)

More can be added later as drop-in plugins!
"""

from typing import List, Optional
from brain.tools.protocol import BaseTool

# Import essential tools
from brain.tools.web_search_tool import WebSearchTool
from brain.tools.wiki_tool import WikiTool
from brain.tools.docs_tool import DocsTool

from brain import config

# Registry of active tools
_TOOLS = {
    "web_search": WebSearchTool(config.SEARXNG_URL),
    "wiki_lookup": WikiTool(),
    "docs_lookup": DocsTool(),
}


def list_tools() -> List[BaseTool]:
    """Get all active tools."""
    return list(_TOOLS.values())


def get_tool(name: str) -> Optional[BaseTool]:
    """Get a tool by name."""
    return _TOOLS.get(name)


__all__ = ['list_tools', 'get_tool', 'BaseTool']
