"""
Ada Swarm Configuration
Configures LiteLLM proxy for Pydantic AI agents
"""
import os

# LiteLLM Proxy Configuration
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

# For Pydantic AI, we need to use OpenAI-compatible mode
# Set these as environment variables so Pydantic AI picks them up
if LITELLM_PROXY_URL:
    os.environ["OPENAI_API_BASE"] = LITELLM_PROXY_URL
    os.environ["OPENAI_API_KEY"] = LITELLM_MASTER_KEY
    print(f"✨ LiteLLM proxy configured for Pydantic AI: {LITELLM_PROXY_URL}")
else:
    print("⚠️  No LITELLM_PROXY_URL set, using direct provider access")

# Model aliases for convenience
# Use openai/ prefix to route through proxy
DEFAULT_FAST_MODEL = "openai/gemini-flash"
DEFAULT_SMART_MODEL = "openai/gemini-pro"
DEFAULT_CODER_MODEL = "openai/glm-flash"
