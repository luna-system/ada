"""
Ada Swarm Configuration
Configures LiteLLM to use proxy with fallback chains
"""
import os
import litellm

# Configure LiteLLM to use our proxy
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

if LITELLM_PROXY_URL:
    litellm.api_base = LITELLM_PROXY_URL
    litellm.api_key = LITELLM_MASTER_KEY
    print(f"✨ LiteLLM configured to use proxy: {LITELLM_PROXY_URL}")
else:
    print("⚠️  No LITELLM_PROXY_URL set, using direct provider access")

# Model aliases for convenience
DEFAULT_FAST_MODEL = "gemini-flash"
DEFAULT_SMART_MODEL = "gemini-pro"
DEFAULT_CODER_MODEL = "glm-flash"
