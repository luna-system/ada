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

        if self.use_http:
            emb = self.embedding_fn([text])
            self.col.upsert(ids=[doc_id], documents=[text], metadatas=[meta], embeddings=emb)
        else:
            self.col.upsert(ids=[doc_id], documents=[text], metadatas=[meta])
        return doc_id

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
