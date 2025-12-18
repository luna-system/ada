"""
Ada Brain Service: REST API for LLM orchestration with RAG.

Pure FastAPI backend service that handles:
- Chat streaming with Server-Sent Events (SSE)
- Memory management (long-term storage)
- RAG context assembly (persona, FAQ, memories, conversation turns)
- Health checking and debugging

The frontend (Nginx) proxies /api/* requests to /v1/* endpoints here.
External tools can also hit the API directly at http://brain:7000/v1/*
"""
# @ai-indexable: entrypoint
# @ai-purpose: FastAPI REST API for LLM orchestration, chat streaming, and memory management
# @ai-dependencies: fastapi, uvicorn, brain.llm, brain.prompt_builder, brain.rag_store, brain.schemas
# @ai-related: brain/llm.py, brain/prompt_builder.py, brain/rag_store.py, brain/wsgi.py
# @ai-key-functions: chat_stream_v1, list_specialists, get_schema, get_info, healthz
# @ai-endpoints: POST /v1/chat/stream, GET /v1/specialists, GET /v1/schema, GET /v1/info, GET /v1/healthz
# @ai-data-flow: HTTP request → route handler → prompt building → LLM streaming → SSE response

import os
import datetime
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

# System notice manager
from brain.notices import notice_manager
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

from fastapi import APIRouter

# --- System Notice API Models ---
class NoticeIn(BaseModel):
    severity: str
    component: str
    code: str
    message: str

class AckIn(BaseModel):
    ack_by: str = "system"

# Router so endpoints can be registered after app creation
router = APIRouter()

@router.get('/v1/notices')
async def list_notices(active: bool = True):
    """List active (default) or all system notices."""
    return notice_manager.list_notices(active_only=active)

@router.post('/v1/notices')
async def add_notice(notice: NoticeIn):
    """Add a new system notice (deduplicated by component/code/message)."""
    nid = notice_manager.add_notice(
        severity=notice.severity,
        component=notice.component,
        code=notice.code,
        message=notice.message,
    )
    return {"id": nid}

@router.post('/v1/notices/{notice_id}/ack')
async def ack_notice(notice_id: str, ack: AckIn):
    """Acknowledge a notice by id."""
    ok = notice_manager.acknowledge(notice_id, ack_by=ack.ack_by)
    return {"ok": ok}

@router.post('/v1/notices/{notice_id}/clear')
async def clear_notice(notice_id: str):
    """Remove a notice immediately."""
    ok = notice_manager.clear_notice(notice_id)
    return {"ok": ok}

# --- OCR API ---
from fastapi import UploadFile, File, HTTPException
from brain.ocr import get_ocr_processor

@router.post('/v1/ocr/extract')
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extract text from uploaded image using OCR.
    
    Returns extracted text and metadata.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read file bytes
        image_bytes = await file.read()
        
        # Process with OCR
        ocr_processor = get_ocr_processor()
        result = ocr_processor.extract_text(image_bytes)
        
        # Add filename to result
        result['filename'] = file.filename
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

import requests

# Ensure brain module is in path for Docker container
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modular components
import config
from rag_store import RagStore
from llm import stream_chat_async, complete
from media import fetch_listenbrainz, format_media_for_prompt
from brain.prompt_builder import PromptAssembler
from brain.notices_client import get_active_notices

# Ollama + models
OLLAMA_API_URL = config.OLLAMA_API_URL
OLLAMA_MODEL = config.OLLAMA_MODEL
OLLAMA_BASE_URL = config.OLLAMA_BASE_URL

# RAG configuration
RAG_ENABLED = config.RAG_ENABLED
EMBED_MODEL = config.EMBED_MODEL

# Section toggles
RAG_ENABLE_PERSONA = config.RAG_ENABLE_PERSONA
RAG_ENABLE_FAQ = config.RAG_ENABLE_FAQ
RAG_ENABLE_MEMORY = config.RAG_ENABLE_MEMORY
RAG_ENABLE_SUMMARY = config.RAG_ENABLE_SUMMARY
RAG_ENABLE_TURN = config.RAG_ENABLE_TURN
RAG_TURN_TOP_K = config.RAG_TURN_TOP_K
RAG_SUMMARY_TOP_K = config.RAG_SUMMARY_TOP_K
RAG_FAQ_TOP_K = config.RAG_FAQ_TOP_K
RAG_MEMORY_TOP_K = config.RAG_MEMORY_TOP_K
RAG_MEMORY_IMPORTANCE_WEIGHT = config.RAG_MEMORY_IMPORTANCE_WEIGHT
RAG_SUMMARY_EVERY_N = config.RAG_SUMMARY_EVERY_N
RAG_SUMMARY_TURNS_WINDOW = config.RAG_SUMMARY_TURNS_WINDOW
RAG_DEBUG = config.RAG_DEBUG
PERSONA_MAX_CHARS = config.PERSONA_MAX_CHARS

# System identity block
IDENTITY_BLOCK = config.IDENTITY_BLOCK

# ListenBrainz
LISTENBRAINZ_USER = config.LISTENBRAINZ_USER
LISTENBRAINZ_TOKEN = config.LISTENBRAINZ_TOKEN

# Global RAG store instance
rag_store = None

def _init_rag_store():
    """Initialize RAG store and load seed data."""
    global rag_store
    if not RAG_ENABLED:
        return
    
    try:
        rag_store = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=OLLAMA_BASE_URL,
            embed_model=EMBED_MODEL,
        )
        _autoload_seed()
    except Exception as e:
        print(f"[BRAIN][RAG] Init failed: {e}")
        rag_store = None
def _autoload_seed():
    """Autoload persona and FAQ seed data into RAG store."""
    if rag_store is None:
        return
    try:
        # Persona
        if config.RAG_AUTOLOAD_PERSONA:
            persona_path = config.RAG_PERSONA_PATH
            p = Path(persona_path)
            if p.exists() and p.is_file():
                try:
                    text = p.read_text(encoding="utf-8").strip()
                    if text:
                        # Ensure idempotency: remove previous persona docs, then insert fresh copy
                        try:
                            rag_store.col.delete(where={"type": "persona"})
                        except Exception:
                            pass
                        mtime = datetime.datetime.utcfromtimestamp(p.stat().st_mtime).isoformat() + "Z"
                        rag_store.upsert_doc(
                            text,
                            type="persona",
                            scope="global",
                            version=mtime,
                            source="kb",
                        )
                        print(f"[BRAIN][RAG] Autoloaded persona from {persona_path}")
                except Exception as perr:
                    print(f"[BRAIN][RAG] Persona autoload failed: {perr}")
        
        # FAQs
        if config.RAG_AUTOLOAD_FAQ:
            faq_path = config.RAG_FAQ_PATH
            fpath = Path(faq_path)
            if fpath.exists() and fpath.is_file():
                count = 0
                try:
                    if fpath.suffix.lower() == ".jsonl":
                        with fpath.open("r", encoding="utf-8") as fh:
                            for line in fh:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    obj = json.loads(line)
                                except Exception:
                                    continue
                                q = (obj.get("question") or "").strip()
                                a = (obj.get("answer") or "").strip()
                                topic = (obj.get("topic") or None)
                                if q and a:
                                    text = f"Q: {q}\nA: {a}"
                                    rag_store.upsert_doc(text, type="faq", scope="global", topic=topic, source="kb")
                                    count += 1
                    elif fpath.suffix.lower() == ".csv":
                        with fpath.open("r", encoding="utf-8") as fh:
                            reader = csv.DictReader(fh)
                            for row in reader:
                                q = (row.get("question") or "").strip()
                                a = (row.get("answer") or "").strip()
                                topic = (row.get("topic") or None)
                                if q and a:
                                    text = f"Q: {q}\nA: {a}"
                                    rag_store.upsert_doc(text, type="faq", scope="global", topic=topic, source="kb")
                                    count += 1
                    else:
                        print(f"[BRAIN][RAG] FAQ autoload skipped: unsupported extension for {faq_path}")
                    if count:
                        print(f"[BRAIN][RAG] Autoloaded {count} FAQ entries from {faq_path}")
                except Exception as ferr:
                    print(f"[BRAIN][RAG] FAQ autoload failed: {ferr}")
    except Exception as err:
        print(f"[BRAIN][RAG] Autoload seed unexpected error: {err}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - init RAG store on startup."""
    # Startup
    from brain.startup_quotes import get_startup_quote, format_startup_banner
    
    quote = get_startup_quote()
    banner = format_startup_banner(quote)
    print(banner)
    print("[BRAIN] Server is ready. Spawning workers")
    _init_rag_store()
    yield
    # Shutdown
    print("[BRAIN] Server shutting down")

app = FastAPI(
    lifespan=lifespan,
    title="Ada Brain API",
    description="""
    Ada Brain Service - LLM orchestration with RAG and specialist capabilities.
    
    ## Features
    
    - **Streaming Chat**: Real-time responses via Server-Sent Events
    - **RAG Context**: Persona, FAQ, memories, and conversation history
    - **Specialist System**: Pluggable capabilities (web search, OCR, vision, media)
    - **Memory Management**: Long-term context storage with importance ranking
    - **Self-Documenting**: Introspectable schemas, specialists, and system info
    
    ## Key Endpoints
    
    - `/v1/chat` - Streaming chat with RAG context
    - `/v1/schema` - Data model schemas (Pydantic/JSON Schema)
    - `/v1/specialists` - Available specialist capabilities
    - `/v1/info` - System information and features
    - `/v1/memory` - Memory management
    - `/v1/healthz` - Health check and diagnostics
    
    ## Documentation
    
    Full documentation available at `/docs/index.html`
    """,
    version="1.0.0",
    contact={
        "name": "Ada Project",
        "url": "https://github.com/your-repo/ada-v1",
    },
    license_info={
        "name": "CC0 1.0 Universal (Public Domain)",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    openapi_tags=[
        {
            "name": "chat",
            "description": "Chat and streaming endpoints",
        },
        {
            "name": "introspection",
            "description": "Self-documenting endpoints (schema, specialists, info)",
        },
        {
            "name": "memory",
            "description": "Long-term memory management",
        },
        {
            "name": "health",
            "description": "Health checks and diagnostics",
        },
        {
            "name": "debug",
            "description": "Debug and inspection tools",
        },
    ],
)

# Include system notice router
app.include_router(router)



@app.get('/v1/schema', tags=['introspection'])
async def get_schemas(doc_type: Optional[str] = Query(None, description="Specific document type (persona, faq, memory, turn, summary)")):
    """
    Get JSON Schema definitions for Chroma document metadata.
    
    Returns JSON Schema for all document types or a specific type.
    Use this endpoint to understand the structure of documents in the vector database.
    
    **Query Parameters:**
        - doc_type (optional): Specific document type to retrieve schema for
    
    **Response (200 OK):**
        JSON Schema definition(s) for document metadata
    
    **Example Requests:**
        - GET /v1/schema - All schemas
        - GET /v1/schema?doc_type=memory - Memory schema only
    """
    from brain.schemas import get_all_schemas, get_schema_by_type, get_metadata_fields_by_type, get_required_fields_by_type
    
    try:
        if doc_type:
            schema = get_schema_by_type(doc_type)
            return {
                "document_type": doc_type,
                "schema": schema,
                "fields": get_metadata_fields_by_type()[doc_type],
                "required_fields": get_required_fields_by_type()[doc_type]
            }
        else:
            return {
                "schemas": get_all_schemas(),
                "document_types": ["persona", "faq", "memory", "turn", "summary"],
                "fields_by_type": get_metadata_fields_by_type(),
                "required_fields_by_type": get_required_fields_by_type()
            }
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get('/v1/specialists', tags=['introspection'])
async def get_specialists():
    """
    List all available specialist capabilities.
    
    Returns information about registered specialists including their names,
    descriptions, parameters, priorities, and enabled status. This endpoint
    makes the specialist system self-documenting.
    
    **Response (200 OK):**
        JSON array of specialist capability objects
    
    **Example Response:**
        .. code-block:: json
        
            {
              "specialists": [
                {
                  "name": "web_search",
                  "description": "Search the web for current information",
                  "icon": "🔍",
                  "version": "1.0.0",
                  "priority": "medium",
                  "enabled": true,
                  "tags": ["search", "web", "information"],
                  "input_schema": {
                    "type": "object",
                    "properties": {
                      "query": {"type": "string"}
                    },
                    "required": ["query"]
                  },
                  "output_schema": {}
                }
              ],
              "count": 3
            }
    """
    from brain.specialists import list_specialists
    
    specialists = list_specialists()
    
    return {
        "specialists": [
            {
                "name": spec.capability.name,
                "description": spec.capability.description,
                "icon": spec.capability.context_icon,
                "version": spec.capability.version,
                "priority": spec.capability.context_priority.name.lower(),
                "enabled": spec.capability.enabled,
                "tags": spec.capability.tags,
                "input_schema": spec.capability.input_schema,
                "output_schema": spec.capability.output_schema,
            }
            for spec in specialists
        ],
        "count": len(specialists)
    }


@app.get('/v1/info', tags=['introspection'])
async def get_system_info():
    """
    Get system information and capabilities.
    
    Returns version information, feature flags, active configuration,
    and available capabilities. Makes the system self-describing.
    
    **Response (200 OK):**
        JSON object with system information
    
    **Example Response:**
        .. code-block:: json
        
            {
              "service": "ada-brain",
              "version": "1.0.0",
              "python_version": "3.13.1",
              "features": {
                "rag": true,
                "specialists": true,
                "streaming": true,
                "memory": true
              },
              "endpoints": ["/v1/chat", "/v1/schema", ...],
              "models": {
                "llm": "deepseek-r1",
                "embedding": "nomic-embed-text"
              }
            }
    """
    import sys
    from brain.specialists import list_specialists
    
    # Get all registered routes
    endpoints = sorted([route.path for route in app.routes if hasattr(route, 'path')])
    
    # Count specialists
    specialists = list_specialists()
    enabled_specialists = [s for s in specialists if s.capability.enabled]
    
    return {
        "service": "ada-brain",
        "version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "features": {
            "rag": config.RAG_ENABLED,
            "specialists": len(enabled_specialists) > 0,
            "streaming": True,
            "memory": config.RAG_ENABLE_MEMORY,
            "pause_resume": config.SPECIALIST_PAUSE_RESUME,
        },
        "capabilities": {
            "specialist_count": len(specialists),
            "enabled_specialists": len(enabled_specialists),
            "specialist_names": [s.capability.name for s in enabled_specialists],
            "rag_features": {
                "persona": config.RAG_ENABLE_PERSONA,
                "faq": config.RAG_ENABLE_FAQ,
                "memory": config.RAG_ENABLE_MEMORY,
                "summary": config.RAG_ENABLE_SUMMARY,
                "turn": config.RAG_ENABLE_TURN,
            }
        },
        "models": {
            "llm": config.OLLAMA_MODEL,
            "embedding": config.EMBED_MODEL,
        },
        "endpoints": endpoints,
        "documentation": "/docs/index.html"
    }


@app.get('/v1/healthz', tags=['health'])
async def healthz():
    """
    Health check endpoint for the brain service.
    
    Returns detailed information about service status, dependencies, and configuration.
    
    **Response (200 OK):**
        JSON object with keys:
        
        - ok (bool): Overall service health status
        - service (str): Service name ("brain")
        - python (str): Python version
        - config (dict): Active configuration
        - persona (dict): Persona status
        - chroma (dict): Vector database status
    """
    try:
        # Compose detailed health info
        chroma_url = os.getenv("CHROMA_URL")
        chroma_ok = None
        chroma_error = None
        chroma_version = None
        if chroma_url:
            try:
                r = requests.get(chroma_url.rstrip('/') + '/api/v1/heartbeat', timeout=3)
                if r.status_code in (200, 204):
                    chroma_ok = True
                    try:
                        chroma_version = r.json()
                    except Exception:
                        chroma_version = None
                elif r.status_code in (404, 405, 410):
                    # Endpoint exists or method differs across versions – consider service reachable
                    chroma_ok = True
                    chroma_error = f"HTTP {r.status_code}"
                else:
                    chroma_ok = False
                    chroma_error = f"HTTP {r.status_code}"
            except Exception as e:
                chroma_ok = False
                chroma_error = str(e)

        persona_loaded = False
        try:
            if rag_store is not None:
                got_p = rag_store.col.get(where={"type": "persona"})
                persona_loaded = len(got_p.get('documents', [])) > 0
        except Exception:
            persona_loaded = False

        ok = True
        # Basic checks: collection exists and Chroma reachable
        if rag_store is not None and getattr(rag_store, 'col', None) is None:
            ok = False
        if chroma_url and (chroma_ok is False):
            ok = False

        payload = {
            "ok": ok,
            "service": "brain",
            "python": sys.version.split()[0],
            "config": config.get_config_dict(),
            "persona": {"loaded": persona_loaded},
            "chroma": {
                "ok": chroma_ok,
                "version": chroma_version,
                "error": chroma_error,
            },
        }
        status_code = 200 if ok else 503
        return JSONResponse(content=payload, status_code=status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'ok': False, 'error': str(e)}
        )



def _fetch_listenbrainz():
    return fetch_listenbrainz(LISTENBRAINZ_USER, LISTENBRAINZ_TOKEN)


def _format_media_for_prompt(media_info):
    return format_media_for_prompt(media_info)


@app.get('/v1/media/listenbrainz')
async def media_listenbrainz():
    data, err = _fetch_listenbrainz()
    if err and data is None:
        return JSONResponse(status_code=500, content={"error": err})
    if data is None:
        return JSONResponse(status_code=500, content={"error": "unavailable"})
    return data


@app.post('/v1/chat/stream', tags=['chat'])
async def chat_stream(request: Request):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).

    - **Method:** POST
    - **Path:** /v1/chat/stream
    - **Request JSON:** prompt (required), conversation_id, include_thinking, entity,
      save_memory, memory_text, turns_k, faq_k, memory_k
    - **Content-Type:** text/event-stream

    Events (newline-delimited, prefixed with ``data: ``):
    - ``token``: assistant response token
    - ``thinking``: reasoning token (only if include_thinking=true)
    - ``done``: final metadata (conversation_id, used_context, timestamps, request_id)
    - ``error``: error details

    Responses:
    - 200: Stream started
    - 400: Missing prompt
    - 500: Internal error (e.g., Ollama unreachable)

    Side effects: same as /v1/chat (turn upserts, optional memories, summaries).
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={'error': 'invalid json'})
    
    prompt = (data.get('prompt') or '').strip()
    if not prompt:
        return JSONResponse(status_code=400, content={'error': 'prompt required'})

    req_id = str(uuid.uuid4())[:8]
    conversation_id = data.get('conversation_id') or str(uuid.uuid4())
    include_thinking = data.get('include_thinking', False)
    user_timestamp = data.get('user_timestamp') or datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_memory = data.get('save_memory', False)
    memory_text = (data.get('memory_text') or '').strip() if save_memory else None
    entity = (data.get('entity') or '').strip() or None
    turns_k = int(data.get('turns_k', RAG_TURN_TOP_K))
    faq_k = int(data.get('faq_k', RAG_FAQ_TOP_K))
    memory_k = int(data.get('memory_k', RAG_MEMORY_TOP_K))

    # Build prompt using new modular PromptAssembler with caching
    if RAG_ENABLED and rag_store is not None:
        # Get active notices
        notices = get_active_notices()
        
        # Create assembler (initializes cache internally, pass rag_store instance)
        assembler = PromptAssembler(rag_store_instance=rag_store)
        
        # Build request context for specialists
        request_context = {
            'entity': entity,
            'media': data.get('media') if isinstance(data.get('media'), dict) else None,
            'ocr_context': data.get('ocr_context') if isinstance(data.get('ocr_context'), dict) else None,
        }
        
        # Build prompt (clean new API!)
        final_prompt = assembler.build_prompt(
            user_message=prompt,
            conversation_id=conversation_id,
            specialists=[],  # TODO: Load actual specialists
            notices=notices,
            request_context=request_context
        )
        
        # Get cache stats for logging
        cache_stats = assembler.cache.get_stats()
        logger.info(f"Request {req_id}: Cache hits={cache_stats.hits}, misses={cache_stats.misses}, hit_rate={cache_stats.hit_rate:.2%}")
        
        # Stub for used_context (kept for backward compat in metadata)
        used_context = {'cache': cache_stats.__dict__}
    else:
        final_prompt = f"User: {prompt}\nAssistant:"
        used_context = {}

    # Generator function for SSE streaming
    async def generate():
        nonlocal conversation_id
        try:
            accumulated_text = ""
            accumulated_thinking = ""
            
            # Stream from Ollama using modularized llm module (async)
            async for chunk in stream_chat_async(final_prompt, model=OLLAMA_MODEL, include_thinking=include_thinking):
                if 'error' in chunk:
                    yield f"data: {json.dumps({'type': 'error', 'error': chunk['error']})}\n\n"
                    return
                
                # Send response tokens
                if 'token' in chunk:
                    token = chunk['token']
                    accumulated_text += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                
                # Send thinking tokens if enabled
                if 'thinking' in chunk:
                    thinking_token = chunk['thinking']
                    accumulated_thinking += thinking_token
                    yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_token})}\n\n"
                
                # Check if stream is done
                if 'done' in chunk and chunk['done']:
                    assistant_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    
                    # Upsert turn after generation completes
                    if rag_store is not None and prompt and accumulated_text:
                        try:
                            cid = rag_store.upsert_turn(
                                conversation_id,
                                user_text=prompt,
                                assistant_text=accumulated_text,
                                user_ts=user_timestamp,
                                assistant_ts=assistant_timestamp,
                                source="chat",
                            )
                            conversation_id = cid
                        except Exception:
                            if RAG_DEBUG:
                                import traceback
                                print(f"[BRAIN][RAG][upsert][{req_id}] failed:\n" + traceback.format_exc())

                    # Summarize periodically
                    if RAG_ENABLE_SUMMARY and rag_store is not None and conversation_id:
                        try:
                            total_turn_docs = rag_store.count_turns(conversation_id)
                            if total_turn_docs >= 2 and (total_turn_docs // 2) % max(RAG_SUMMARY_EVERY_N, 1) == 0:
                                last_pairs = rag_store.get_last_turns(conversation_id, limit=RAG_SUMMARY_TURNS_WINDOW)
                                convo_lines = []
                                for t, m in last_pairs:
                                    role = (m or {}).get('role', 'context')
                                    ts = (m or {}).get('timestamp')
                                    if ts:
                                        convo_lines.append(f"- {role} [{ts}]: {t}")
                                    else:
                                        convo_lines.append(f"- {role}: {t}")
                                summary_prompt = (
                                    "Summarize the following recent conversation turns succinctly (3-5 bullet points). "
                                    "Capture decisions, facts, preferences, and open items.\n\n" + "\n".join(convo_lines)
                                )
                                stext, _, _ = complete(summary_prompt, model=OLLAMA_MODEL)
                                if stext:
                                    rag_store.upsert_summary(conversation_id, stext, timestamp=assistant_timestamp, source='chat')
                        except Exception:
                            if RAG_DEBUG:
                                import traceback
                                print(f"[BRAIN][RAG][summary][{req_id}] failed:\n" + traceback.format_exc())

                    # Consent-based memory save
                    if rag_store is not None and save_memory:
                        try:
                            mem_text = memory_text or accumulated_text
                            if mem_text and mem_text.strip():
                                rag_store.upsert_memory(
                                    mem_text.strip(),
                                    scope="global",
                                    importance=int(data.get('memory_importance', 3))
                                )
                        except Exception:
                            if RAG_DEBUG:
                                import traceback
                                print("[BRAIN][RAG][memory-upsert] failed:\n" + traceback.format_exc())

                    # Send completion metadata
                    metadata = {
                        'type': 'done',
                        'conversation_id': conversation_id,
                        'used_context': used_context,
                        'user_timestamp': user_timestamp,
                        'assistant_timestamp': assistant_timestamp,
                        'request_id': req_id,
                    }
                    yield f"data: {json.dumps(metadata)}\n\n"
                    break

        except Exception as e:
            error_data = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')


@app.get('/v1/memory', tags=['memory'])
async def list_memory(
    search: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    limit: int = Query(20)
):
    """
    Retrieve long-term memories with optional semantic search.

    - **Method:** GET
    - **Path:** /v1/memory
    - **Query params:**
      - search or query (optional): semantic search term; if omitted returns all memories
      - scope (optional): memory scope (e.g., ``global``, ``user:123``)
      - entity (optional): entity/topic scope
      - limit (optional): max results (default 20, capped at 100)

    Responses:
    - 200: ``{"items": [...]}`` - list of memories
    - 200: empty items if RAG disabled
    - 500: retrieval error
    """
    if rag_store is None:
        return {'items': []}
    
    # Support both 'search' and 'query' parameter names
    search_term = (search or query or '').strip()
    scope_str = (scope or '').strip()
    entity_str = (entity or '').strip()
    items = []
    
    try:
        if search_term:
            # Semantic search for matching memories
            hits = rag_store.retrieve_memories(query=search_term, k=min(limit, 100), entity=(entity_str or None))
            for text, meta in hits:
                items.append({'id': None, 'text': text, 'meta': meta})
        else:
            # No search query: list all memories
            rows = rag_store.list_memories(limit=min(limit, 100))
            for mid, text, meta in rows:
                if scope_str and (meta or {}).get('scope') != scope_str:
                    continue
                if entity_str and (meta or {}).get('scope') != f"entity:{entity_str}":
                    continue
                items.append({'id': mid, 'text': text, 'meta': meta})
    except Exception as err:
        return JSONResponse(status_code=500, content={'error': str(err)})
    
    return {'items': items}


@app.post('/v1/memory', tags=['memory'])
async def create_memory(request: Request):
    """
    Create a new long-term memory entry.

    - **Method:** POST
    - **Path:** /v1/memory
    - **Request JSON:** text (required), importance (1-5, default 3),
      scope (default ``global``), entity (optional)

    Responses:
    - 201: memory created (id returned)
    - 400: text missing
    - 503: RAG unavailable
    - 500: storage error
    """
    if rag_store is None:
        return JSONResponse(status_code=503, content={'error': 'RAG not available'})
    
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={'error': 'invalid json'})
    
    text = (data.get('text') or '').strip()
    if not text:
        return JSONResponse(status_code=400, content={'error': 'text is required'})
    scope = (data.get('scope') or 'global').strip() or 'global'
    entity = (data.get('entity') or '').strip()
    if entity and not scope.startswith('entity:'):
        scope = f'entity:{entity}'
    try:
        importance = int(data.get('importance', 3))
    except Exception:
        importance = 3
    tags = data.get('tags') if isinstance(data.get('tags'), list) else None
    try:
        mem_id = rag_store.upsert_memory(text, scope=scope, importance=importance, tags=tags, source='chat')
        return JSONResponse(status_code=201, content={'id': mem_id})
    except Exception as err:
        return JSONResponse(status_code=500, content={'error': str(err)})


@app.delete('/v1/memory/{mem_id}')
async def delete_memory(mem_id: str):
    """
    Delete a long-term memory entry by ID.

    - **Method:** DELETE
    - **Path:** /v1/memory/<mem_id>

    Responses:
    - 200: deleted
    - 503: RAG unavailable
    - 500: delete error (e.g., missing id)
    """
    if rag_store is None:
        return JSONResponse(status_code=503, content={'error': 'RAG not available'})
    try:
        rag_store.delete_memory(mem_id)
        return {'ok': True}
    except Exception as err:
        return JSONResponse(status_code=500, content={'error': str(err)})


@app.get('/v1/debug/rag', tags=['debug'])
async def rag_debug(conversation_id: Optional[str] = Query(None)):
    """
    Debug information for the RAG system (development only).

    - **Method:** GET
    - **Path:** /v1/debug/rag
    - **Query params:** conversation_id (optional)

    Responses:
    - 200: RAG stats (persona_count, faq_count, memory_count, summary_count, optional turn_count_for_conversation)
    - 404: debug disabled (RAG_DEBUG!=true or RAG unavailable)
    - 500: error retrieving stats
    """
    if not RAG_DEBUG or rag_store is None:
        return JSONResponse(status_code=404, content={'error': 'debug disabled'})
    try:
        cid = conversation_id
        info: Dict[str, Any] = {'conversation_id': cid}
        try:
            got_p = rag_store.col.get(where={"type": "persona"})
            info['persona_count'] = len(got_p.get('documents', []))
        except Exception as e:
            info['persona_error'] = str(e)
        # turn docs
        where_t: Dict[str, Any] = {"type": "turn"} if not cid else {"$and": [{"type": "turn"}, {"conversation_id": {"$eq": cid}}]}
        try:
            got_t = rag_store.col.get(where=where_t)
            docs_t = got_t.get('documents', [])
            metas_t = got_t.get('metadatas', [])
            info['turn_count'] = len(docs_t)
            sample = []
            for i in range(min(3, len(metas_t))):
                m = metas_t[i] or {}
                sample.append({
                    'role': m.get('role'),
                    'timestamp': m.get('timestamp'),
                    'conversation_id': m.get('conversation_id'),
                    'source': m.get('source'),
                })
            info['turn_sample'] = sample
        except Exception as e:
            info['turns_error'] = str(e)

        # summaries and memories
        try:
            where_s: Dict[str, Any] = {"type": "summary"} if not cid else {"$and": [{"type": "summary"}, {"conversation_id": {"$eq": cid}}]}
            got_s = rag_store.col.get(where=where_s)
            info['summary_count'] = len(got_s.get('documents', []))
        except Exception as e:
            info['summary_error'] = str(e)

        try:
            where_m: Dict[str, Any] = {"type": "memory"}
            got_m = rag_store.col.get(where=where_m)
            info['memory_count'] = len(got_m.get('documents', []))
        except Exception as e:
            info['memory_error'] = str(e)

        return info
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.get('/v1/debug/prompt', tags=['debug'])
async def prompt_debug(
    conversation_id: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    prompt: Optional[str] = Query(None),
    turns_k: int = Query(None),
    faq_k: int = Query(None),
    memory_k: int = Query(None),
    share_listenbrainz: Optional[str] = Query(None)
):
    """
    Return the assembled prompt sections and context that would be sent to the LLM.

    - Method: GET
    - Path: /v1/debug/prompt
    - Query params: conversation_id (optional), entity (optional), prompt (optional),
      turns_k, faq_k, memory_k
    - Returns: counts and sections for persona/faq/memory/turns/summaries plus the final prompt string.

    Requires RAG_DEBUG=true and an available rag_store.
    """
    if not RAG_DEBUG or rag_store is None:
        return JSONResponse(status_code=404, content={'error': 'debug disabled'})

    try:
        prompt_str = (prompt or '').strip() or 'debug'
        cid = (conversation_id or '').strip() or None
        entity_str = (entity or '').strip() or None
        turns_k_val = turns_k if turns_k is not None else RAG_TURN_TOP_K
        faq_k_val = faq_k if faq_k is not None else RAG_FAQ_TOP_K
        memory_k_val = memory_k if memory_k is not None else RAG_MEMORY_TOP_K
        share_lb = (share_listenbrainz or '').lower() in ('1', 'true', 'yes', 'on')

        user_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sections: List[str] = []
        media_info = None
        used_context: Dict[str, Any] = {"persona": None, "faqs": [], "turns": [], "memories": [], "summaries": [], "entity": entity_str, "media": None}

        # Inject system notices (active, unacknowledged)
        try:
            notices = get_active_notices()
            if notices:
                notice_lines = []
                for n in notices[:3]:
                    msg = n.get('message','')[:200] + ('...' if len(n.get('message','')) > 200 else '')
                    severity_label = n.get('severity','').upper()
                    notice_lines.append(f"⚠️ {severity_label} ALERT [{n.get('component','')}.{n.get('code','')}]: {msg}")
                sections.append("🔔 SYSTEM NOTICES — Acknowledge these immediately before responding to the user:\n" + "\n".join(notice_lines))
        except Exception:
            pass

        sections.append(IDENTITY_BLOCK)

        # Media (ListenBrainz) if requested
        if share_lb:
            media_info, media_err = _fetch_listenbrainz()
            used_context["media"] = media_info
            if media_info and isinstance(media_info, dict):
                media_line = _format_media_for_prompt(media_info)
                if media_line:
                    sections.append(media_line)

        # Persona
        if RAG_ENABLE_PERSONA:
            persona = rag_store.load_persona_block()
            if persona:
                if isinstance(persona, tuple):
                    p_text, p_meta = persona
                else:
                    p_text, p_meta = str(persona), {}
                short_persona = p_text if len(p_text) <= PERSONA_MAX_CHARS else p_text[:PERSONA_MAX_CHARS]
                sections.append("Persona and style guidelines (global):\n" + short_persona)
                used_context["persona"] = {
                    "included": True,
                    "version": (p_meta or {}).get("version"),
                    "timestamp": (p_meta or {}).get("timestamp"),
                    "length": len(short_persona),
                }
            else:
                used_context["persona"] = {"included": False}

        # Memory
        if RAG_ENABLE_MEMORY and memory_k_val > 0:
            mem_hits = rag_store.retrieve_memories(query=prompt_str, k=memory_k_val, entity=entity_str)
            if mem_hits:
                mem_lines = []
                for text_m, meta_m in mem_hits:
                    imp = (meta_m or {}).get('importance')
                    scope = (meta_m or {}).get('scope', 'global')
                    tag_str = ''
                    tags = (meta_m or {}).get('tags')
                    if isinstance(tags, list) and tags:
                        tag_str = f" tags={','.join(tags)}"
                    if imp is not None:
                        mem_lines.append(f"- ({scope}, importance={imp}{tag_str}) {text_m}")
                    else:
                        mem_lines.append(f"- ({scope}{tag_str}) {text_m}")
                    used_context["memories"].append(text_m)
                sections.append("Long-term memory:\n" + "\n".join(mem_lines))

        # FAQs
        if RAG_ENABLE_FAQ and faq_k_val > 0:
            faq_hits = rag_store.retrieve_faqs(query=prompt_str, k=faq_k_val)
            if faq_hits:
                faq_lines = []
                for text, meta in faq_hits:
                    topic = (meta or {}).get('topic', 'faq')
                    faq_lines.append(f"- ({topic}) {text}")
                    used_context["faqs"].append(text)
                sections.append("Reference snippets (FAQs):\n" + "\n".join(faq_lines))

        # Conversation turns
        if RAG_ENABLE_TURN and turns_k_val > 0:
            hits = rag_store.retrieve_turns(query=prompt_str, k=turns_k_val, conversation_id=cid)
            if hits:
                turn_lines = []
                for text_t, meta_t in hits:
                    role = (meta_t or {}).get('role', 'context')
                    ts = (meta_t or {}).get('timestamp')
                    if ts:
                        turn_lines.append(f"- {role} [{ts}]: {text_t}")
                    else:
                        turn_lines.append(f"- {role}: {text_t}")
                    used_context["turns"].append(text_t)
                sections.append("Recent conversation turns (most relevant first):\n" + "\n".join(turn_lines))

        # Summaries
        if RAG_ENABLE_SUMMARY and cid:
            sum_hits = rag_store.retrieve_summaries(conversation_id=cid, k=2)
            if sum_hits:
                used_context["summaries"] = [t for t, _ in sum_hits]
                sections.append("Conversation summaries:\n" + "\n".join(f"- {t}" for t, _ in sum_hits))

        instructions = (
            "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
            "conversation memory when relevant. If the user asks about times or durations, use the provided "
            "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
        )
        reminder = f"Reminder: You are {config.AI_NAME}, {config.AI_USER_NAME}'s assistant. Always identify as {config.AI_NAME}."
        current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
        assembled = ("\n\n".join(sections) + "\n\n" if sections else "") + instructions + "\n" + reminder + "\n" + current_ts_line
        final_prompt = f"{assembled}\nUser: {prompt_str}\nAssistant:"

        return {
            "conversation_id": cid,
            "entity": entity_str,
            "prompt_used": prompt_str,
            "final_prompt": final_prompt,
            "sections": sections,
            "used_context": used_context,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get('/v1/conversations/recent')
async def get_recent_conversations(limit: int = Query(10)):
    """
    Return a list of recent conversations with preview and metadata.

    - Method: GET
    - Path: /v1/conversations/recent
    - Query params: limit (optional, default 10)
    - Returns: [{id, preview, timestamp, turn_count}, ...]
    """
    if rag_store is None:
        return JSONResponse(status_code=503, content={'error': 'RAG not available'})

    try:
        conversations = rag_store.get_recent_conversations(limit=limit)
        return conversations
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.get('/v1/conversations/{conversation_id}')
async def get_conversation(conversation_id: str):
    """
    Return all turns for a specific conversation.

    - Method: GET
    - Path: /v1/conversations/<conversation_id>
    - Returns: {conversation_id, turns: [{role, text, timestamp}, ...]}
    """
    if rag_store is None:
        return JSONResponse(status_code=503, content={'error': 'RAG not available'})

    try:
        turns = rag_store.get_conversation_turns(conversation_id)
        return {
            'conversation_id': conversation_id,
            'turns': turns
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7000)
