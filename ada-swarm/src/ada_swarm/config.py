"""
Ada Swarm Configuration
Gemini-only (March 2026) - Using working Gemini models
"""
import os
from pathlib import Path
from typing import Dict, List

# Load environment variables from .env file if not already set
# This ensures the Hive spawner and all agents get proper config
try:
    from dotenv import load_dotenv
    # Try to load from .env in parent directory (project root)
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✨ Loaded environment from {env_path}")
except ImportError:
    pass  # dotenv not installed, rely on existing env vars

LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

LITELLM_API_BASE = LITELLM_PROXY_URL
LITELLM_API_KEY = LITELLM_MASTER_KEY

if LITELLM_PROXY_URL:
    print(f"✨ LiteLLM proxy configured: {LITELLM_PROXY_URL}")
    if LITELLM_MASTER_KEY:
        print(f"   API Key: {LITELLM_MASTER_KEY[:10]}...")
    else:
        print("   ⚠️  Warning: No LITELLM_MASTER_KEY set!")

# === Agent Model Configuration - Gemini 1.5 (Paid Tier) ===
# Using Gemini 1.5 models which are in Luna's paid tier with better rate limits!
AGENT_MODEL_CONFIG: Dict[str, Dict[str, any]] = {
    "queen": {
        "primary": "litellm/gemini-pro",      # Gemini 1.5 Pro - most capable
        "fallback": "litellm/gemini-flash",   # Fallback to Gemini 1.5 Flash
        "description": "Strategic orchestrator",
        "max_tokens": 4096,
    },
    "coder": {
        "primary": "litellm/gemini-flash",    # Gemini 1.5 Flash - fast & capable
        "fallback": "litellm/gemini-pro",
        "description": "Implementation specialist",
        "max_tokens": 2048,
    },
    "researcher": {
        "primary": "litellm/gemini-pro",      # Deep reasoning
        "fallback": "litellm/gemini-flash",
        "description": "Research specialist",
        "max_tokens": 4096,
    },
    "tester": {
        "primary": "litellm/gemini-flash",    # Fast for testing
        "fallback": "litellm/gemini-pro",
        "description": "Testing specialist",
        "max_tokens": 2048,
    },
    "reviewer": {
        "primary": "litellm/gemini-pro",      # Thorough analysis
        "fallback": "litellm/gemini-flash",
        "description": "Code reviewer",
        "max_tokens": 3072,
    },
    "drone": {
        "primary": "litellm/gemini-flash",    # Fastest
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
