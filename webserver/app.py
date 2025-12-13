from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests
import datetime
import json
import csv
from pathlib import Path
from typing import List, Dict, Any

from rag import RagStore

# Serve static files from /app/static so docker volume mount works
# (compose.yaml mounts ./webserver/static -> /app/static)
app = Flask(__name__, static_folder="/app/static", static_url_path="/static")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# RAG configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Section toggles and sizes
RAG_ENABLE_PERSONA = os.getenv("RAG_ENABLE_PERSONA", "true").lower() == "true"
RAG_ENABLE_FAQ = os.getenv("RAG_ENABLE_FAQ", "true").lower() == "true"
RAG_TURNS_TOP_K = int(os.getenv("RAG_TURNS_TOP_K", os.getenv("RAG_TOP_K", "4")))
RAG_FAQ_TOP_K = int(os.getenv("RAG_FAQ_TOP_K", "2"))
RAG_DEBUG = os.getenv("RAG_DEBUG", "false").lower() == "true"

rag_store = None
if RAG_ENABLED:
    try:
        rag_store = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=OLLAMA_BASE_URL,
            embed_model=EMBED_MODEL,
        )
    except Exception as e:
        # If RAG init fails, continue without blocking the app
        rag_store = None

    # Autoload seed data (persona and FAQs) if enabled
    def _autoload_seed():
        if rag_store is None:
            return
        try:
            # Persona
            if os.getenv("RAG_AUTOLOAD_PERSONA", "true").lower() == "true":
                persona_path = os.getenv("RAG_PERSONA_PATH", "/app/prompt.md")
                p = Path(persona_path)
                if p.exists() and p.is_file():
                    try:
                        text = p.read_text(encoding="utf-8").strip()
                        if text:
                            # version from mtime ISO date
                            mtime = datetime.datetime.utcfromtimestamp(p.stat().st_mtime).isoformat() + "Z"
                            rag_store.upsert_doc(
                                text,
                                type="persona",
                                scope="global",
                                version=mtime,
                                source="kb",
                            )
                            print(f"[RAG] Autoloaded persona from {persona_path}")
                    except Exception as perr:
                        print(f"[RAG] Persona autoload failed: {perr}")

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
                            print(f"[RAG] FAQ autoload skipped: unsupported extension for {faq_path}")
                        if count:
                            print(f"[RAG] Autoloaded {count} FAQ entries from {faq_path}")
                    except Exception as ferr:
                        print(f"[RAG] FAQ autoload failed: {ferr}")
        except Exception as err:
            print(f"[RAG] Autoload seed unexpected error: {err}")

    # Run autoload once at startup
    _autoload_seed()

@app.route('/')
def index():
    # Serve the SPA/HTML from the configured static folder
    return send_from_directory(app.static_folder, 'index.html')

# Lightweight diagnostics to verify RAG wiring at runtime
@app.route('/api/debug/rag', methods=['GET'])
def rag_debug():
    if not RAG_DEBUG or rag_store is None:
        return jsonify({'error': 'debug disabled'}), 404
    try:
        cid = request.args.get('conversation_id')
        info: Dict[str, Any] = {'conversation_id': cid}
        # Count persona docs
        try:
            got_p = rag_store.col.get(where={"type": "persona"})
            info['persona_count'] = len(got_p.get('documents', []))
        except Exception as e:
            info['persona_error'] = str(e)
        # Count turn docs (optionally scoped by cid)
        where_t: Dict[str, Any] = {"type": "turn"}
        if cid:
            where_t['conversation_id'] = cid
        try:
            got_t = rag_store.col.get(where=where_t)
            docs_t = got_t.get('documents', [])
            metas_t = got_t.get('metadatas', [])
            info['turn_count'] = len(docs_t)
            # Return a small sample of metas for inspection
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
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    include_thinking = bool(data.get('include_thinking', False))
    conversation_id = data.get('conversation_id')
    turns_k = int(data.get('turns_k', RAG_TURNS_TOP_K))
    faq_k = int(data.get('faq_k', RAG_FAQ_TOP_K))

    # Build payload for Ollama. Per your backend contract, the toggle
    # must be a top-level "think" property on the payload object.
    final_prompt = prompt

    used_context: Dict[str, Any] = {"persona": None, "faqs": [], "turns": []}
    # Capture when we received the user's message
    user_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if rag_store is not None and final_prompt:
        try:
            sections: List[str] = []
            dbg = {"persona": False, "faqs": 0, "turns": 0, "cid": conversation_id}

            # Persona block (always-on if enabled and available)
            if RAG_ENABLE_PERSONA:
                persona = rag_store.load_persona_block()
                if persona:
                    p_text, p_meta = persona
                    # Keep concise persona; if it's very long, take the first ~800 chars
                    short_persona = p_text if len(p_text) <= 2000 else p_text[:2000]
                    sections.append("Persona and style guidelines (global):\n" + short_persona)
                    used_context["persona"] = {
                        "included": True,
                        "version": (p_meta or {}).get("version"),
                        "timestamp": (p_meta or {}).get("timestamp"),
                    }
                else:
                    used_context["persona"] = {"included": False}

            # FAQs/reference (similarity-only)
            if RAG_ENABLE_FAQ and faq_k > 0:
                faq_hits = rag_store.retrieve_faqs(query=prompt, k=faq_k)
                if faq_hits:
                    faq_lines = []
                    for text, meta in faq_hits:
                        topic = (meta or {}).get('topic', 'faq')
                        faq_lines.append(f"- ({topic}) {text}")
                        used_context["faqs"].append(text)
                    sections.append("Reference snippets (FAQs):\n" + "\n".join(faq_lines))
                    dbg["faqs"] = len(faq_hits)

            # Conversation turns with timestamps (recency-aware)
            if turns_k > 0:
                # Retrieve prior turns strictly before this message's timestamp,
                # so we don't return the just-upserted current turn on a fast second request.
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
                        used_context["turns"].append(text)
                    sections.append("Memory (most relevant first):\n" + "\n".join(turn_lines))
                    dbg["turns"] = len(hits)

            # Build instructions and final prompt
            instructions = (
                "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
                "conversation memory when relevant. If the user asks about times or durations, use the provided "
                "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
            )
            current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
            assembled = f"{instructions}\n\n" + ("\n\n".join(sections) + "\n\n" if sections else "")
            final_prompt = (
                f"{assembled}"
                f"{current_ts_line}\n"
                f"User: {prompt}\nAssistant:"
            )
            if RAG_DEBUG:
                print(f"[RAG][build] cid={dbg['cid']} persona={bool(used_context.get('persona',{}).get('included'))} faqs={dbg['faqs']} turns={dbg['turns']}")
        except Exception:
            # If retrieval fails, proceed without context
            pass

    payload = {
        'model': OLLAMA_MODEL,
        'prompt': final_prompt,
        'stream': False,
        'think': include_thinking,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        # Ollama may return both 'response' and (optionally) 'thinking' when think=true
        text = result.get('response', '')
        thinking = result.get('thinking', '') if include_thinking else ''
        # Timestamp when we produce the assistant's message
        assistant_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Upsert this turn into the store (non-blocking)
        if rag_store is not None and prompt and text:
            try:
                cid = rag_store.upsert_turn(
                    conversation_id,
                    user_text=prompt,
                    assistant_text=text,
                    user_ts=user_timestamp,
                    assistant_ts=assistant_timestamp,
                    source="chat",
                )
                conversation_id = cid
            except Exception:
                if RAG_DEBUG:
                    import traceback
                    print("[RAG][upsert] failed:\n" + traceback.format_exc())
                pass

        return jsonify({
            'response': text,
            'thinking': thinking,
            'conversation_id': conversation_id,
            'used_context': used_context,
            'user_timestamp': user_timestamp,
            'assistant_timestamp': assistant_timestamp,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
