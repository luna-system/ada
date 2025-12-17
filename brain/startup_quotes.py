"""Startup quotes for Ada - a tribute to Vylet Pony and open culture.

All quotes from "Webpunk" by Vylet Pony, released freely without copyright.
A celebration of DIY, open source, and the magic of community.

@ai-indexable: utility
@ai-purpose: Random inspirational startup quotes from Vylet Pony's Webpunk
"""
import random
from typing import List


# Punchy lines from Webpunk by Vylet Pony (used with permission - no copyright)
WEBPUNK_QUOTES: List[str] = [
    "Revolution in a zip file, baby",
    "Copy, paste, archive, and send to your friends",
    "DIY is everything",
    "The magic isn't dead quite yet",
    "Plant, seed, retry, then do it again",
    "Taking back the ordinary",
]


def get_startup_quote() -> str:
    """Get a random startup quote from Webpunk.
    
    Returns:
        Random quote string from the collection
    """
    return random.choice(WEBPUNK_QUOTES)


def format_startup_banner(quote: str) -> str:
    """Format a quote as a startup banner.
    
    Args:
        quote: The quote to format
        
    Returns:
        Formatted banner string with decorative borders
    """
    width = len(quote) + 4
    border = "=" * width
    
    return f"\n{border}\n  {quote}  \n{border}\n"
