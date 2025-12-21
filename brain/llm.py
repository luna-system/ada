"""
LLM (Ollama) interaction layer for Ada brain.

Handles streaming and non-streaming chat completions.
"""
# @ai-indexable: core-functionality
# @ai-purpose: LLM client wrapper for Ollama, manages streaming token generation and thinking mode
# @ai-dependencies: httpx, requests, ollama-server
# @ai-related: brain/app.py, brain/prompt_builder.py, scripts/consolidate_memories.py
# @ai-key-functions: stream_chat_async, stream_chat, extract_thinking_blocks
# @ai-data-flow: Receives prompt → streams to Ollama /api/generate → yields tokens via async generator

import json
import requests
import httpx
from typing import Generator, Dict, Any, AsyncGenerator
from config import OLLAMA_BASE_URL, OLLAMA_KEEP_ALIVE, OLLAMA_MODEL

# Construct API endpoint
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"


def stream_chat(
    prompt: str,
    model: str = OLLAMA_MODEL,
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
            'keep_alive': OLLAMA_KEEP_ALIVE,
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
    model: str = OLLAMA_MODEL,
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
            'keep_alive': OLLAMA_KEEP_ALIVE,
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
    except Exception as e:
        yield {'error': str(e)}


def complete(
    prompt: str,
    model: str = OLLAMA_MODEL,
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
            'keep_alive': OLLAMA_KEEP_ALIVE,
        }
        
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        
        response_text = (data.get('response') or '').strip()
        thinking_text = (data.get('thinking') or '').strip() if include_thinking else ""
        
        return response_text, thinking_text, True
    except Exception as e:
        return "", "", False


def warm_model(model: str = OLLAMA_MODEL, timeout: int = 120) -> bool:
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
            'keep_alive': OLLAMA_KEEP_ALIVE,
        }
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception:
        return False
