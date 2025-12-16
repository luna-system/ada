#!/usr/bin/env python3
"""
Test suite for prompt building and RAG retrieval.

Tests:
- Prompt building with various configurations
- RAG retrieval for turns, FAQs, memories, summaries
- Specialist docs retrieval
- Edge cases and error handling
"""
import sys
import os
from pathlib import Path

from brain.rag_store import RagStore
from brain.prompt_builder import build_prompt
from brain import config
import asyncio


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.details = None
    
    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        result = f"{status} - {self.name}"
        if self.details:
            result += f"\n      {self.details}"
        if self.error:
            result += f"\n      Error: {self.error}"
        return result


async def test_rag_store_initialization():
    """Test RAG store initializes correctly."""
    result = TestResult("RAG Store Initialization")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        count = rag.col.count()
        result.details = f"Collection has {count} documents"
        result.passed = count > 0
        if count == 0:
            result.error = "Collection is empty"
    except Exception as e:
        result.error = str(e)
    return result


async def test_memory_retrieval():
    """Test memory retrieval with embeddings."""
    result = TestResult("Memory Retrieval")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        # Test with a query that should match memories
        mem_hits = rag.retrieve_memories(query="luna plural system", k=3, entity=None)
        result.details = f"Retrieved {len(mem_hits)} memories"
        result.passed = len(mem_hits) > 0
        
        if not result.passed:
            result.error = "No memories retrieved"
    except Exception as e:
        result.error = str(e)
    return result


async def test_faq_retrieval():
    """Test FAQ retrieval with embeddings."""
    result = TestResult("FAQ Retrieval")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        faq_hits = rag.retrieve_faqs(query="web search specialist", k=3)
        result.details = f"Retrieved {len(faq_hits)} FAQs"
        result.passed = len(faq_hits) > 0
        
        if not result.passed:
            result.error = "No FAQs retrieved"
    except Exception as e:
        result.error = str(e)
    return result


async def test_turn_retrieval():
    """Test turn retrieval."""
    result = TestResult("Turn Retrieval")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        # Get a conversation ID that exists
        all_turns = rag.col.get(where={"type": "turn"}, limit=1, include=["metadatas"])
        if not all_turns.get("metadatas"):
            result.error = "No turns in collection"
            return result
        
        conv_id = all_turns["metadatas"][0].get("conversation_id")
        turn_hits = rag.retrieve_turns(query="test", k=3, conversation_id=conv_id)
        result.details = f"Retrieved {len(turn_hits)} turns from conversation {conv_id[:8]}"
        result.passed = len(turn_hits) > 0
        
    except Exception as e:
        result.error = str(e)
    return result


async def test_prompt_building():
    """Test full prompt building with RAG."""
    result = TestResult("Prompt Building")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        # Get a real conversation ID
        all_turns = rag.col.get(where={"type": "turn"}, limit=1, include=["metadatas"])
        conv_id = all_turns["metadatas"][0].get("conversation_id") if all_turns.get("metadatas") else None
        
        final_prompt, used_context = await build_prompt(
            user_prompt="tell me about web search",
            conversation_id=conv_id,
            entity=None,
            media_info=None,
            user_timestamp="2025-12-16T00:00:00Z",
            rag_store=rag,
            turns_k=3,
            faq_k=2,
            memory_k=2
        )
        
        # Check that context was retrieved
        has_faqs = len(used_context.get('faqs', [])) > 0
        has_turns = len(used_context.get('turns', [])) > 0
        has_persona = used_context.get('persona', {}).get('included', False)
        
        result.details = f"Persona: {has_persona}, FAQs: {len(used_context.get('faqs', []))}, Turns: {len(used_context.get('turns', []))}, Memories: {len(used_context.get('memories', []))}"
        result.passed = has_persona and (has_faqs or has_turns)
        
        if not result.passed:
            result.error = "Prompt missing expected context"
            
    except Exception as e:
        result.error = str(e)
    return result


async def test_specialist_docs_retrieval():
    """Test specialist documentation retrieval."""
    result = TestResult("Specialist Docs Retrieval")
    try:
        from brain.specialists.specialist_docs import get_relevant_specialist_docs
        
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        docs = get_relevant_specialist_docs("how do I use web search?", rag, k=2)
        result.details = f"Retrieved {len(docs)} chars of specialist docs"
        result.passed = len(docs) > 0
        
        if not result.passed:
            result.error = "No specialist docs retrieved"
            
    except Exception as e:
        result.error = str(e)
    return result


async def test_embedding_generation():
    """Test that embeddings can be generated."""
    result = TestResult("Embedding Generation")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        embeddings = rag.embedding_fn(["test query"])
        result.details = f"Generated embedding of length {len(embeddings[0])}"
        result.passed = len(embeddings) > 0 and len(embeddings[0]) > 0
        
        if not result.passed:
            result.error = "Embedding generation failed"
            
    except Exception as e:
        result.error = str(e)
    return result


async def test_query_consistency():
    """Test that multiple queries return consistent results."""
    result = TestResult("Query Consistency")
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        # Run same query twice
        query = "luna system"
        results1 = rag.retrieve_memories(query=query, k=3, entity=None)
        results2 = rag.retrieve_memories(query=query, k=3, entity=None)
        
        # Check that results are the same
        same_count = len(results1) == len(results2)
        same_content = all(r1[0] == r2[0] for r1, r2 in zip(results1, results2)) if results1 and results2 else True
        
        result.details = f"Query 1: {len(results1)} results, Query 2: {len(results2)} results"
        result.passed = same_count and same_content
        
        if not result.passed:
            result.error = "Query results inconsistent"
            
    except Exception as e:
        result.error = str(e)
    return result


async def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("PROMPT INTERFACE TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_rag_store_initialization,
        test_embedding_generation,
        test_memory_retrieval,
        test_faq_retrieval,
        test_turn_retrieval,
        test_specialist_docs_retrieval,
        test_query_consistency,
        test_prompt_building,
    ]
    
    results = []
    for test in tests:
        print(f"Running: {test.__doc__.strip()}...")
        result = await test()
        results.append(result)
        print(f"  {result}")
        print()
    
    # Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    print("=" * 60)
    print(f"SUMMARY: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
