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
# - Queen: Most powerful models for strategic thinking (gemini-pro, glm-plus)
# - Workers: Fast, reliable models for implementation (gemini-flash, glm-flash)
# - Drones: Fastest models for simple read-only tasks (gemini-flash, glm-flash)
#
# Note: LiteLLM proxy handles automatic fallbacks per litellm-proxy-config.yaml
# These are just the preferred starting models for each role.

AGENT_MODEL_CONFIG: Dict[str, Dict[str, any]] = {
    "queen": {
        "primary": "litellm/gemini-pro",  # gemini-exp-1206 (Gemini 2.5 Pro preview)
        "fallback": "litellm/glm-plus",   # glm-4.7 (Z.ai newest)
        "description": "Strategic orchestrator - needs powerful reasoning",
        "max_tokens": 4096,  # Higher context for complex planning
    },
    "coder": {
        "primary": "litellm/gemini-flash",  # gemini-2.0-flash-exp (fast & free)
        "fallback": "litellm/glm-flash",    # glm-4.5-flash (Z.ai fast)
        "description": "Implementation specialist - needs speed + quality",
        "max_tokens": 2048,  # Medium context for code implementation
    },
    "researcher": {
        "primary": "litellm/gemini-pro",    # gemini-exp-1206 (deep analysis)
        "fallback": "litellm/glm-stable",   # glm-4.6 (reliable)
        "description": "Research specialist - needs deep reasoning",
        "max_tokens": 4096,  # Higher context for research
    },
    "tester": {
        "primary": "litellm/gemini-flash",  # gemini-2.0-flash-exp (fast)
        "fallback": "litellm/glm-flash",    # glm-4.5-flash (fast)
        "description": "Testing specialist - needs speed + precision",
        "max_tokens": 2048,  # Medium context for test generation
    },
    "reviewer": {
        "primary": "litellm/gemini-pro",    # gemini-exp-1206 (thorough analysis)
        "fallback": "litellm/glm-stable",   # glm-4.6 (reliable)
        "description": "Code reviewer - needs careful analysis",
        "max_tokens": 3072,  # Higher context for code review
    },
    "drone": {
        "primary": "litellm/gemini-flash",  # gemini-2.0-flash-exp (fastest)
        "fallback": "litellm/glm-flash",    # glm-4.5-flash (fast)
        "description": "Simple read-only tasks - needs maximum speed",
        "max_tokens": 1024,  # Lower context for simple tasks
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
    
    Examples:
        >>> get_model_for_role("queen")
        'litellm/gemini-pro'
        >>> get_model_for_role("drone")
        'litellm/gemini-flash'
        >>> get_model_for_role("coder", prefer_fallback=True)
        'litellm/glm-flash'
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
DEFAULT_CODER_MODEL = "litellm/glm-flash"  # Z.ai GLM through proxy!
