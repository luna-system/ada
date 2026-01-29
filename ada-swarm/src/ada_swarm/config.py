"""
Ada Swarm Configuration
Configures LiteLLM proxy for Pydantic AI agents using LiteLLMProvider
"""
import os

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

# Model aliases - use with LiteLLMProvider
# Format: litellm/model-name where model-name matches proxy config
DEFAULT_FAST_MODEL = "litellm/gemini-flash"
DEFAULT_SMART_MODEL = "litellm/gemini-pro"
DEFAULT_CODER_MODEL = "litellm/glm-flash"  # Z.ai GLM through proxy!
