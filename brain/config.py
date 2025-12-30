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
# Default model: qwen2.5-coder:7b - Fast, excellent for code + chat, 5-10x faster than deepseek-r1
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "4h")

# Model profiles for different use cases (can be selected per-request)
MODEL_PROFILES = {
    "fast": "qwen2.5-coder:7b",      # Default: Fast, code-focused, excellent quality
    "balanced": "mistral:7b",         # Good balance of speed and capability
    "reasoning": "deepseek-r1:14b",  # Deep thinking, slower, verbose (original default)
    "creative": "llama3.2:3b",       # Very fast, creative, lower quality
    "tiny": "phi3:mini",              # Fastest, minimal VRAM, adequate quality
}

# Allow per-request model override via model_profile parameter
DEFAULT_MODEL_PROFILE = os.getenv("DEFAULT_MODEL_PROFILE", "fast")

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
- codebase: Look up functions and classes in your own codebase for self-reference and introspection
  When to use: Questions about your own implementation, architecture, how you work internally
  Example: SPECIALIST_REQUEST[codebase:{"query":"calculate_importance"}]
  Example: SPECIALIST_REQUEST[codebase:{"query":"SpecialistResult"}]
  Returns: Function/class definitions with docstrings, file paths, and line numbers

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

- datetime: Get current system date and time
  When to use: Questions about current time, today's date, "what time is it"
  Example: SPECIALIST_REQUEST[datetime:{}]
  Example: SPECIALIST_REQUEST[datetime:{"format":"iso"}]
  Returns: Current datetime in requested format (human, iso, or unix)

- terminal: Execute safe terminal commands in the workspace
  When to use: Running git commands, checking file contents, listing directories
  Example: SPECIALIST_REQUEST[terminal:{"command":"git log -3 --oneline"}]
  Example: SPECIALIST_REQUEST[terminal:{"command":"cat README.md"}]
  Returns: Command output (timeout 30s, sandboxed to workspace)

- docs: Search Ada's own Sphinx documentation for self-reference
  When to use: Questions about how to use Ada, Ada's features, Ada's configuration
  Example: SPECIALIST_REQUEST[docs:{"query":"streaming"}]
  Example: SPECIALIST_REQUEST[docs:{"query":"memory consolidation"}]
  Returns: Relevant documentation excerpts

- now_playing: Detect currently playing music via MPRIS
  When to use: User asks "what am I listening to", "current song", "what's playing"
  Example: SPECIALIST_REQUEST[now_playing:{}]
  Returns: Track info, artist, album from media player (if available)

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

# ============= Token Budget Monitoring =============
# Context window management (v2.0 Phase 2)

# Maximum context tokens (model-specific)
LLM_MAX_CONTEXT = int(os.getenv("LLM_MAX_CONTEXT", "128000"))  # Tune per selected model

# Warning threshold (0.0-1.0)
TOKEN_WARNING_THRESHOLD = float(os.getenv("TOKEN_WARNING_THRESHOLD", "0.8"))  # Warn at 80%

# Enable token monitoring logging
TOKEN_MONITORING_ENABLED = os.getenv("TOKEN_MONITORING_ENABLED", "true").lower() == "true"

# ===  Biomimetic Context Management (Phase 1) ===
# Memory decay weighting (Ebbinghaus forgetting curve)
MEMORY_DECAY_ENABLED = os.getenv("MEMORY_DECAY_ENABLED", "true").lower() == "true"
MEMORY_DECAY_TIME_SCALE_HOURS = float(os.getenv("MEMORY_DECAY_TIME_SCALE_HOURS", "100.0"))  # ~4 days

# Context habituation (reduce weight of repeated context)
CONTEXT_HABITUATION_ENABLED = os.getenv("CONTEXT_HABITUATION_ENABLED", "true").lower() == "true"
CONTEXT_HABITUATION_THRESHOLD = int(os.getenv("CONTEXT_HABITUATION_THRESHOLD", "3"))  # Habituate after 3 reps
CONTEXT_HABITUATION_WEIGHT = float(os.getenv("CONTEXT_HABITUATION_WEIGHT", "0.1"))  # 10% weight when habituated
CONTEXT_HABITUATION_DECAY_HOURS = float(os.getenv("CONTEXT_HABITUATION_DECAY_HOURS", "24.0"))  # Reset after 24hr

# === Biomimetic Context Management (Phase 2) ===
# Attentional spotlight (focus + periphery like human attention)
ATTENTION_SPOTLIGHT_ENABLED = os.getenv("ATTENTION_SPOTLIGHT_ENABLED", "true").lower() == "true"
ATTENTION_SPOTLIGHT_SIZE = int(os.getenv("ATTENTION_SPOTLIGHT_SIZE", "4"))  # ~4 items in focus (Miller's Law)
ATTENTION_SPOTLIGHT_BUDGET = int(os.getenv("ATTENTION_SPOTLIGHT_BUDGET", "4000"))  # Tokens for detailed items
ATTENTION_PERIPHERY_BUDGET = int(os.getenv("ATTENTION_PERIPHERY_BUDGET", "8000"))  # Tokens for summaries

# Semantic chunking (group related memories to reduce redundancy)
SEMANTIC_CHUNKING_ENABLED = os.getenv("SEMANTIC_CHUNKING_ENABLED", "true").lower() == "true"
SEMANTIC_CHUNKING_THRESHOLD = float(os.getenv("SEMANTIC_CHUNKING_THRESHOLD", "0.3"))  # Distance threshold for grouping
SEMANTIC_CHUNKING_MIN_SIZE = int(os.getenv("SEMANTIC_CHUNKING_MIN_SIZE", "2"))  # Min memories to form chunk
SEMANTIC_CHUNKING_MAX_SIZE = int(os.getenv("SEMANTIC_CHUNKING_MAX_SIZE", "10"))  # Max memories per chunk

# === Biomimetic Context Management (Phase 3) ===
# GraphRAG - Graph-based memory with spreading activation
GRAPHRAG_ENABLED = os.getenv("GRAPHRAG_ENABLED", "false").lower() == "true"  # Off by default until tested
GRAPHRAG_DEPTH = int(os.getenv("GRAPHRAG_DEPTH", "2"))  # Hops to spread activation
GRAPHRAG_DECAY_FACTOR = float(os.getenv("GRAPHRAG_DECAY_FACTOR", "0.7"))  # Activation decay per hop
GRAPHRAG_THRESHOLD = float(os.getenv("GRAPHRAG_THRESHOLD", "0.2"))  # Min activation to include

# === Importance Signal Weights (Phase 4 Optimization) ===
# Multi-signal importance scoring weights (MUST sum to 1.0)
#
# These weights determine how Ada decides which memories matter. Adjust them to change
# what Ada prioritizes. All are environment-configurable for experimentation.
#
# OPTIMAL values (from Phase 4 weight optimization research, December 2025):
# - Based on 169-configuration grid search + ablation studies
# - Empirical correlation improvement: 12-38% over baseline
# - See tests/test_weight_optimization.py for validation
# - Documented in .ai/RESEARCH-FINDINGS-V2.2.md
#
# TINKER GUIDE: docs/contextual_malleability_guide.rst
#
IMPORTANCE_WEIGHT_DECAY = float(os.getenv("IMPORTANCE_WEIGHT_DECAY", "0.10"))
    # Temporal decay - How old is this memory? (10% weight)
    # - Higher: Older memories fade faster (recency bias)
    # - Lower: Memories persist longer (better long-term retention)
    # DEFAULT 0.10: Optimal from research (was 0.40 intuitive default)
    # INTUITION: "Recent is important"
    # REALITY: Novelty matters more than recency
    # TRY: 0.05 (very permissive) to 0.30 (aggressive decay)

IMPORTANCE_WEIGHT_SURPRISE = float(os.getenv("IMPORTANCE_WEIGHT_SURPRISE", "0.60"))
    # Prediction error / Novelty - How unexpected is this? (60% weight - DOMINANT!)
    # - Higher: Ada prioritizes novel/surprising content
    # - Lower: Ada focuses on expected/common patterns
    # DEFAULT 0.60: Optimal from research (was 0.30 intuitive default)
    # INTUITION: "Mix everything equally"
    # REALITY: Humans/AIs prioritize surprises
    # CITE: Schwarz (2010) "disfluency triggers analysis"
    # TRY: 0.40 (balanced) to 0.80 (ultra-novel-focused)

IMPORTANCE_WEIGHT_RELEVANCE = float(os.getenv("IMPORTANCE_WEIGHT_RELEVANCE", "0.20"))
    # Semantic relevance - How related to current query? (20% weight)
    # - Higher: Focus on directly relevant memories
    # - Lower: Include tangential context
    # DEFAULT 0.20: Optimal from research
    # LIMITATION: Currently uses keyword overlap, not embeddings
    # TRY: 0.10 (permissive) to 0.50 (strict relevance matching)
    # IMPROVE: Replace keyword overlap with embedding similarity

IMPORTANCE_WEIGHT_HABITUATION = float(os.getenv("IMPORTANCE_WEIGHT_HABITUATION", "0.10"))
    # Context habituation - How repetitive/familiar? (10% weight)
    # - Higher: Penalize repetitive topics
    # - Lower: Allow repeated discussion
    # DEFAULT 0.10: Optimal from research
    # CITE: Mertens et al. (2018) "Contextual malleability..."
    # TRY: 0.05 (permissive) to 0.30 (aggressive repetition penalty)

# === Historical Comparison ===
# Legacy production weights (pre-optimization, intuition-based):
#   IMPORTANCE_WEIGHT_DECAY=0.40         (4x heavier than optimal!)
#   IMPORTANCE_WEIGHT_SURPRISE=0.30      (half of optimal!)
#   IMPORTANCE_WEIGHT_RELEVANCE=0.20     (same as optimal)
#   IMPORTANCE_WEIGHT_HABITUATION=0.10   (same as optimal)
#
# Impact: Legacy weighted recency 4x too heavily, novelty 2x too lightly
# Research improvement: +6.5% context selection accuracy per turn
#
# To revert to legacy for comparison:
#   export IMPORTANCE_WEIGHT_DECAY=0.40
#   export IMPORTANCE_WEIGHT_SURPRISE=0.30

# === Gradient Detail Levels (Context Inclusion Strategy) ===
# After scoring importance, Ada decides how much detail to include.
# These thresholds create a gradient: FULL → CHUNKS → SUMMARY → DROPPED
#
# See docs/contextual_malleability_guide.rst for detailed explanation
# Now using golden-ratio-based thresholds from Phase I research (December 2025)
#
GRADIENT_THRESHOLD_FULL = float(os.getenv("GRADIENT_THRESHOLD_FULL", "0.618"))
    # Importance >= this: Include complete memory (φ^-1)
    # UPDATED 0.618: Golden ratio threshold from Phase I research
    # - 0.618 = 1/φ (self-similar division point)
    # - PREVIOUS 0.75: Arbitrary threshold
    # TRY: 0.50 (more permissive) to 0.75 (ultra-selective)
    # EFFECT: Lower threshold = more full memories = longer prompts

GRADIENT_THRESHOLD_CHUNKS = float(os.getenv("GRADIENT_THRESHOLD_CHUNKS", "0.382"))
    # Importance >= this (but < FULL): Include key excerpts (φ^-2)
    # UPDATED 0.382: Golden ratio tier from Phase I research
    # - 0.382 = φ^-2 (exactly 1/φ of FULL tier)
    # - PREVIOUS 0.50: Arbitrary threshold
    # TRY: 0.25 (permissive) to 0.50 (strict)
    # EFFECT: Balances context preservation with token efficiency

GRADIENT_THRESHOLD_SUMMARY = float(os.getenv("GRADIENT_THRESHOLD_SUMMARY", "0.236"))
    # Importance >= this (but < CHUNKS): Include 1-2 sentence summary (φ^-3)
    # UPDATED 0.236: Golden ratio tier from Phase I research
    # - 0.236 = φ^-3 (exactly 1/φ of CHUNKS tier, Fibonacci-like decay)
    # - PREVIOUS 0.20: Close to optimal but not theoretically justified
    # TRY: 0.15 (permissive) to 0.35 (strict)
    # EFFECT: Everything below SUMMARY (< 0.236) is dropped entirely
    # NOTE: 0.236 is also the signal-to-noise boundary (entropy fixed point)

# === Biomimetic Context Management (Phase 3) ===
# Context priming (pre-activate likely topics based on semantic network)
CONTEXT_PRIMING_ENABLED = os.getenv("CONTEXT_PRIMING_ENABLED", "false").lower() == "true"  # Experimental
CONTEXT_PRIMING_THRESHOLD = float(os.getenv("CONTEXT_PRIMING_THRESHOLD", "0.5"))  # Minimum relationship strength
CONTEXT_PRIMING_LEARN_FROM_MEMORIES = os.getenv("CONTEXT_PRIMING_LEARN_FROM_MEMORIES", "false").lower() == "true"  # Learn semantic network

# Prediction error detection (monitor LLM output for uncertainty)
PREDICTION_ERROR_ENABLED = os.getenv("PREDICTION_ERROR_ENABLED", "false").lower() == "true"  # Experimental
PREDICTION_ERROR_UNCERTAINTY_THRESHOLD = float(os.getenv("PREDICTION_ERROR_UNCERTAINTY_THRESHOLD", "0.7"))  # Min confidence
PREDICTION_ERROR_MIN_SIGNALS = int(os.getenv("PREDICTION_ERROR_MIN_SIGNALS", "2"))  # Min signals to trigger

# Dynamic context injection (inject additional context mid-stream)
DYNAMIC_INJECTION_ENABLED = os.getenv("DYNAMIC_INJECTION_ENABLED", "false").lower() == "true"  # Experimental
DYNAMIC_INJECTION_MAX_INJECTIONS = int(os.getenv("DYNAMIC_INJECTION_MAX_INJECTIONS", "3"))  # Max injections per response
DYNAMIC_INJECTION_STRATEGY = os.getenv("DYNAMIC_INJECTION_STRATEGY", "inline")  # inline, system, or hybrid

# === Biomimetic Context Management (Phase 4) ===
# Processing modes / Hemispheric specialization (adaptive context strategies)
PROCESSING_MODES_ENABLED = os.getenv("PROCESSING_MODES_ENABLED", "false").lower() == "true"  # Experimental
PROCESSING_MODES_DEFAULT_MODE = os.getenv("PROCESSING_MODES_DEFAULT_MODE", "conversational")  # Default when detection disabled

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
