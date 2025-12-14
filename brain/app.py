from flask import Flask, request, jsonify, Response, stream_with_context
import os
import requests
import datetime
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import sys
import time
import uuid
from dotenv import load_dotenv

load_dotenv()

from rag import RagStore

app = Flask(__name__)

# Ollama + models
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# RAG configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Section toggles and sizes
RAG_ENABLE_PERSONA = os.getenv("RAG_ENABLE_PERSONA", "true").lower() == "true"
RAG_ENABLE_FAQ = os.getenv("RAG_ENABLE_FAQ", "true").lower() == "true"
RAG_ENABLE_MEMORY = os.getenv("RAG_ENABLE_MEMORY", "true").lower() == "true"
RAG_ENABLE_SUMMARY = os.getenv("RAG_ENABLE_SUMMARY", "true").lower() == "true"
# Stream/non-stream parity toggles
RAG_ENABLE_TURN = os.getenv("RAG_ENABLE_TURN", "true").lower() == "true"
RAG_TURN_TOP_K = int(os.getenv("RAG_TURN_TOP_K", os.getenv("RAG_TURNS_TOP_K", os.getenv("RAG_TOP_K", "4"))))
RAG_SUMMARY_TOP_K = int(os.getenv("RAG_SUMMARY_TOP_K", "2"))
RAG_FAQ_TOP_K = int(os.getenv("RAG_FAQ_TOP_K", "2"))
RAG_MEMORY_TOP_K = int(os.getenv("RAG_MEMORY_TOP_K", "3"))
RAG_MEMORY_IMPORTANCE_WEIGHT = float(os.getenv("RAG_MEMORY_IMPORTANCE_WEIGHT", "0.5"))
RAG_SUMMARY_EVERY_N = int(os.getenv("RAG_SUMMARY_EVERY_N", "8"))
RAG_SUMMARY_TURNS_WINDOW = int(os.getenv("RAG_SUMMARY_TURNS_WINDOW", "12"))
RAG_DEBUG = os.getenv("RAG_DEBUG", "false").lower() == "true"
PERSONA_MAX_CHARS = int(os.getenv("RAG_PERSONA_MAX_CHARS", "2000"))

# System identity block (used in all chat endpoints)
IDENTITY_BLOCK = (
    "System identity:\n"
    "- You are Ada, a helpful personal assistant for user luna (the developer).\n"
    "- Always refer to yourself as Ada; never claim other model names (e.g., DeepSeek).\n"
    "- If asked your name or who you are, reply: 'I am Ada, luna's assistant.'\n"
    "- Tone: warm, concise, conversational; mirror the user's formality; sparse emojis.\n"
)

# ListenBrainz integration
LISTENBRAINZ_USER = os.getenv("LISTENBRAINZ_USER")
LISTENBRAINZ_TOKEN = os.getenv("LISTENBRAINZ_TOKEN")
LISTENBRAINZ_CACHE = {"ts": 0.0, "data": None}

rag_store = None
if RAG_ENABLED:
    try:
        rag_store = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=OLLAMA_BASE_URL,
            embed_model=EMBED_MODEL,
        )
    except Exception:
        rag_store = None

    def _autoload_seed():
        if rag_store is None:
            return
        try:
            # Persona
            if os.getenv("RAG_AUTOLOAD_PERSONA", "true").lower() == "true":
                persona_path = os.getenv("RAG_PERSONA_PATH", "/app/persona.md")
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
            if os.getenv("RAG_AUTOLOAD_FAQ", "false").lower() == "true":
                faq_path = os.getenv("RAG_FAQ_PATH", "/app/seed/faqs.jsonl")
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

    _autoload_seed()


@app.route('/v1/healthz', methods=['GET'])
def healthz():
    """
    Health check endpoint for the brain service.
    
    Returns detailed information about service status, dependencies, and configuration.
    
    **HTTP Method:** GET
    
    **Response (200 OK):**
        JSON object with keys:
        
        - ok (bool): Overall service health status
        - service (str): Service name ("brain")
        - python (str): Python version
        - config (dict): Active configuration including:
            - OLLAMA_BASE_URL: LLM backend URL
            - OLLAMA_MODEL: Active LLM model name
            - CHROMA_URL: Vector database URL
            - RAG_ENABLE_*: Feature toggles for Persona, FAQ, Memory, Summary
        - persona (dict): Persona status with 'loaded' boolean
        - chroma (dict): Vector database connectivity status with:
            - ok (bool): Connectivity status
            - version (str): Database version if available
            - error (str): Error message if unhealthy
    
    **Response (503 Service Unavailable):**
        Returned if critical dependencies are unavailable.
    
    **Example:**
        >>> curl http://localhost:7000/v1/healthz
        {
            "ok": true,
            "service": "brain",
            "python": "3.13.0",
            "config": {...},
            "persona": {"loaded": true},
            "chroma": {"ok": true, "version": "0.5.11", "error": null}
        }
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
                # Some Chroma builds return 410 on /api/v1/heartbeat even when healthy.
                # Treat any reachable response (including 410) as an indicator the server is up.
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
            "config": {
                "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL"),
                "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL"),
                "CHROMA_URL": chroma_url,
                "RAG_ENABLE_PERSONA": os.getenv("RAG_ENABLE_PERSONA", "true"),
                "RAG_ENABLE_FAQ": os.getenv("RAG_ENABLE_FAQ", "true"),
                "RAG_ENABLE_MEMORY": os.getenv("RAG_ENABLE_MEMORY", "true"),
                "RAG_ENABLE_SUMMARY": os.getenv("RAG_ENABLE_SUMMARY", "true"),
            },
            "persona": {"loaded": persona_loaded},
            "chroma": {
                "ok": chroma_ok,
                "version": chroma_version,
                "error": chroma_error,
            },
        }
        return jsonify(payload), (200 if ok else 503)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500



def _fetch_listenbrainz():
    if not LISTENBRAINZ_USER:
        return None, "LISTENBRAINZ_USER not configured"
    now = time.time()
    cached = LISTENBRAINZ_CACHE.get("data")
    if cached and (now - LISTENBRAINZ_CACHE.get("ts", 0) < 5):
        return cached, None

    headers = {"User-Agent": "ada-v1/brain"}
    if LISTENBRAINZ_TOKEN:
        headers["Authorization"] = f"Token {LISTENBRAINZ_TOKEN}"

    def normalize(meta, status, listened_at=None):
        if not meta:
            return None
        return {
            "source": "listenbrainz",
            "status": status,
            "artist": (meta or {}).get("artist_name"),
            "track": (meta or {}).get("track_name"),
            "release": (meta or {}).get("release_name"),
            "listened_at": listened_at,
        }

    base = "https://api.listenbrainz.org/1/user/" + LISTENBRAINZ_USER
    
    # Try to fetch recent listens with count=1 (most recent, which is effectively "now playing")
    try:
        r = requests.get(base + "/listens", headers=headers, params={"count": 1}, timeout=5)
        if r.status_code == 200:
            payload = r.json() or {}
            listens = (payload.get("payload") or {}).get("listens") or []
            if listens:
                first = listens[0]
                meta = (first.get("track_metadata") or {})
                listened_at = (first.get("listened_at") or first.get("played_at"))
                info = normalize(meta, status="playing", listened_at=listened_at)
                LISTENBRAINZ_CACHE.update({"ts": now, "data": info})
                return info, None
    except Exception as e:
        return None, str(e)

    info = {"source": "listenbrainz", "status": "idle"}
    LISTENBRAINZ_CACHE.update({"ts": now, "data": info})
    return info, None


def _format_media_for_prompt(media_info: dict) -> str | None:
    """Format ListenBrainz media info as natural language for the prompt."""
    if not media_info or not isinstance(media_info, dict):
        return None
    status = media_info.get("status")
    if status == "playing":
        artist = media_info.get("artist", "Unknown Artist")
        track = media_info.get("track", "Unknown Track")
        return f"luna has chosen to share that she is currently listening to the song {track} by artist {artist}."
    elif status == "recent":
        artist = media_info.get("artist", "Unknown Artist")
        track = media_info.get("track", "Unknown Track")
        listened_at = media_info.get("listened_at")
        time_str = ""
        if listened_at:
            try:
                from datetime import datetime as dt
                ldt = dt.fromisoformat(listened_at.replace("Z", "+00:00"))
                now_dt = dt.now(ldt.tzinfo)
                delta = now_dt - ldt
                days = delta.days
                hours = delta.seconds // 3600
                if days > 0:
                    time_str = f"{days} day{'s' if days != 1 else ''} ago"
                elif hours > 0:
                    time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    time_str = "a few minutes ago"
            except Exception:
                time_str = "recently"
        else:
            time_str = "recently"
        return f"luna has chosen to share that the last song she listened to was {track} by artist {artist} {time_str}."
    return None


@app.route('/v1/media/listenbrainz', methods=['GET'])
def media_listenbrainz():
    data, err = _fetch_listenbrainz()
    if err and data is None:
        return jsonify({"error": err}), 500
    if data is None:
        return jsonify({"error": "unavailable"}), 500
    return jsonify(data)


@app.route('/v1/chat/stream', methods=['POST'])
def chat_stream():
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
    data = request.get_json()
    prompt = (data.get('prompt') or '').strip()
    if not prompt:
        return jsonify({'error': 'prompt required'}), 400

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

    # Build RAG context (same as non-streaming endpoint)
    final_prompt = prompt
    media_info = data.get('media') if isinstance(data.get('media'), dict) else None
    used_context = {'persona': None, 'faqs': [], 'memories': [], 'turns': [], 'summaries': [], 'entity': entity, 'media': media_info}
    t_retrieve = 0
    t_assemble = 0

    if RAG_ENABLED and rag_store is not None:
        try:
            t0 = time.perf_counter()
            sections = []

            # Identity guardrail
            sections.append(IDENTITY_BLOCK)

            # Media (ListenBrainz) if provided
            if media_info and isinstance(media_info, dict):
                media_line = _format_media_for_prompt(media_info)
                if media_line:
                    sections.append(media_line)

            # Persona
            if RAG_ENABLE_PERSONA:
                persona_doc = rag_store.load_persona_block()
                if persona_doc:
                    if isinstance(persona_doc, tuple):
                        p_text, p_meta = persona_doc
                    else:
                        p_text, p_meta = str(persona_doc), {}
                    short_persona = p_text if len(p_text) <= PERSONA_MAX_CHARS else p_text[:PERSONA_MAX_CHARS]
                    sections.append("Persona and style guidelines (global):\n" + short_persona)
                    used_context['persona'] = {
                        'included': True,
                        'version': (p_meta or {}).get('version'),
                        'timestamp': (p_meta or {}).get('timestamp'),
                    }
                else:
                    used_context['persona'] = {'included': False}

            # Long-term memory
            if RAG_ENABLE_MEMORY and memory_k > 0:
                mem_hits = rag_store.retrieve_memories(query=prompt, k=memory_k, entity=entity)
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
                        used_context['memories'].append(text_m)
                    sections.append("Long-term memory:\n" + "\n".join(mem_lines))

            # FAQs/reference
            if RAG_ENABLE_FAQ and faq_k > 0:
                faq_hits = rag_store.retrieve_faqs(query=prompt, k=faq_k)
                if faq_hits:
                    faq_lines = []
                    for text, meta in faq_hits:
                        topic = (meta or {}).get('topic', 'faq')
                        faq_lines.append(f"- ({topic}) {text}")
                        used_context['faqs'].append(text)
                    sections.append("Reference snippets (FAQs):\n" + "\n".join(faq_lines))

            # Conversation turns with timestamps (recency-aware)
            if RAG_ENABLE_TURN and turns_k > 0:
                hits = rag_store.retrieve_turns(query=prompt, k=turns_k, conversation_id=conversation_id)
                if hits:
                    turn_lines = []
                    for text, meta in hits:
                        role = (meta or {}).get('role', 'context')
                        ts = (meta or {}).get('timestamp')
                        if ts:
                            turn_lines.append(f"- {role} [{ts}]: {text}")
                        else:
                            turn_lines.append(f"- {role}: {text}")
                        used_context['turns'].append(text)
                    sections.append("Recent conversation turns (most relevant first):\n" + "\n".join(turn_lines))

            # Conversation summaries
            if RAG_ENABLE_SUMMARY and conversation_id:
                sum_hits = rag_store.retrieve_summaries(conversation_id=conversation_id, k=RAG_SUMMARY_TOP_K)
                if sum_hits:
                    used_context['summaries'] = [t for t, _ in sum_hits]
                    sections.append("Conversation summaries:\n" + "\n".join(f"- {t}" for t, _ in sum_hits))

            instructions = (
                "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
                "conversation memory when relevant. If the user asks about times or durations, use the provided "
                "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
            )
            reminder = "Reminder: You are Ada, Luna's assistant. Always identify as Ada."
            current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
            assembled = ("\n\n".join(sections) + "\n\n" if sections else "") + instructions + "\n" + reminder + "\n" + current_ts_line
            final_prompt = f"{assembled}\nUser: {prompt}\nAssistant:"
            t_retrieve = time.perf_counter() - t0
            t_assemble = time.perf_counter() - t0
        except Exception:
            pass

    # Generator function for SSE streaming
    def generate():
        nonlocal conversation_id
        try:
            payload = {
                'model': OLLAMA_MODEL,
                'prompt': final_prompt,
                'stream': True,
                'think': include_thinking,
            }

            # Stream from Ollama
            accumulated_text = ""
            accumulated_thinking = ""
            
            with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        
                        # Send response tokens
                        if 'response' in chunk and chunk['response']:
                            token = chunk['response']
                            accumulated_text += token
                            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                        
                        # Send thinking tokens if enabled
                        if include_thinking and 'thinking' in chunk and chunk['thinking']:
                            thinking_token = chunk['thinking']
                            accumulated_thinking += thinking_token
                            yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_token})}\n\n"
                        
                        # Check if stream is done
                        if chunk.get('done', False):
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

                            # Summarize periodically (mirror non-streaming endpoint)
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
                                        sum_payload = {
                                            'model': OLLAMA_MODEL,
                                            'prompt': summary_prompt,
                                            'stream': False,
                                            'think': False,
                                        }
                                        rsum = requests.post(OLLAMA_API_URL, json=sum_payload, timeout=120)
                                        rsum.raise_for_status()
                                        sdata = rsum.json()
                                        stext = (sdata.get('response') or '').strip()
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

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/v1/memory', methods=['GET'])
def list_memory():
    """
    Retrieve long-term memories with optional semantic search.

    - **Method:** GET
    - **Path:** /v1/memory
    - **Query params:**
      - search (optional): semantic query; if omitted returns empty list
      - scope (optional): memory scope (e.g., ``global``, ``user:123``)
      - entity (optional): entity/topic scope
      - limit (optional): max results (default 20, capped at 20)

    Responses:
    - 200: ``{"items": [...]}``
    - 200: empty items if RAG disabled
    - 500: retrieval error
    """
    if rag_store is None:
        return jsonify({'items': []})
    q = (request.args.get('search') or '').strip()
    scope = (request.args.get('scope') or '').strip()
    entity = (request.args.get('entity') or '').strip()
    try:
        limit = int(request.args.get('limit', '20'))
    except Exception:
        limit = 20
    items = []
    try:
        if q:
            hits = rag_store.retrieve_memories(query=q, k=min(limit, 20), entity=(entity or None))
            for text, meta in hits:
                items.append({'id': None, 'text': text, 'meta': meta})
        else:
            rows = rag_store.list_memories(limit=limit)
            for mid, text, meta in rows:
                if scope and (meta or {}).get('scope') != scope:
                    continue
                if entity and (meta or {}).get('scope') != f"entity:{entity}":
                    continue
                items.append({'id': mid, 'text': text, 'meta': meta})
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    return jsonify({'items': items})


@app.route('/v1/memory', methods=['POST'])
def create_memory():
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
        return jsonify({'error': 'RAG not available'}), 503
    data = request.json or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'text is required'}), 400
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
        return jsonify({'id': mem_id})
    except Exception as err:
        return jsonify({'error': str(err)}), 500


@app.route('/v1/memory/<mem_id>', methods=['DELETE'])
def delete_memory(mem_id: str):
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
        return jsonify({'error': 'RAG not available'}), 503
    try:
        rag_store.delete_memory(mem_id)
        return jsonify({'ok': True})
    except Exception as err:
        return jsonify({'error': str(err)}), 500


@app.route('/v1/debug/rag', methods=['GET'])
def rag_debug():
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
        return jsonify({'error': 'debug disabled'}), 404
    try:
        cid = request.args.get('conversation_id')
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

        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/v1/debug/prompt', methods=['GET'])
def prompt_debug():
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
        return jsonify({'error': 'debug disabled'}), 404

    try:
        prompt = (request.args.get('prompt') or '').strip() or 'debug'
        conversation_id = (request.args.get('conversation_id') or '').strip() or None
        entity = (request.args.get('entity') or '').strip() or None
        turns_k = int(request.args.get('turns_k', RAG_TURN_TOP_K))
        faq_k = int(request.args.get('faq_k', RAG_FAQ_TOP_K))
        memory_k = int(request.args.get('memory_k', RAG_MEMORY_TOP_K))
        share_lb = (request.args.get('share_listenbrainz') or '').lower() in ('1', 'true', 'yes', 'on')

        user_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sections: List[str] = []
        media_info = None
        used_context: Dict[str, Any] = {"persona": None, "faqs": [], "turns": [], "memories": [], "summaries": [], "entity": entity, "media": None}

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
        if RAG_ENABLE_MEMORY and memory_k > 0:
            mem_hits = rag_store.retrieve_memories(query=prompt, k=memory_k, entity=entity)
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
        if RAG_ENABLE_FAQ and faq_k > 0:
            faq_hits = rag_store.retrieve_faqs(query=prompt, k=faq_k)
            if faq_hits:
                faq_lines = []
                for text, meta in faq_hits:
                    topic = (meta or {}).get('topic', 'faq')
                    faq_lines.append(f"- ({topic}) {text}")
                    used_context["faqs"].append(text)
                sections.append("Reference snippets (FAQs):\n" + "\n".join(faq_lines))

        # Conversation turns
        if RAG_ENABLE_TURN and turns_k > 0:
            hits = rag_store.retrieve_turns(query=prompt, k=turns_k, conversation_id=conversation_id)
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
        if RAG_ENABLE_SUMMARY and conversation_id:
            sum_hits = rag_store.retrieve_summaries(conversation_id=conversation_id, k=2)
            if sum_hits:
                used_context["summaries"] = [t for t, _ in sum_hits]
                sections.append("Conversation summaries:\n" + "\n".join(f"- {t}" for t, _ in sum_hits))

        instructions = (
            "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
            "conversation memory when relevant. If the user asks about times or durations, use the provided "
            "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
        )
        reminder = "Reminder: You are Ada, Luna's assistant. Always identify as Ada."
        current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
        assembled = ("\n\n".join(sections) + "\n\n" if sections else "") + instructions + "\n" + reminder + "\n" + current_ts_line
        final_prompt = f"{assembled}\nUser: {prompt}\nAssistant:"

        return jsonify({
            "conversation_id": conversation_id,
            "entity": entity,
            "prompt_used": prompt,
            "final_prompt": final_prompt,
            "sections": sections,
            "used_context": used_context,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
