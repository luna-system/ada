"""
Ada Swarm Configuration
Gemini-only (March 2026) - Using working Gemini models
"""
import os
from typing import Dict, List

LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

LITELLM_API_BASE = LITELLM_PROXY_URL
LITELLM_API_KEY = LITELLM_MASTER_KEY

if LITELLM_PROXY_URL:
    print(f"✨ LiteLLM proxy configured: {LITELLM_PROXY_URL}")

# === Agent Model Configuration - Gemini Only ===
# NOTE: Using gemini-2.5-flash as primary (tested working)
# gemini-pro has issues, gemini-2.5-pro not tested yet

AGENT_MODEL_CONFIG: Dict[str, Dict[str, any]] = {
    "queen": {
        "primary": "litellm/gemini-2.5-flash",    # Tested working
        "fallback": "litellm/gemini-flash",
        "description": "Strategic orchestrator",
        "max_tokens": 4096,
    },
    "coder": {
        "primary": "litellm/gemini-2.5-flash",    # Excellent for coding
        "fallback": "litellm/gemini-flash",
        "description": "Implementation specialist",
        "max_tokens": 2048,
    },
    "researcher": {
        "primary": "litellm/gemini-2.5-flash",
        "fallback": "litellm/gemini-flash",
        "description": "Research specialist",
        "max_tokens": 4096,
    },
    "tester": {
        "primary": "litellm/gemini-flash",        # Fast for testing
        "fallback": "litellm/gemini-2.5-flash",
        "description": "Testing specialist",
        "max_tokens": 2048,
    },
    "reviewer": {
        "primary": "litellm/gemini-2.5-flash",
        "fallback": "litellm/gemini-flash",
        "description": "Code reviewer",
        "max_tokens": 3072,
    },
    "drone": {
        "primary": "litellm/gemini-flash",        # Fastest
        "fallback": "litellm/local-llama",
        "description": "Simple read-only tasks",
        "max_tokens": 1024,
    },
}


def get_model_for_role(role: str, prefer_fallback: bool = False) -> str:
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        return "litellm/gemini-2.5-flash"
    return config["fallback"] if prefer_fallback else config["primary"]


def get_max_tokens_for_role(role: str) -> int:
    config = AGENT_MODEL_CONFIG.get(role.lower())
    if not config:
        return 2048
    return config["max_tokens"]


DEFAULT_FAST_MODEL = "litellm/gemini-flash"
DEFAULT_SMART_MODEL = "litellm/gemini-2.5-flash"
DEFAULT_CODER_MODEL = "litellm/gemini-2.5-flash"
