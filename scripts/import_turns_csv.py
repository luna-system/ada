#!/usr/bin/env python3
"""
Import a CSV of turn pairs (user, assistant) into the RAG store.

Usage:
  uv run python scripts/import_turns_csv.py --file path/to/turns.csv \
      --conversation-id my-thread-123 \
      [--source import] [--timestamp-col timestamp]

CSV format (headers expected):
  user,assistant[,timestamp]

Notes:
  - If --conversation-id is omitted, a new UUID will be generated and printed.
  - If a 'timestamp' column exists and --timestamp-col is not specified, it will be used
    for both user and assistant timestamps for that row. Otherwise, current UTC is used.
  - This script talks to the same Chroma & Ollama endpoints as the brain service via RagStore.
    It can be run against the brain container (recommended) or on the host if env matches.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
import uuid
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Reuse the shared RAG module; ensure /app is on sys.path when running ad-hoc
try:
    from rag import RagStore
except ModuleNotFoundError:  # pragma: no cover
    import sys as _sys, os as _os
    if "/app" not in _sys.path:
        _sys.path.append("/app")
    from rag import RagStore


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import CSV of turn pairs into RAG store")
    p.add_argument("--file", required=True, help="Path to CSV file (user,assistant[,timestamp])")
    p.add_argument("--conversation-id", dest="conversation_id", default=None,
                   help=(
                       "Conversation/thread id to import into. If omitted, the CSV base filename "
                       "(without extension) will be used. If the filename is empty or generic (e.g., 'turns'), "
                       "a new UUID will be generated."
                   ))
    p.add_argument("--timestamp-col", dest="timestamp_col", default=None,
                   help="Optional CSV column name containing ISO8601 timestamps")
    p.add_argument("--start", dest="start_iso", default=None,
                   help=(
                       "Optional ISO8601 UTC start time to synthesize timestamps when the CSV has none, "
                       "e.g. 2025-01-01T00:00:00Z"
                   ))
    p.add_argument("--step-seconds", dest="step_seconds", type=int, default=60,
                   help="Step in seconds between consecutive rows when synthesizing timestamps (default: 60)")
    p.add_argument("--source", default="import", help="Metadata source tag (default: import)")
    # Optional promotion of rows as long-term memories
    p.add_argument("--as-memory", action="store_true",
                   help="Also upsert each row as a long-term memory entry (type=memory)")
    p.add_argument("--entity", default=None,
                   help="Optional entity/topic scope for promoted memories (scope=entity:<name>)")
    p.add_argument("--importance", type=int, default=None,
                   help="Importance 1..5 for promoted memories (default: none)")
    p.add_argument(
        "--tags",
        default=None,
        action="append",
        help=(
            "Tags for promoted memories. May be provided multiple times or as a comma-separated list. "
            "Examples: --tags imported --tags project-x   or   --tags imported,project-x"
        ),
    )
    return p.parse_args()


def iso_or_none(s: str | None) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        # Validate/normalize
        dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return s
    except Exception:
        return None


def main() -> int:
    args = parse_args()

    # Env configuration mirrors brain/app.py
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    chroma_url = os.getenv("CHROMA_URL")  # when set, uses HTTP client

    store = RagStore(
        persist_dir="/data/chroma",
        collection_name="conversations",
        ollama_base_url=ollama_base,
        embed_model=embed_model,
    )

    # Determine conversation id precedence:
    # 1) explicit --conversation-id
    # 2) CSV base filename (without extension), if non-empty and not a generic placeholder
    # 3) generated UUID
    conv_id: Optional[str] = args.conversation_id
    if not conv_id:
        base = os.path.splitext(os.path.basename(args.file))[0].strip()
        # Treat common generic names as placeholders to avoid accidental collisions
        generic_names = {"turns", "chat", "conversation", "convo", "transcript", "history"}
        if base and base.lower() not in generic_names:
            conv_id = base
        else:
            conv_id = str(uuid.uuid4())
    print(f"[import] conversation_id={conv_id}")

    path = args.file
    if not os.path.exists(path):
        print(f"[import] file not found: {path}", file=sys.stderr)
        return 2

    rows = 0
    imported = 0
    # Prepare synthetic timestamp baseline if requested
    start_dt: Optional[dt.datetime] = None
    if args.start_iso:
        try:
            start_dt = dt.datetime.fromisoformat(args.start_iso.replace("Z", "+00:00"))
            if start_dt.tzinfo is None:
                # Assume UTC if naive
                start_dt = start_dt.replace(tzinfo=dt.timezone.utc)
        except Exception:
            print(f"[import] invalid --start value (expect ISO8601): {args.start_iso}", file=sys.stderr)
            return 2

    step = max(1, int(args.step_seconds))
    synth_index = 0
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        # Require user/assistant columns
        if not set(["user", "assistant"]).issubset(reader.fieldnames or []):
            print("[import] CSV must contain headers: user,assistant[,timestamp]", file=sys.stderr)
            return 2
        tcol = args.timestamp_col or ("timestamp" if "timestamp" in (reader.fieldnames or []) else None)
        for row in reader:
            rows += 1
            u = (row.get("user") or "").strip()
            a = (row.get("assistant") or "").strip()
            if not u and not a:
                continue
            # Assign timestamps (same timestamp for both sides if provided)
            ts = iso_or_none(row.get(tcol)) if tcol else None
            if not ts and start_dt:
                # Synthesize an increasing timestamp per row
                ts_dt = start_dt + dt.timedelta(seconds=synth_index * step)
                ts = ts_dt.isoformat()
                synth_index += 1
            try:
                store.upsert_turn(
                    conv_id,
                    user_text=u,
                    assistant_text=a,
                    user_ts=ts,
                    assistant_ts=ts,
                    source=args.source,
                )
                # Optionally promote as a long-term memory
                if args.as_memory:
                    scope = f"entity:{args.entity}" if args.entity else "global"
                    # Normalize tags: accept multiple --tags flags and/or comma-separated values
                    tag_list = []
                    if args.tags:
                        for entry in args.tags:
                            if entry:
                                tag_list.extend([t.strip() for t in str(entry).split(',') if t.strip()])
                    # Chroma metadata values must be scalar; encode tags into a comma-separated string
                    tags_meta = ",".join(tag_list) if tag_list else None
                    imp = None
                    if args.importance is not None:
                        try:
                            imp = max(1, min(5, int(args.importance)))
                        except Exception:
                            imp = None
                    text_for_memory = f"User: {u}\nAssistant: {a}".strip()
                    if text_for_memory:
                        store.upsert_memory(
                            text_for_memory,
                            scope=scope,
                            importance=(imp if imp is not None else 3),
                            tags=tags_meta,
                            timestamp=ts,
                            source=args.source,
                        )
                imported += 1
            except Exception as e:
                print(f"[import] upsert failed at row {rows}: {e}", file=sys.stderr)

    print(f"[import] done: {imported}/{rows} rows imported into conversation_id={conv_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
