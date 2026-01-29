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
    print(f"   Use model format: 'openai/model-name' with LiteLLMProvider")
else:
    print("⚠️  No LITELLM_PROXY_URL set, using direct provider access")

# Model aliases - use with LiteLLMProvider
# Format: openai/model-name where model-name matches proxy config
DEFAULT_FAST_MODEL = "openai/gemini-flash"
DEFAULT_SMART_MODEL = "openai/gemini-pro"
DEFAULT_CODER_MODEL = "openai/glm-flash"  # Z.ai GLM through proxy!
