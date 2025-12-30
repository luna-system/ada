"""
Ada v4.0 - Specialist System

Clean plugin architecture with ONLY essential specialists:
- web_search (SearxNG)
- wiki_lookup (Wikipedia/MediaWiki)

More can be added later as drop-in plugins!
"""

from typing import List, Optional
from brain.specialists.protocol import BaseSpecialist

# Import essential specialists
from brain.specialists.web_search_specialist import WebSearchSpecialist
from brain.specialists.wiki_specialist import WikiSpecialist

# Registry of active specialists
_SPECIALISTS = {
    "web_search": WebSearchSpecialist(),
    "wiki_lookup": WikiSpecialist(),
}


def list_specialists() -> List[BaseSpecialist]:
    """Get all active specialists."""
    return list(_SPECIALISTS.values())


def get_specialist(name: str) -> Optional[BaseSpecialist]:
    """Get a specialist by name."""
    return _SPECIALISTS.get(name)


__all__ = ['list_specialists', 'get_specialist', 'BaseSpecialist']
