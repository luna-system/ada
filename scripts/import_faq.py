#!/usr/bin/env python3
"""
Import FAQs into Chroma as typed documents.

Supports JSONL and CSV input:
  - JSONL: one object per line with keys: question, answer, [topic]
  - CSV: headers: question, answer, [topic]

Examples:
  uv run python scripts/import_faq.py --file faqs.jsonl
  uv run python scripts/import_faq.py --file faqs.csv

Environment (used by RagStore):
  - CHROMA_URL (optional): http://localhost:8000 for Chroma Server; otherwise embedded at /data/chroma
  - OLLAMA_BASE_URL (default http://localhost:11434)
  - OLLAMA_EMBED_MODEL (default nomic-embed-text)
"""

import argparse
import csv
import json
import os
import sys
from typing import Iterable, Dict

from rag import RagStore


def iter_jsonl(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSON on line {i}: {e}")
            yield obj


def iter_csv(path: str) -> Iterable[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def main() -> int:
    parser = argparse.ArgumentParser(description="Import FAQs into Chroma (type=faq)")
    parser.add_argument("--file", required=True, help="Path to JSONL or CSV file")
    parser.add_argument("--topic", default=None, help="Default topic to apply when missing")
    args = parser.parse_args()

    path = args.file
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2

    ext = os.path.splitext(path)[1].lower()
    if ext == ".jsonl":
        it = iter_jsonl(path)
    elif ext == ".csv":
        it = iter_csv(path)
    else:
        print("Error: --file must be .jsonl or .csv", file=sys.stderr)
        return 2

    store = RagStore(
        persist_dir=os.getenv("CHROMA_PERSIST", "/data/chroma"),
        collection_name=os.getenv("CHROMA_COLLECTION", "conversations"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )

    count = 0
    for obj in it:
        q = (obj.get("question") or obj.get("q") or "").strip()
        a = (obj.get("answer") or obj.get("a") or "").strip()
        topic = (obj.get("topic") or args.topic or "").strip() or None

        if not q or not a:
            # Skip incomplete rows
            continue

        text = f"Q: {q}\nA: {a}"
        store.upsert_doc(
            text,
            type="faq",
            scope="global",
            topic=topic,
            source="kb",
        )
        count += 1

    print({"status": "ok", "imported": count, "type": "faq"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
