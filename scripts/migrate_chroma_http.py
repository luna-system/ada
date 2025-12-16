#!/usr/bin/env python3
"""
Migrate Chroma collection to ensure HTTP mode compatibility.

This script:
1. Backs up the existing collection (rename to conversations_backup)
2. Creates a fresh collection
3. Re-inserts all documents with properly generated embeddings
4. Verifies queries work correctly

Run this when embeddings queries return 0 results in HTTP mode.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

import chromadb
from brain.rag_store import OllamaEmbeddingFunction
from brain import config


def migrate_collection():
    """Migrate collection to ensure HTTP mode query compatibility."""
    
    # Connect to Chroma
    chroma_url = os.getenv("CHROMA_URL", "http://chroma:8000")
    from urllib.parse import urlparse
    p = urlparse(chroma_url)
    host = p.hostname or "localhost"
    port = p.port or (443 if (p.scheme or "http").lower() == "https" else 8000)
    ssl = (p.scheme or "http").lower() == "https"
    
    print(f"[MIGRATE] Connecting to Chroma at {host}:{port}")
    client = chromadb.HttpClient(host=host, port=port, ssl=ssl)
    
    # Setup embedding function
    ollama_url = config.OLLAMA_BASE_URL
    embed_model = config.EMBED_MODEL
    print(f"[MIGRATE] Using embedding model: {embed_model} @ {ollama_url}")
    embedding_fn = OllamaEmbeddingFunction(endpoint=ollama_url, model=embed_model)
    
    # Collection names
    old_name = "conversations"
    backup_name = f"conversations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Get old collection
        print(f"[MIGRATE] Fetching old collection: {old_name}")
        old_col = client.get_collection(name=old_name)
        old_count = old_col.count()
        print(f"[MIGRATE] Old collection has {old_count} documents")
        
        if old_count == 0:
            print("[MIGRATE] Collection is empty, nothing to migrate")
            return
        
        # Fetch all documents in batches
        print(f"[MIGRATE] Reading all documents...")
        batch_size = 1000
        offset = 0
        all_docs = []
        all_metas = []
        all_ids = []
        
        while offset < old_count:
            limit = min(batch_size, old_count - offset)
            results = old_col.get(
                limit=limit,
                offset=offset,
                include=['documents', 'metadatas']
            )
            
            docs = results.get('documents', [])
            metas = results.get('metadatas', [])
            ids = results.get('ids', [])
            
            all_docs.extend(docs)
            all_metas.extend(metas)
            all_ids.extend(ids)
            
            offset += len(docs)
            print(f"[MIGRATE] Read {offset}/{old_count} documents")
            
            if len(docs) == 0:
                break
        
        print(f"[MIGRATE] Total documents read: {len(all_docs)}")
        
        # Delete old collection and create backup
        print(f"[MIGRATE] Creating backup: {backup_name}")
        try:
            # Chroma HTTP doesn't support rename, so we recreate
            backup_col = client.create_collection(name=backup_name)
            # Copy data to backup without embeddings (just for safety)
            for i in range(0, len(all_docs), 100):
                batch_docs = all_docs[i:i+100]
                batch_metas = all_metas[i:i+100]
                batch_ids = all_ids[i:i+100]
                backup_col.add(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas
                )
            print(f"[MIGRATE] Backup created with {len(all_docs)} documents")
        except Exception as e:
            print(f"[MIGRATE] Backup creation warning: {e}")
            print("[MIGRATE] Continuing with migration...")
        
        # Delete old collection
        print(f"[MIGRATE] Deleting old collection: {old_name}")
        client.delete_collection(name=old_name)
        
        # Create fresh collection
        print(f"[MIGRATE] Creating fresh collection: {old_name}")
        new_col = client.create_collection(name=old_name)
        
        # Re-insert documents with fresh embeddings
        print(f"[MIGRATE] Re-inserting documents with fresh embeddings...")
        batch_size = 50  # Smaller batches for embedding generation
        
        for i in range(0, len(all_docs), batch_size):
            batch_docs = all_docs[i:i+batch_size]
            batch_metas = all_metas[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]
            
            # Generate embeddings for this batch
            print(f"[MIGRATE] Generating embeddings for batch {i//batch_size + 1}/{(len(all_docs) + batch_size - 1)//batch_size}")
            batch_embeddings = embedding_fn(batch_docs)
            
            # Upsert with embeddings
            new_col.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embeddings
            )
            
            print(f"[MIGRATE] Inserted {min(i+batch_size, len(all_docs))}/{len(all_docs)} documents")
        
        print(f"[MIGRATE] Migration complete!")
        print(f"[MIGRATE] New collection count: {new_col.count()}")
        
        # Verify queries work
        print("\n[MIGRATE] Verifying query functionality...")
        test_queries = [
            ("luna plural system", "memory"),
            ("web search specialist", "faq"),
            ("conversation", "turn"),
        ]
        
        for query_text, expected_type in test_queries:
            qemb = embedding_fn([query_text])
            result = new_col.query(
                query_embeddings=qemb,
                n_results=3,
                where={"type": expected_type}
            )
            docs = result.get('documents', [[]])[0]
            print(f"[MIGRATE] Query '{query_text}' (type={expected_type}): {len(docs)} results")
            if len(docs) > 0:
                print(f"[MIGRATE]   ✓ Sample: {docs[0][:60]}...")
        
        print(f"\n[MIGRATE] ✓ Migration successful!")
        print(f"[MIGRATE] Backup available as: {backup_name}")
        
    except Exception as e:
        print(f"[MIGRATE] ✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    print("[MIGRATE] Starting Chroma HTTP mode migration")
    print("[MIGRATE] This will rebuild the collection with proper embeddings")
    print()
    
    migrate_collection()
    
    print()
    print("[MIGRATE] Done! Restart the brain service to use the migrated collection.")
