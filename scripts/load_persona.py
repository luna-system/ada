#!/usr/bin/env python3
"""
Load a persona prompt into Chroma as a typed document.

Usage examples:
  uv run python scripts/load_persona.py --file prompt.md --version 2025-12-12
  uv run python scripts/load_persona.py --text "Be concise and friendly." --version v1

Environment (used by RagStore):
  - CHROMA_URL (optional): http://localhost:8000 for Chroma Server; otherwise embedded at /data/chroma
  - OLLAMA_BASE_URL (default http://localhost:11434)
  - OLLAMA_EMBED_MODEL (default nomic-embed-text)
"""

import argparse
import os
import sys
from rag import RagStore


def main():
    parser = argparse.ArgumentParser(description="Load a persona prompt into Chroma")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="Path to a markdown/text file containing the persona")
    group.add_argument("--text", type=str, help="Persona text provided directly on the command line")
    parser.add_argument("--version", type=str, default=None, help="Version label to store in metadata (e.g., date or semantic version)")
    parser.add_argument("--scope", type=str, default="global", help="Scope metadata (default: global)")
    parser.add_argument("--source", type=str, default="kb", help="Source metadata (default: kb)")
    args = parser.parse_args()

    if args.file:
        if not os.path.isfile(args.file):
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 2
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    else:
        text = (args.text or "").strip()

    if not text:
        print("Error: persona text is empty", file=sys.stderr)
        return 2

    store = RagStore(
        persist_dir=os.getenv("CHROMA_PERSIST", "/data/chroma"),
        collection_name=os.getenv("CHROMA_COLLECTION", "conversations"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )

    doc_id = store.upsert_doc(
        text,
        type="persona",
        scope=args.scope,
        version=args.version,
        source=args.source,
    )

    print({"status": "ok", "doc_id": doc_id, "type": "persona", "version": args.version})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
