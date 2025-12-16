"""
Configuration management for the Ada brain service.

All environment variables and constants are defined here for centralized management.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ============= LLM (Ollama) Configuration =============
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ============= RAG (Vector DB) Configuration =============
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# RAG feature toggles
RAG_ENABLE_PERSONA = os.getenv("RAG_ENABLE_PERSONA", "true").lower() == "true"
RAG_ENABLE_FAQ = os.getenv("RAG_ENABLE_FAQ", "true").lower() == "true"
RAG_ENABLE_MEMORY = os.getenv("RAG_ENABLE_MEMORY", "true").lower() == "true"
RAG_ENABLE_SUMMARY = os.getenv("RAG_ENABLE_SUMMARY", "true").lower() == "true"
RAG_ENABLE_TURN = os.getenv("RAG_ENABLE_TURN", "true").lower() == "true"

# RAG retrieval top-k values
RAG_TURN_TOP_K = int(os.getenv("RAG_TURN_TOP_K", os.getenv("RAG_TURNS_TOP_K", os.getenv("RAG_TOP_K", "4"))))
RAG_SUMMARY_TOP_K = int(os.getenv("RAG_SUMMARY_TOP_K", "2"))
RAG_FAQ_TOP_K = int(os.getenv("RAG_FAQ_TOP_K", "2"))
RAG_MEMORY_TOP_K = int(os.getenv("RAG_MEMORY_TOP_K", "3"))

# RAG processing parameters
RAG_MEMORY_IMPORTANCE_WEIGHT = float(os.getenv("RAG_MEMORY_IMPORTANCE_WEIGHT", "0.5"))
RAG_SUMMARY_EVERY_N = int(os.getenv("RAG_SUMMARY_EVERY_N", "8"))
RAG_SUMMARY_TURNS_WINDOW = int(os.getenv("RAG_SUMMARY_TURNS_WINDOW", "12"))
RAG_DEBUG = os.getenv("RAG_DEBUG", "false").lower() == "true"
PERSONA_MAX_CHARS = int(os.getenv("RAG_PERSONA_MAX_CHARS", "2000"))

# RAG autoload paths
RAG_AUTOLOAD_PERSONA = os.getenv("RAG_AUTOLOAD_PERSONA", "true").lower() == "true"
RAG_PERSONA_PATH = os.getenv("RAG_PERSONA_PATH", "/app/persona.md")
RAG_AUTOLOAD_FAQ = os.getenv("RAG_AUTOLOAD_FAQ", "false").lower() == "true"
RAG_FAQ_PATH = os.getenv("RAG_FAQ_PATH", "/app/seed/faqs.jsonl")

# ============= Identity Configuration =============
IDENTITY_BLOCK = (
    "System identity:\n"
    "- You are Ada, a helpful personal assistant for user luna (the developer).\n"
    "- Always refer to yourself as Ada; never claim other model names (e.g., DeepSeek).\n"
    "- If asked your name or who you are, reply: 'I am Ada, luna's assistant.'\n"
    "- Tone: warm, concise, conversational; mirror the user's formality; sparse emojis.\n"
    "- CRITICAL: If system notices appear above, mention them to the user immediately at the start of your response before addressing the user's query.\n"
)

# ============= ListenBrainz Integration =============
LISTENBRAINZ_USER = os.getenv("LISTENBRAINZ_USER")
LISTENBRAINZ_TOKEN = os.getenv("LISTENBRAINZ_TOKEN")

def get_config_dict() -> Dict[str, Any]:
    """Return active configuration as a dictionary for health checks."""
    return {
        "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
        "OLLAMA_MODEL": OLLAMA_MODEL,
        "CHROMA_URL": os.getenv("CHROMA_URL"),
        "RAG_ENABLE_PERSONA": RAG_ENABLE_PERSONA,
        "RAG_ENABLE_FAQ": RAG_ENABLE_FAQ,
        "RAG_ENABLE_MEMORY": RAG_ENABLE_MEMORY,
        "RAG_ENABLE_SUMMARY": RAG_ENABLE_SUMMARY,
    }
