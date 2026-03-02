"""
Ada Swarm Configuration
Configures LiteLLM proxy for Pydantic AI agents using LiteLLMProvider
"""
import os
from typing import Dict, List

# LiteLLM Proxy Configuration
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

# Export for LiteLLMProvider to use
LITELLM_API_BASE = LITELLM_PROXY_URL
LITELLM_API_KEY = LITELLM_MASTER_KEY

if LITELLM_PROXY_URL:
    print(f"✨ LiteLLM proxy configured: {LITELLM_PROXY_URL}")
    print(f"   Use model format: 'litellm/model-name' where model-name matches proxy config")
else:
    print("⚠️  No LITELLM_PROXY_URL set, using direct provider access")

# === Agent Model Configuration ===
# Role-based model selection with priority and fallback chains
# Format: litellm/model-name where model-name matches proxy config
#
# Strategy:
# - Queen: Most powerful models for strategic thinking (gemini-pro, kimi-pro)
# - Workers: Fast, reliable models for implementation (gemini-flash, kimi-code)
# - Drones: Fastest models for simple read-only tasks (gemini-flash, kimi-8k)
#
# Note: LiteLLM proxy handles automatic fallbacks per litellm-proxy-config.yaml
# These are just the preferred starting models for each role.

AGENT_MODEL_CONFIG: Dict[str, Dict[str, any]] = {
    "queen": {
        "primary": "litellm/gemini-pro",    # Gemini 2.5 Pro - powerful reasoning
        "fallback": "litellm/kimi-pro",     # Kimi 128k - large context
        "description": "Strategic orchestrator - needs powerful reasoning",
        "max_tokens": 4096,
    },
    "coder": {
        "primary": "litellm/kimi-code",     # Kimi 32k - excellent for coding
        "fallback": "litellm/gemini-flash", # Gemini Flash - fast & free
        "description": "Implementation specialist - needs speed + quality",
        "max_tokens": 2048,
    },
    "researcher": {
        "primary": "litellm/gemini-pro",    # Gemini Pro - deep analysis
        "fallback": "litellm/kimi-pro",     # Kimi Pro - large context
        "description": "Research specialist - needs deep reasoning",
        "max_tokens": 4096,
    },
    "tester": {
        "primary": "litellm/kimi-code",     # Kimi - precise for testing
        "fallback": "litellm/gemini-flash", # Gemini Flash - fast
        "description": "Testing specialist - needs speed + precision",
        "max_tokens": 2048,
    },
    "reviewer": {
        "primary": "litellm/kimi-pro",      # Kimi Pro - thorough analysis
        "fallback": "litellm/gemini-pro",   # Gemini Pro - careful review
        "description": "Code reviewer - needs careful analysis",
        "max_tokens": 3072,
    },
    "drone": {
        "primary": "litellm/gemini-flash",  # Gemini Flash - fastest & free
        "fallback": "litellm/kimi-8k",      # Kimi 8k - fast alternative
        "description": "Simple read-only tasks - needs maximum speed",
        "max_tokens": 1024,
    },
}


def get_model_for_role(role: str, prefer_fallback: bool = False) -> str:
    """
    Get the appropriate model for an agent role.
    
    Args:
        role: Agent role (queen, coder, researcher, tester, reviewer, drone)
        prefer_fallback: If True, use fallback model instead of primary
    
    Returns:
        Model string in format 'litellm/model-name'
    """
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        # Default to fast model for unknown roles
        return "litellm/gemini-flash"
    
    return config["fallback"] if prefer_fallback else config["primary"]


def get_max_tokens_for_role(role: str) -> int:
    """
    Get the max_tokens setting for an agent role.
    
    Args:
        role: Agent role (queen, coder, researcher, tester, reviewer, drone)
    
    Returns:
        Maximum tokens for the role
    """
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        return 2048  # Default medium context
    
    return config["max_tokens"]


# Legacy model aliases (for backward compatibility)
DEFAULT_FAST_MODEL = "litellm/gemini-flash"
DEFAULT_SMART_MODEL = "litellm/gemini-pro"
DEFAULT_CODER_MODEL = "litellm/kimi-code"  # Kimi for coding!
