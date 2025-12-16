# @ai-indexable: core-functionality
# @ai-purpose: Vector storage interface for semantic search over memories, conversations, persona, and FAQ
# @ai-dependencies: chromadb, requests, ollama (for embeddings)
# @ai-related: brain/app.py, brain/prompt_builder.py, scripts/consolidate_memories.py
# @ai-key-classes: RagStore, OllamaEmbeddingFunction
# @ai-data-flow: Receives text → generates embeddings via Ollama → stores in ChromaDB → semantic search retrieval

import os
import uuid
import datetime
from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urlparse

import requests
import chromadb


class OllamaEmbeddingFunction:
    """
    Minimal embedding function for Chroma that calls Ollama's /api/embeddings.

    Expected interface: __call__(texts: List[str]) -> List[List[float]]
    """

    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint.rstrip("/")
        self.model = model

    def __call__(self, texts: List[str]):
        out = []
        for t in texts:
            payload = {"model": self.model, "prompt": t}
            r = requests.post(f"{self.endpoint}/api/embeddings", json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            # Ollama returns { embedding: [..] }
            out.append(data.get("embedding", []))
        return out


class RagStore:
    def __init__(
        self,
        persist_dir: str = "/data/chroma",
        collection_name: str = "conversations",
        ollama_base_url: str = "http://localhost:11434",
        embed_model: str = "nomic-embed-text",
    ):
        # Choose Chroma client: prefer server if CHROMA_URL is set, otherwise embedded persistence
        chroma_url = os.getenv("CHROMA_URL")
        self.use_http = bool(chroma_url)
        if self.use_http:
            p = urlparse(chroma_url)
            host = p.hostname or "localhost"
            port = p.port or (443 if (p.scheme or "http").lower() == "https" else 8000)
            ssl = (p.scheme or "http").lower() == "https"
            self.client = chromadb.HttpClient(host=host, port=port, ssl=ssl)
        else:
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)

        self.embedding_fn = OllamaEmbeddingFunction(
            endpoint=ollama_base_url, model=embed_model
        )

        # Create or get collection
        # Note: In server (HTTP) mode, Chroma cannot execute client-side embedding functions.
        # We therefore do NOT attach an embedding_function and instead pass embeddings explicitly on upsert/query.
        try:
            if self.use_http:
                self.col = self.client.get_collection(name=collection_name)
            else:
                self.col = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn,
                )
        except Exception:
            if self.use_http:
                self.col = self.client.create_collection(name=collection_name)
            else:
                self.col = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn,
                )

    @staticmethod
    def _ensure_id(cid: Optional[str]) -> str:
        return cid or str(uuid.uuid4())

    def upsert_turn(
        self,
        conversation_id: Optional[str],
        user_text: str,
        assistant_text: str,
        user_ts: Optional[str] = None,
        assistant_ts: Optional[str] = None,
        source: str = "chat",
    ) -> str:
        """Store one chat turn: user and assistant as two docs.

        Returns the conversation_id used (generated if None).
        """
        cid = self._ensure_id(conversation_id)
        ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        documents = [user_text, assistant_text]
        # Produce ISO 8601 UTC timestamps if not provided
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        u_ts = user_ts or now_iso
        a_ts = assistant_ts or now_iso
        metadatas = [
            {
                "conversation_id": cid,
                "role": "user",
                "timestamp": u_ts,
                "source": source,
                "type": "turn",
                "scope": "conversation",
            },
            {
                "conversation_id": cid,
                "role": "assistant",
                "timestamp": a_ts,
                "source": source,
                "type": "turn",
                "scope": "conversation",
            },
        ]
        if self.use_http:
            # Compute embeddings client-side and pass explicitly
            embeddings = self.embedding_fn(documents)
            self.col.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        else:
            self.col.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return cid

    def retrieve(self, query: str, k: int = 4, conversation_id: Optional[str] = None) -> List[Tuple[str, dict]]:
        """Return top-k documents [(text, metadata), ...]. If conversation_id is provided,
        restrict retrieval to that conversation; otherwise search globally.
        """
        where: Optional[Dict[str, Any]] = {"conversation_id": conversation_id} if conversation_id else None
        if self.use_http:
            qemb = self.embedding_fn([query])
            result = self.col.query(query_embeddings=qemb, n_results=k, where=where)
        else:
            result = self.col.query(query_texts=[query], n_results=k, where=where)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        return list(zip(docs, metas))

    # --- New helpers for typed documents (FAQ/Docs/Persona/Policy) ---
    def upsert_doc(
        self,
        text: str,
        *,
        type: str,
        scope: str = "global",
        topic: Optional[str] = None,
        version: Optional[str] = None,
        source: str = "kb",
        timestamp: Optional[str] = None,
        conversation_id: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        extra_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Insert a single non-turn document (faq/doc/persona/policy/summary).
        Returns the generated id.
        """
        doc_id = str(uuid.uuid4())
        ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
        meta: Dict[str, Any] = {
            "type": type,
            "scope": scope,
            "source": source,
            "timestamp": ts,
        }
        if topic:
            meta["topic"] = topic
        if version:
            meta["version"] = version
        if conversation_id:
            meta["conversation_id"] = conversation_id
        if importance is not None:
            try:
                imp = int(importance)
            except Exception:
                imp = None
            if imp is not None:
                meta["importance"] = imp
        if tags:
            meta["tags"] = tags
        if extra_meta:
            meta.update(extra_meta)

        if self.use_http:
            emb = self.embedding_fn([text])
            self.col.upsert(ids=[doc_id], documents=[text], metadatas=[meta], embeddings=emb)
        else:
            self.col.upsert(ids=[doc_id], documents=[text], metadatas=[meta])
        return doc_id

    # ---- Long-term memory helpers ----
    def upsert_memory(
        self,
        text: str,
        *,
        scope: str = "global",
        importance: int = 3,
        tags: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
        source: str = "chat",
    ) -> str:
        return self.upsert_doc(
            text,
            type="memory",
            scope=scope,
            importance=importance,
            tags=tags,
            timestamp=timestamp,
            source=source,
        )

    def retrieve_memories(self, query: str, k: int = 3, entity: Optional[str] = None) -> List[Tuple[str, dict]]:
        """Retrieve global/entity memories by similarity and rerank by importance + recency.
        If `entity` is provided, prefer scope="entity:<entity>" but also allow global as backfill.
        """
        entity_scope = f"entity:{entity}" if entity else None
        where: Dict[str, Any] = {"type": "memory"}
        try:
            if entity_scope:
                # Try entity-scoped first
                w_ent: Dict[str, Any] = {"$and": [{"type": "memory"}, {"scope": {"$eq": entity_scope}}]}
                if self.use_http:
                    qemb = self.embedding_fn([query])
                    result = self.col.query(query_embeddings=qemb, n_results=max(k, 6), where=w_ent)
                else:
                    result = self.col.query(query_texts=[query], n_results=max(k, 6), where=w_ent)
            else:
                if self.use_http:
                    qemb = self.embedding_fn([query])
                    result = self.col.query(query_embeddings=qemb, n_results=max(k, 6), where=where)
                else:
                    result = self.col.query(query_texts=[query], n_results=max(k, 6), where=where)
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            items = list(zip(docs, metas))
            # If entity-scoped yielded too few, backfill with global memories
            if entity_scope and len(items) < k:
                w_global = {"$and": [{"type": "memory"}, {"scope": {"$eq": "global"}}]}
                if self.use_http:
                    qemb = self.embedding_fn([query])
                    res2 = self.col.query(query_embeddings=qemb, n_results=max(k, 6), where=w_global)
                else:
                    res2 = self.col.query(query_texts=[query], n_results=max(k, 6), where=w_global)
                docs2 = res2.get("documents", [[]])[0]
                metas2 = res2.get("metadatas", [[]])[0]
                items2 = list(zip(docs2, metas2))
                # merge unique preserving order
                seen = set()
                merged: List[Tuple[str, dict]] = []
                for d,m in items + items2:
                    key = (d, (m or {}).get("timestamp"))
                    if key in seen:
                        continue
                    seen.add(key)
                    merged.append((d,m))
                items = merged
        except Exception:
            # Fallback to listing all memories
            try:
                if entity_scope:
                    got = self.col.get(where={"$and": [{"type": "memory"}, {"scope": {"$eq": entity_scope}}]})
                    docs = got.get("documents", [])
                    metas = got.get("metadatas", [])
                    items = list(zip(docs, metas))
                    if len(items) < k:
                        got2 = self.col.get(where={"$and": [{"type": "memory"}, {"scope": {"$eq": "global"}}]})
                        items += list(zip(got2.get("documents", []), got2.get("metadatas", [])))
                else:
                    got = self.col.get(where=where)
                    items = list(zip(got.get("documents", []), got.get("metadatas", [])))
            except Exception:
                items = []

        # Rerank: importance (0..1) and recency decay
        half_life = float(os.getenv("RAG_RECENCY_HALF_LIFE_SECONDS", "3600"))
        now = datetime.datetime.now(datetime.timezone.utc)

        def recency_score(ts_iso: Optional[str]) -> float:
            if not ts_iso:
                return 0.0
            try:
                ts = datetime.datetime.fromisoformat(ts_iso)
                age = (now - ts).total_seconds()
                if age < 0:
                    age = 0
                return 0.5 ** (age / half_life) if half_life > 0 else 0.0
            except Exception:
                return 0.0

        def importance_norm(meta: dict) -> float:
            imp = (meta or {}).get("importance")
            try:
                imp = int(imp)
            except Exception:
                imp = 0
            return max(0, min(5, imp)) / 5.0

        w_imp = float(os.getenv("RAG_MEMORY_IMPORTANCE_WEIGHT", "0.5"))
        items.sort(
            key=lambda it: (w_imp * importance_norm(it[1] or {})) + ((1 - w_imp) * recency_score((it[1] or {}).get("timestamp"))),
            reverse=True,
        )
        return items[:k]

    # ---- Conversation summaries ----
    def upsert_summary(self, conversation_id: str, text: str, *, timestamp: Optional[str] = None, source: str = "chat") -> str:
        """Store a brief summary for a conversation."""
        return self.upsert_doc(
            text,
            type="summary",
            scope="conversation",
            source=source,
            timestamp=timestamp,
            conversation_id=conversation_id,
        )

    def retrieve_summaries(self, conversation_id: str, k: int = 2) -> List[Tuple[str, dict]]:
        where: Dict[str, Any] = {"$and": [{"type": "summary"}, {"conversation_id": {"$eq": conversation_id}}]}
        try:
            got = self.col.get(where=where)
            docs = got.get("documents", [])
            metas = got.get("metadatas", [])
            pairs = list(zip(docs, metas))
            # order by timestamp desc
            def ts_of(meta: dict) -> float:
                try:
                    ts = datetime.datetime.fromisoformat((meta or {}).get("timestamp"))
                    return ts.timestamp()
                except Exception:
                    return 0.0
            pairs.sort(key=lambda p: ts_of(p[1] or {}), reverse=True)
            return pairs[:k]
        except Exception:
            return []

    def count_turns(self, conversation_id: str) -> int:
        where: Dict[str, Any] = {"$and": [{"type": "turn"}, {"conversation_id": {"$eq": conversation_id}}]}
        try:
            got = self.col.get(where=where)
            return len(got.get("documents", []))
        except Exception:
            return 0

    def get_last_turns(self, conversation_id: str, limit: int = 8) -> List[Tuple[str, dict]]:
        where: Dict[str, Any] = {"$and": [{"type": "turn"}, {"conversation_id": {"$eq": conversation_id}}]}
        try:
            got = self.col.get(where=where)
            docs = got.get("documents", [])
            metas = got.get("metadatas", [])
            pairs = list(zip(docs, metas))
            # order by timestamp desc and take last N in chronological order
            def ts_of(meta: dict) -> float:
                try:
                    ts = datetime.datetime.fromisoformat((meta or {}).get("timestamp"))
                    return ts.timestamp()
                except Exception:
                    return 0.0
            pairs.sort(key=lambda p: ts_of(p[1] or {}), reverse=True)
            latest = pairs[:limit]
            latest.reverse()  # chronological
            return latest
        except Exception:
            return []

    def list_memories(self, limit: int = 20) -> List[Tuple[str, str, dict]]:
        """Return [(id, text, meta), ...] ordered by timestamp desc then importance."""
        try:
            got = self.col.get(where={"type": "memory"})
            ids = got.get("ids", [])
            docs = got.get("documents", [])
            metas = got.get("metadatas", [])
            rows = list(zip(ids, docs, metas))
        except Exception:
            rows = []

        def ts_of(meta: dict) -> float:
            try:
                ts = datetime.datetime.fromisoformat((meta or {}).get("timestamp"))
                return ts.timestamp()
            except Exception:
                return 0.0

        def imp_of(meta: dict) -> int:
            try:
                return int((meta or {}).get("importance", 0))
            except Exception:
                return 0

        rows.sort(key=lambda r: (ts_of(r[2]), imp_of(r[2])), reverse=True)
        return rows[:limit]

    def delete_memory(self, mem_id: str) -> None:
        try:
            self.col.delete(ids=[mem_id])
        except Exception:
            pass

    def retrieve_turns(
        self,
        query: str,
        k: int,
        conversation_id: Optional[str],
    ) -> List[Tuple[str, dict]]:
        """Retrieve turns only (type=turn) scoped to a conversation, with recency-aware reranking."""
        # Chroma HTTP 'where' expects a single operator; combine constraints under $and when needed
        if conversation_id:
            where: Dict[str, Any] = {"$and": [{"type": "turn"}, {"conversation_id": {"$eq": conversation_id}}]}
        else:
            where = {"type": "turn"}

        items: List[Tuple[str, dict]] = []

        # Try exact last-N by recency if conversation_id is provided (strongest signal for continuity)
        # This avoids relying on similarity for very short queries like "what did I just say?".
        if conversation_id:
            try:
                got = self.col.get(where=where)
                g_docs = got.get("documents", [])
                g_metas = got.get("metadatas", [])
                items = list(zip(g_docs, g_metas))
            except Exception:
                items = []

        # If we didn't get enough items yet, backfill with similarity search
        if len(items) < k:
            try:
                if self.use_http:
                    qemb = self.embedding_fn([query])
                    result = self.col.query(query_embeddings=qemb, n_results=k, where=where)
                else:
                    result = self.col.query(query_texts=[query], n_results=k, where=where)
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                sim_items = list(zip(docs, metas))
                # Merge unique by (text, timestamp) to avoid dupes
                seen = set(( (m or {}).get("timestamp"), d) for d, m in items)
                for d, m in sim_items:
                    key = ((m or {}).get("timestamp"), d)
                    if key not in seen:
                        items.append((d, m))
                        seen.add(key)
            except Exception:
                pass
        weight = float(os.getenv("RAG_RECENCY_WEIGHT", "0.3"))
        half_life = float(os.getenv("RAG_RECENCY_HALF_LIFE_SECONDS", "3600"))
        now = datetime.datetime.now(datetime.timezone.utc)

        def recency_score(ts_iso: Optional[str]) -> float:
            if not ts_iso:
                return 0.0
            try:
                ts = datetime.datetime.fromisoformat(ts_iso)
                age = (now - ts).total_seconds()
                if age < 0:
                    age = 0
                # exponential decay: half-life
                return 0.5 ** (age / half_life) if half_life > 0 else 0.0
            except Exception:
                return 0.0

        # Rank purely by recency since similarity scores aren't exposed.
        items.sort(key=lambda it: recency_score((it[1] or {}).get("timestamp")), reverse=True)
        return items[:k]

    def retrieve_faqs(self, query: str, k: int = 2) -> List[Tuple[str, dict]]:
        """Retrieve FAQs (type=faq), global scope, similarity-only."""
        where: Dict[str, Any] = {"type": "faq"}
        if self.use_http:
            qemb = self.embedding_fn([query])
            result = self.col.query(query_embeddings=qemb, n_results=k, where=where)
        else:
            result = self.col.query(query_texts=[query], n_results=k, where=where)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        return list(zip(docs, metas))

    def load_persona_block(self) -> Optional[Tuple[str, dict]]:
        """Return the most recent persona doc (type=persona) if any, else None.
        We pick the latest by timestamp.
        """
        where: Dict[str, Any] = {"type": "persona"}
        # Fetch a handful and pick latest by timestamp
        result = self.col.get(where=where)
        docs = result.get("documents", [])
        metas = result.get("metadatas", [])
        if not docs:
            return None
        # Pair and select by timestamp desc
        pairs = list(zip(docs, metas))
        def ts_of(meta: dict) -> float:
            try:
                ts = datetime.datetime.fromisoformat(meta.get("timestamp"))
                return ts.timestamp()
            except Exception:
                return 0.0
        pairs.sort(key=lambda p: ts_of(p[1] or {}), reverse=True)
        return pairs[0]

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return a list of recent conversations with metadata.
        Each entry: {id, preview, timestamp, turn_count}
        """
        # Get all turns sorted by timestamp
        where: Dict[str, Any] = {"type": "turn"}
        result = self.col.get(where=where)
        docs = result.get("documents", [])
        metas = result.get("metadatas", [])
        
        if not docs:
            return []
        
        # Group by conversation_id
        convos: Dict[str, Dict[str, Any]] = {}
        for doc, meta in zip(docs, metas):
            cid = meta.get("conversation_id")
            if not cid:
                continue
            
            ts_str = meta.get("timestamp", "")
            try:
                ts = datetime.datetime.fromisoformat(ts_str)
            except Exception:
                ts = datetime.datetime.min
            
            if cid not in convos:
                convos[cid] = {
                    "id": cid,
                    "preview": doc[:100] if meta.get("role") == "user" else "",
                    "timestamp": ts,
                    "turn_count": 0
                }
            
            # Update with earliest user message as preview
            if meta.get("role") == "user" and not convos[cid]["preview"]:
                convos[cid]["preview"] = doc[:100]
            
            # Track latest timestamp
            if ts > convos[cid]["timestamp"]:
                convos[cid]["timestamp"] = ts
            
            convos[cid]["turn_count"] += 1
        
        # Sort by timestamp desc and limit
        sorted_convos = sorted(convos.values(), key=lambda c: c["timestamp"], reverse=True)[:limit]
        
        # Convert timestamps to ISO strings
        for c in sorted_convos:
            c["timestamp"] = c["timestamp"].isoformat()
        
        return sorted_convos

    def get_conversation_turns(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all turns for a specific conversation, ordered chronologically.
        Returns: [{role, text, timestamp}, ...]
        """
        where: Dict[str, Any] = {"$and": [{"type": "turn"}, {"conversation_id": conversation_id}]}
        result = self.col.get(where=where)
        docs = result.get("documents", [])
        metas = result.get("metadatas", [])
        
        if not docs:
            return []
        
        # Build turns list
        turns = []
        for doc, meta in zip(docs, metas):
            turns.append({
                "role": meta.get("role", "user"),
                "text": doc,
                "timestamp": meta.get("timestamp", "")
            })
        
        # Sort by timestamp
        turns.sort(key=lambda t: t["timestamp"])
        return turns
