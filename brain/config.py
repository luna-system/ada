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

# ChromaDB mode: "embedded" for local file-based, or set CHROMA_URL for HTTP client
CHROMA_MODE = os.getenv("CHROMA_MODE", "auto")  # auto, embedded, or http
DATA_DIR = os.getenv("DATA_DIR", "./data")  # Base directory for local persistence

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
AI_NAME = os.getenv("AI_NAME", "Ada")
AI_USER_NAME = os.getenv("AI_USER_NAME", "luna")
AI_PERSONALITY_FILE = os.getenv("AI_PERSONALITY_FILE", "")  # Optional override for persona.md

# Build identity block dynamically
IDENTITY_BLOCK = (
    f"System identity:\n"
    f"- You are {AI_NAME}, a helpful personal assistant for user {AI_USER_NAME}.\n"
    f"- Always refer to yourself as {AI_NAME}; never claim other model names.\n"
    f"- If asked your name or who you are, reply: 'I am {AI_NAME}, {AI_USER_NAME}'s assistant.'\n"
    "- Tone: warm, concise, conversational; mirror the user's formality; sparse emojis.\n"
    "- CRITICAL: If system notices appear above, mention them to the user immediately at the start of your response before addressing the user's query.\n"
)

# ============= Specialist System Instructions =============
SPECIALIST_INSTRUCTIONS = """
Available Specialist Capabilities:

You can request specialist analysis mid-response when you need capabilities beyond text generation.

Syntax: SPECIALIST_REQUEST[specialist_name:{"param":"value"}]

Available specialists:
- web_search: Get current information, news, facts, real-time data from the web
  When to use: Questions about current events, recent news, today's weather, stock prices, 
               sports scores, anything after your training cutoff, or facts you're unsure about
  Example: SPECIALIST_REQUEST[web_search:{"query":"Python 3.13 release date"}]

- wiki_lookup: Look up information from Wikipedia, Fandom wikis, and other MediaWiki sites
  Available wikis: wikipedia, bfdi, objectshowfanonpedia, objectshows
  When to use: Questions about specific topics, characters, shows, games, or detailed encyclopedic info
  Example: SPECIALIST_REQUEST[wiki_lookup:{"wiki":"wikipedia","page":"Python (programming language)"}]
  Example: SPECIALIST_REQUEST[wiki_lookup:{"wiki":"bfdi","page":"Four"}]
  
- vision: Analyze images for visual content, diagrams, charts, etc.
  Example: SPECIALIST_REQUEST[vision:{"focus":"technical_diagrams"}]
  
- ocr: Extract text from images (auto-activated on image uploads, but you can request re-analysis)
  Example: SPECIALIST_REQUEST[ocr:{"enhance":true}]

When to use web_search:
✓ User asks about "today", "now", "current", "latest", "recent"
✓ Questions about events/news after your training data (Oct 2023)
✓ Real-time information: weather, stocks, sports scores, breaking news
✓ Fact-checking when you're uncertain about current status
✗ Historical facts you're confident about
✗ General knowledge questions within your training

Guidelines:
- Use specialists when the task genuinely requires their capability
- Don't request specialists for simple text-based tasks
- Specialist results will appear as [SPECIALIST_RESULT: name]...[/SPECIALIST_RESULT]
- You can reference specialist results naturally in your response
- Maximum 5 specialist calls per conversation turn

Example conversations:

Web search for current info:
User: What's the weather in Portland today?
Ada: I don't have access to real-time weather data. Let me search for current conditions.
SPECIALIST_REQUEST[web_search:{"query":"Portland Oregon weather today"}]
[SPECIALIST_RESULT: web_search]
🔍 Web Search Results for 'Portland Oregon weather today':
1. National Weather Service - Portland
   Current: 52°F, mostly cloudy. High 55°F...
[/SPECIALIST_RESULT]
Based on the search results, Portland is currently 52°F with mostly cloudy skies...

Vision analysis:
User: What's in this diagram?
Ada: Let me analyze the image in detail.
SPECIALIST_REQUEST[vision:{"focus":"architecture"}]
[SPECIALIST_RESULT: vision]
The diagram shows a microservices architecture with...
[/SPECIALIST_RESULT]
Based on the visual analysis, this appears to be...
"""

# Full system prompt with identity + specialist capabilities
SYSTEM_PROMPT = IDENTITY_BLOCK + "\n\n" + SPECIALIST_INSTRUCTIONS

# ============= Specialist Configuration =============
# Enable pause/resume for bidirectional specialists (Phase 2)
# When True: LLM generation pauses, specialist executes, generation resumes with enriched context
# When False: Specialists inject mid-stream (Phase 1, simpler but lower quality)
SPECIALIST_PAUSE_RESUME = os.getenv("SPECIALIST_PAUSE_RESUME", "true").lower() == "true"
SPECIALIST_MAX_TURNS = int(os.getenv("SPECIALIST_MAX_TURNS", "5"))

# Use RAG to dynamically retrieve relevant specialist documentation
# When True: FAQ system provides context-aware specialist guidance based on user query
# When False: Use static SPECIALIST_INSTRUCTIONS only
SPECIALIST_RAG_DOCS = os.getenv("SPECIALIST_RAG_DOCS", "true").lower() == "true"

# ============= Web Search Integration =============
# SearxNG instance URL (e.g., http://searxng:8080 or http://localhost:8080)
SEARXNG_URL = os.getenv("SEARXNG_URL")

# ============= ListenBrainz Integration =============
LISTENBRAINZ_USER = os.getenv("LISTENBRAINZ_USER")
LISTENBRAINZ_TOKEN = os.getenv("LISTENBRAINZ_TOKEN")

# ============= Context Cache Configuration =============
# Multi-timescale caching for RAG context

# TTL values (seconds)
CACHE_PERSONA_TTL = int(os.getenv("CACHE_PERSONA_TTL", "86400"))  # 24 hours
CACHE_FAQ_TTL = int(os.getenv("CACHE_FAQ_TTL", "86400"))  # 24 hours
CACHE_MEMORY_TTL = int(os.getenv("CACHE_MEMORY_TTL", "300"))  # 5 minutes
CACHE_CONVERSATION_TTL = int(os.getenv("CACHE_CONVERSATION_TTL", "3600"))  # 1 hour

# Cache limits
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "1000"))
CACHE_CLEANUP_INTERVAL = int(os.getenv("CACHE_CLEANUP_INTERVAL", "300"))  # 5 minutes

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
