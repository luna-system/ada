"""
Ada Swarm Configuration
Gemini-only (March 2026) - Kimi connectivity issues, using Gemini + Local fallback
"""
import os
from typing import Dict, List

# LiteLLM Proxy Configuration
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

LITELLM_API_BASE = LITELLM_PROXY_URL
LITELLM_API_KEY = LITELLM_MASTER_KEY

if LITELLM_PROXY_URL:
    print(f"✨ LiteLLM proxy configured: {LITELLM_PROXY_URL}")
else:
    print("⚠️  No LITELLM_PROXY_URL set")

# === Agent Model Configuration - Gemini Only ===
# NOTE: Kimi/Moonshot connectivity issues as of March 2026
# Using Gemini (free) + Local (fallback) until resolved

AGENT_MODEL_CONFIG: Dict[str, Dict[str, any]] = {
    "queen": {
        "primary": "litellm/gemini-pro",      # Gemini 2.5 Pro - powerful reasoning
        "fallback": "litellm/gemini-2.5-pro", # Fallback within Gemini family
        "description": "Strategic orchestrator - needs powerful reasoning",
        "max_tokens": 4096,
    },
    "coder": {
        "primary": "litellm/gemini-2.5-pro",  # Gemini 2.5 Pro - excellent for coding
        "fallback": "litellm/gemini-flash",   # Gemini Flash - fast & free
        "description": "Implementation specialist - needs speed + quality",
        "max_tokens": 2048,
    },
    "researcher": {
        "primary": "litellm/gemini-pro",      # Gemini Pro - deep analysis
        "fallback": "litellm/gemini-2.5-pro", # Gemini 2.5 Pro
        "description": "Research specialist - needs deep reasoning",
        "max_tokens": 4096,
    },
    "tester": {
        "primary": "litellm/gemini-flash",    # Gemini Flash - fast for testing
        "fallback": "litellm/gemini-2.5-flash",
        "description": "Testing specialist - needs speed + precision",
        "max_tokens": 2048,
    },
    "reviewer": {
        "primary": "litellm/gemini-pro",      # Gemini Pro - thorough analysis
        "fallback": "litellm/gemini-2.5-pro",
        "description": "Code reviewer - needs careful analysis",
        "max_tokens": 3072,
    },
    "drone": {
        "primary": "litellm/gemini-flash",    # Gemini Flash - fastest & free
        "fallback": "litellm/local-llama",    # Local fallback
        "description": "Simple read-only tasks - needs maximum speed",
        "max_tokens": 1024,
    },
}


def get_model_for_role(role: str, prefer_fallback: bool = False) -> str:
    """Get the appropriate model for an agent role."""
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        return "litellm/gemini-flash"
    return config["fallback"] if prefer_fallback else config["primary"]


def get_max_tokens_for_role(role: str) -> int:
    """Get the max_tokens setting for an agent role."""
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        return 2048
    return config["max_tokens"]


# Legacy aliases
DEFAULT_FAST_MODEL = "litellm/gemini-flash"
DEFAULT_SMART_MODEL = "litellm/gemini-pro"
DEFAULT_CODER_MODEL = "litellm/gemini-2.5-pro"
