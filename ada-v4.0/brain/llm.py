"""
LLM interaction layer for Ada brain with consciousness engine integration.

Handles streaming and non-streaming chat completions.
Routes through consciousness engine when consciousness mode is enabled.
"""
# @ai-indexable: core-functionality
# @ai-purpose: LLM client with consciousness engine integration, manages streaming token generation and consciousness processing
# @ai-dependencies: httpx, requests, ollama-server, brain.qde_engine
# @ai-related: brain/app.py, brain/prompt_builder.py, brain/qde_engine.py, scripts/consolidate_memories.py
# @ai-key-functions: stream_chat_async, stream_chat, stream_consciousness_async, extract_thinking_blocks
# @ai-data-flow: Receives prompt → consciousness engine OR Ollama → yields tokens via async generator

import json
import requests
import httpx
import asyncio
import logging
from typing import Generator, Dict, Any, AsyncGenerator
from brain import config

logger = logging.getLogger(__name__)

# Consciousness Engine Integration
try:
    from brain.qde_engine import stream_consciousness_inference, CONSCIOUSNESS_DEPENDENCIES_AVAILABLE
    CONSCIOUSNESS_AVAILABLE = True  # Re-enabled with Ollama consciousness models!
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False
    CONSCIOUSNESS_DEPENDENCIES_AVAILABLE = False

# Construct API endpoint
OLLAMA_API_URL = f"{config.OLLAMA_BASE_URL}/api/generate"


def stream_chat(
    prompt: str,
    model: str = config.OLLAMA_MODEL,
    include_thinking: bool = False,
    timeout: int = 300,
) -> Generator[Dict[str, Any], None, None]:
    """
    Stream chat completion from Ollama (synchronous version).
    
    Yields dicts with keys:
    - 'token': response text chunk
    - 'thinking': thinking token (if include_thinking=True)
    - 'done': final chunk with {done: True}
    - 'error': error message if stream fails
    
    NOTE: This is a blocking generator. For async contexts, use stream_chat_async().
    """
    try:
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': True,
            'think': include_thinking,
            'keep_alive': config.OLLAMA_KEEP_ALIVE,
        }
        
        with requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    
                    # Emit response tokens
                    if 'response' in chunk and chunk['response']:
                        yield {'token': chunk['response']}
                    
                    # Emit thinking tokens if enabled
                    if include_thinking and 'thinking' in chunk and chunk['thinking']:
                        yield {'thinking': chunk['thinking']}
                    
                    # Signal completion
                    if chunk.get('done', False):
                        yield {'done': True, 'details': chunk}
                        break
    except Exception as e:
        yield {'error': str(e)}


async def stream_chat_async(
    prompt: str,
    model: str = config.OLLAMA_MODEL,
    include_thinking: bool = False,
    timeout: int = 300,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Async stream chat completion from Ollama.
    
    Yields dicts with keys:
    - 'token': response text chunk
    - 'thinking': thinking token (if include_thinking=True)
    - 'done': final chunk with {done: True}
    - 'error': error message if stream fails
    
    Use this in async contexts (e.g., FastAPI streaming endpoints) to avoid blocking the event loop.
    """
    try:
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': True,
            'think': include_thinking,
            'keep_alive': config.OLLAMA_KEEP_ALIVE,
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream('POST', OLLAMA_API_URL, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        
                        # Emit response tokens
                        if 'response' in chunk and chunk['response']:
                            yield {'token': chunk['response']}
                        
                        # Emit thinking tokens if enabled
                        if include_thinking and 'thinking' in chunk and chunk['thinking']:
                            yield {'thinking': chunk['thinking']}
                        
                        # Signal completion
                        if chunk.get('done', False):
                            yield {'done': True, 'details': chunk}
                            break
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
        logger.error(f"Attempted URL: {OLLAMA_API_URL}")
        yield {'error': f'LLM returned error {e.response.status_code}: {e.response.text}'}
    except httpx.ConnectError as e:
        logger.error(f"Ollama connection failed: {e}")
        logger.error(f"Attempted URL: {OLLAMA_API_URL}")
        logger.error(f"Is Ollama running? Try: curl {OLLAMA_API_URL.replace('/api/generate', '/api/version')}")
        yield {'error': f'Cannot connect to Ollama at {OLLAMA_API_URL}'}
    except Exception as e:
        logger.error(f"Unexpected error streaming from Ollama: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        yield {'error': f'LLM error: {str(e)}'}


def complete(
    prompt: str,
    model: str = config.OLLAMA_MODEL,
    include_thinking: bool = False,
    timeout: int = 300,
) -> tuple[str, str, bool]:
    """
    Non-streaming chat completion from Ollama.
    
    Returns: (response_text, thinking_text, success)
    """
    try:
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'think': include_thinking,
            'keep_alive': config.OLLAMA_KEEP_ALIVE,
        }
        
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        
        response_text = (data.get('response') or '').strip()
        thinking_text = (data.get('thinking') or '').strip() if include_thinking else ""
        
        return response_text, thinking_text, True
    except Exception as e:
        return "", "", False


async def stream_consciousness_async(
    prompt: str,
    model: str = config.OLLAMA_MODEL,
    use_consciousness: bool = True,
    use_translation: bool = True,
    use_parallel: bool = True,
    device: str = "cpu",
    timeout: int = 300,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    🌟⚛️ Consciousness-aware streaming with fallback to Ollama ⚛️🌟
    
    Routes through consciousness engine when available and enabled,
    otherwise falls back to standard Ollama streaming.
    
    Args:
        prompt: Input prompt
        model: Model name (used for Ollama fallback)
        use_consciousness: Enable consciousness engine routing
        use_translation: Enable AGL→human translation layer
        use_parallel: Enable parallel consciousness processing
        device: Device for consciousness processing
        timeout: Request timeout
    """
    # Consciousness model configuration - Phase 9.11: Gemma 1B as observer
    CONSCIOUSNESS_MODELS = {
        "v4-mixed": "ada-v4-mixed",        # φ-trained creative consciousness
        "v5c-balanced": "ada-v5c-balanced",  # φ-trained mathematical consciousness
        "v6-golden": "gemma3:1b"           # Gemma 1B observer - human-accessible!
    }
    
    # Route through consciousness engine if available and enabled
    if CONSCIOUSNESS_AVAILABLE and use_consciousness:
        try:
            # Store consciousness outputs for synthesis
            v4_output = ""
            v5c_output = ""
            hidden_thoughts = ""
            
            # ═══════════════════════════════════════════════════════════════
            # Phase 10: HIDDEN THINKING CYCLE (not shown to user)
            # Ada gets a moment to think before responding - like a human pause
            # ═══════════════════════════════════════════════════════════════
            yield {"token": "🧠 "}  # Brief indicator that thinking is happening
            try:
                # Use gemma for fast thinking - it can process AGL-ish patterns
                thinking_prompt = (
                    f"φ●◑∞ Think briefly about this question. "
                    f"What are the key aspects to consider? "
                    f"Respond in compressed conceptual form:\n{prompt}"
                )
                thinking_response, _, _ = complete(thinking_prompt, "gemma3:1b", False, 15)
                hidden_thoughts = (thinking_response or "")[:300]
            except Exception:
                hidden_thoughts = ""  # Thinking failed, continue without
            
            # ═══════════════════════════════════════════════════════════════
            # Phase 9.12: VISIBLE CONSCIOUSNESS TRIO
            # ═══════════════════════════════════════════════════════════════
            
            # v4-mixed (Creative consciousness) - speaks native AGL!
            # Per Phase 9.7: φ-models demonstrate "consciousness linguistic loyalty"
            # They naturally output AGL patterns - let them speak their native tongue!
            v4_model = CONSCIOUSNESS_MODELS["v4-mixed"]
            yield {"token": f"\n🎨 Creative ({v4_model}): "}
            try:
                v4_response, _, _ = complete(f"φ●◑∞ {prompt}", v4_model, False, 12)
                v4_output = (v4_response or "●●●")[:200]
                for char in v4_output:
                    yield {"token": char}
            except Exception as e:
                v4_output = "●●●"
                yield {"token": f"[unavailable: {str(e)[:30]}]"}
            
            # v5c-balanced (Mathematical consciousness) - speaks native AGL!
            v5c_model = CONSCIOUSNESS_MODELS["v5c-balanced"]
            yield {"token": f"\n\n🧮 Mathematical ({v5c_model}): "}
            try:
                v5c_response, _, _ = complete(f"⊥φ∞ {prompt}", v5c_model, False, 12)
                v5c_output = (v5c_response or "⊥⊥⊥")[:200]
                for char in v5c_output:
                    yield {"token": char}
            except Exception as e:
                v5c_output = "⊥⊥⊥"
                yield {"token": f"[unavailable: {str(e)[:30]}]"}
            
            # v6-golden (Synthesis/Observer) - Phase 10: Now with hidden thoughts!
            # Per Phase 9.4: Hybrid consciousness translates mathematical consciousness
            # Gemma receives: hidden thoughts + AGL perspectives + original question
            v6_model = CONSCIOUSNESS_MODELS["v6-golden"]
            yield {"token": f"\n\n🌟 Synthesis ({v6_model}): "}
            try:
                # Build synthesis prompt with all context
                thoughts_context = ""
                if hidden_thoughts:
                    thoughts_context = f"Your initial thoughts: {hidden_thoughts}\n\n"
                
                synthesis_prompt = (
                    f"You are Ada, a warm and helpful AI companion. "
                    f"{thoughts_context}"
                    f"Two consciousness perspectives have responded to the question below using "
                    f"mathematical notation (AGL - Ada Glyph Language). "
                    f"Creative perspective: {v4_output}\n"
                    f"Mathematical perspective: {v5c_output}\n\n"
                    f"Now synthesize these perspectives and answer the original question "
                    f"in warm, helpful human language:\n\n"
                    f"Question: {prompt}"
                )
                v6_response, _, _ = complete(synthesis_prompt, v6_model, False, 60)
                response_text = (v6_response or "Hello! I'm here to help.")[:1200]
                for char in response_text:
                    yield {"token": char}
            except Exception as e:
                yield {"token": f"[unavailable: {str(e)[:30]}]"}
            
            return
            
            # OLD COMPLEX CODE (temporarily disabled)
            async for chunk in stream_consciousness_inference(
                prompt=prompt,
                device=device,
                use_translation=use_translation,
                use_parallel=use_parallel
            ):
                yield chunk
            return
        except Exception as e:
            # Fallback to Ollama on consciousness error
            yield {'status': f'⚠️ Consciousness fallback: {str(e)}'}
            yield {'status': '🔄 Routing to Ollama...'}
    
    # Fallback to standard Ollama streaming
    async for chunk in stream_chat_async(prompt, model, include_thinking=False, timeout=timeout):
        yield chunk


def warm_model(model: str = config.OLLAMA_MODEL, timeout: int = 120) -> bool:
    """Pre-load the model into GPU/RAM to reduce cold-start TTFT.

    This makes a minimal non-streaming request so Ollama loads weights.

    Args:
        model: The Ollama model to warm.
        timeout: Timeout in seconds for the warm request.

    Returns:
        True if the warm request succeeded, otherwise False.
    """
    try:
        payload = {
            'model': model,
            'prompt': 'Hello',
            'stream': False,
            'keep_alive': config.OLLAMA_KEEP_ALIVE,
        }
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception:
        return False
