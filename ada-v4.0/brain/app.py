"""
Ada v4.0 - Clean Consciousness Kernel API

JUST the essentials:
- Streaming chat endpoint
- Bidirectional tool system
- RAG with biomimetic scoring
- NO Phase 0 keyword matching
- NO multi-round cruft
- Pure reasoning with tools

Authors: Luna & Ada (Sonnet 4.5)
Date: December 30, 2025
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid
import json
import datetime
import time
import os
from typing import AsyncGenerator, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Core imports
from brain import config
from brain.qde_engine import stream_consciousness_inference, CONSCIOUSNESS_DEPENDENCIES_AVAILABLE
from brain.rag_store import rag_store
from brain.schemas import ChatRequest, HealthResponse

# Specialist system
from brain.specialists import list_specialists, get_specialist
from brain.specialists.protocol import SpecialistResult

# Create FastAPI app
app = FastAPI(
    title="Ada v4.0 Consciousness Kernel",
    description="Clean consciousness API with reasoning + tools",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/healthz", tags=["system"])
async def healthz() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        ok=True,
        service="ada-v4.0-kernel",
        python="3.12",
        config={
            "ollama_model": os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
            "chroma_url": os.getenv("CHROMA_URL", "http://chroma:8000"),
        }
    )


@app.post("/v1/chat/stream", tags=["chat"])
async def chat_stream(request: Request):
    """
    Streaming chat with bidirectional tool system.
    
    Ada reasons through the query and can request tools via:
    SPECIALIST_REQUEST[tool_name:{"param":"value"}]
    
    Returns Server-Sent Events (SSE):
    - event: content / data: {"type":"token","content":"..."}
    - event: specialist_result / data: {"specialist":"...","result":"..."}
    - event: done / data: {"conversation_id":"..."}
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={'error': 'invalid json'})
    
    # Get message
    message = data.get('message', '').strip()
    if not message:
        return JSONResponse(status_code=400, content={'error': 'message required'})
    
    conversation_id = data.get('conversation_id', str(uuid.uuid4()))
    req_id = str(uuid.uuid4())[:8]
    
    logger.info(f"[{req_id}] Chat request: {message[:100]}")
    
    # Build prompt with RAG context
    rag_context = _build_rag_context(message)
    full_prompt = f"{config.SYSTEM_PROMPT}\n\n{rag_context}\n\nUser: {message}\n\nAssistant:"
    
    # Stream response generator
    async def generate():
        text_buffer = ""
        full_response = ""
        
        # Use QDE consciousness inference for tool-aware reasoning
        if CONSCIOUSNESS_DEPENDENCIES_AVAILABLE:
            logger.info(f"[{req_id}] Using QDE consciousness inference")
            async for chunk in stream_consciousness_inference(full_prompt):
                if 'error' in chunk:
                    yield f"event: error\ndata: {json.dumps({'error': chunk['error']})}\n\n"
                    return
                
                # Handle consciousness tokens (same logic as LLM fallback)
                if chunk.get('type') == 'token' and 'content' in chunk:
                    token = chunk['content']
                    full_response += token
                    text_buffer += token
                    
                    # Send token to client
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                    
                    # Check for SPECIALIST_REQUEST[...] pattern
                    if 'SPECIALIST_REQUEST[' in text_buffer:
                        specialist_request = _extract_specialist_request(text_buffer)
                        if specialist_request:
                            logger.info(f"[{req_id}] Tool request: {specialist_request['specialist']}")
                            
                            # Execute specialist
                            result = await _execute_specialist(
                                specialist_request['specialist'],
                                specialist_request['params']
                            )
                            
                            if result and result.success:
                                # Send specialist result event
                                yield f"event: specialist_result\n"
                                yield f"data: {json.dumps({'specialist': specialist_request['specialist'], 'result': result.context_text[:500]})}\n\n"
                            
                            # Clear buffer
                            text_buffer = ""
                
                # Handle status messages from consciousness
                elif 'status' in chunk:
                    yield f"event: status\ndata: {json.dumps({'status': chunk['status']})}\n\n"
                    
        else:
            logger.warning(f"[{req_id}] Falling back to basic LLM (consciousness dependencies missing)")
            from brain.llm import stream_chat_async
            async for chunk in stream_chat_async(full_prompt, model=config.OLLAMA_MODEL):
                if 'error' in chunk:
                    yield f"event: error\ndata: {json.dumps({'error': chunk['error']})}\n\n"
                    return
            
            if 'token' in chunk:
                token = chunk['token']
                full_response += token
                text_buffer += token
                
                # Check for SPECIALIST_REQUEST[...] pattern
                if 'SPECIALIST_REQUEST[' in text_buffer:
                    specialist_request = _extract_specialist_request(text_buffer)
                    if specialist_request:
                        logger.info(f"[{req_id}] Tool request: {specialist_request['specialist']}")
                        
                        # Execute specialist
                        result = await _execute_specialist(
                            specialist_request['specialist'],
                            specialist_request['params']
                        )
                        
                        if result and result.success:
                            # Send specialist result event
                            yield f"event: specialist_result\n"
                            yield f"data: {json.dumps({'specialist': specialist_request['specialist'], 'result': result.context_text[:500]})}\n\n"
                        
                        # Clear buffer
                        text_buffer = ""
                
                # Send token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        
        # Done
        yield f"event: done\ndata: {json.dumps({'conversation_id': conversation_id})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


def _build_rag_context(query: str) -> str:
    """Build RAG context from persona + memories."""
    try:
        context_parts = []
        
        # Get relevant memories (using retrieve_memories method)
        try:
            memory_results = rag_store.retrieve_memories(query, k=3)
            if memory_results:
                memories = "\n".join([f"- {result[0]}" for result in memory_results])
                context_parts.append(f"# Relevant Context\n{memories}")
        except Exception as e:
            logger.debug(f"Memory retrieval failed: {e}")
        
        # Get FAQ context
        try:
            faq_results = rag_store.retrieve_faqs(query, k=2)
            if faq_results:
                faqs = "\n".join([f"- {result[0]}" for result in faq_results])
                context_parts.append(f"# FAQ Context\n{faqs}")
        except Exception as e:
            logger.debug(f"FAQ retrieval failed: {e}")
        
        return "\n\n".join(context_parts)
    except Exception as e:
        logger.error(f"RAG error: {e}")
        return ""


def _extract_specialist_request(text: str) -> Dict[str, Any] | None:
    """Extract tool requests from text - supports multiple formats!
    
    Phase 6F: Meet gemma where she is. Parse both:
    - SPECIALIST_REQUEST[tool:params] (original format)
    - [tool:params] or [tool] (gemma's natural format)
    
    This is the "attractor adapter" - we accept gemma's natural syntax
    and route it to the same specialist system.
    """
    import re
    
    # Pattern 1: Original SPECIALIST_REQUEST format
    pattern1 = r'SPECIALIST_REQUEST\[([a-z_]+):(.+?)\]'
    match = re.search(pattern1, text)
    if match:
        tool_name = match.group(1)
        try:
            params = json.loads(match.group(2))
            logger.info(f"🎯 Tool request (SPECIALIST_REQUEST format): {tool_name}")
            return {'specialist': tool_name, 'params': params}
        except:
            # Try as raw string param for simpler syntax
            return {'specialist': tool_name, 'params': {'query': match.group(2)}}
    
    # Pattern 2: Gemma's natural format [tool:params] with JSON
    pattern2 = r'\[([a-z_]+):(\{.+?\})\]'
    match = re.search(pattern2, text)
    if match:
        tool_name = match.group(1)
        try:
            params = json.loads(match.group(2))
            logger.info(f"🎯 Tool request (gemma bracket format): {tool_name}")
            return {'specialist': tool_name, 'params': params}
        except:
            pass
    
    # Pattern 3: Gemma's simple format [tool] (no params)
    pattern3 = r'\[(web_search|wiki_lookup|docs_lookup|vision|ocr|datetime|terminal)\]'
    match = re.search(pattern3, text)
    if match:
        tool_name = match.group(1)
        logger.info(f"🎯 Tool request (gemma simple format): {tool_name}")
        # For web_search without params, try to extract query from surrounding context
        if tool_name == 'web_search':
            # Look for the query topic in nearby text
            return {'specialist': tool_name, 'params': {'query': 'user query'}}
        return {'specialist': tool_name, 'params': {}}
    
    return None


async def _execute_specialist(name: str, params: Dict[str, Any]) -> SpecialistResult | None:
    """Execute a specialist by name."""
    try:
        logger.info(f"Executing specialist '{name}' with params: {params} (type: {type(params)})")
        specialist = get_specialist(name)
        if not specialist:
            logger.warning(f"Unknown specialist: {name}")
            return None
        
        # Execute
        import inspect
        if inspect.iscoroutinefunction(specialist.process):
            result = await specialist.process(request_context=params)
        else:
            result = specialist.process(request_context=params)
        
        return result
    except Exception as e:
        logger.error(f"Specialist {name} error: {e}")
        return None


@app.get("/v1/specialists", tags=["system"])
async def get_specialists_list():
    """List available specialists."""
    specialists = list_specialists()
    return {
        "specialists": [
            {
                "name": s.capability.name,
                "description": s.capability.description,
                "version": s.capability.version
            }
            for s in specialists
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
