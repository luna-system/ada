"""Shared Ada client for MCP tools."""
# @ai-indexable: mcp-infrastructure
# @ai-purpose: Reusable Ada HTTP client for tools

import os
from ada_client import AdaClient

_client_instance: AdaClient | None = None


def get_ada_client() -> AdaClient:
    """Get or create shared Ada client instance.
    
    Returns:
        AdaClient configured with ADA_BASE_URL from environment
    """
    global _client_instance
    
    if _client_instance is None:
        base_url = os.getenv("ADA_BASE_URL", "http://localhost:8000")
        _client_instance = AdaClient(base_url=base_url)
    
    return _client_instance


def reset_client():
    """Reset client instance (useful for testing)."""
    global _client_instance
    _client_instance = None
