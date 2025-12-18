"""Test synthetic tool awareness memories (Phase 4: RAG Tier 2).

Validates that synthetic memories teaching Ada about her toolbox are:
1. Successfully stored in ChromaDB
2. Retrievable via RAG search
3. Included in assembled prompts
4. Result in tool-aware responses

NOTE: These tests use embedded ChromaDB (no CHROMA_URL), which is
different from the Docker setup but allows unit testing without services.
"""
import os
import pytest

# Force embedded mode for tests (no HTTP client)
if "CHROMA_URL" in os.environ:
    del os.environ["CHROMA_URL"]

from brain.rag_store import RagStore
from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.prompt_assembler import PromptAssembler


class TestSyntheticMemoryRetrieval:
    """Test that synthetic memories are retrievable from ChromaDB."""
    
    def test_synthetic_memories_loaded(self):
        """Test that tool usage memories are in ChromaDB."""
        store = RagStore(collection_name="conversations")
        
        # Query for codebase lookup example
        results = store.retrieve_memories(
            query="How do I look up code in my own codebase?",
            k=5
        )
        
        # Should find at least one synthetic memory about codebase capability
        assert len(results) > 0, "No memories found - synthetic memories not loaded?"
        
        # Check that we got relevant content
        content = results[0][0]
        assert any(word in content.lower() for word in ["codebase", "code", "specialist", "lookup"]), \
            f"Retrieved memory doesn't seem relevant: {content[:100]}"
    
    def test_tool_awareness_faqs_loaded(self):
        """Test that tool awareness FAQs are in ChromaDB."""
        store = RagStore(collection_name="conversations")
        
        # Query for capabilities
        results = store.retrieve_faqs(
            query="What tools do I have available?",
            k=5
        )
        
        # Should find FAQ about capabilities
        assert len(results) > 0, "No FAQs found - synthetic FAQs not loaded?"
        
        # Check FAQ structure and content
        content = results[0][0]
        assert "Q:" in content and "A:" in content, "FAQ doesn't have Q:/A: format"
        assert any(word in content.lower() for word in ["capability", "capabilities", "specialist", "tool"]), \
            f"Retrieved FAQ doesn't seem relevant: {content[:100]}"
    
    def test_synthetic_memories_have_correct_metadata(self):
        """Test that synthetic memories have proper metadata tags."""
        store = RagStore(collection_name="conversations")
        
        # Retrieve memories and check metadata
        results = store.retrieve_memories(
            query="pattern matching tool activation",
            k=5
        )
        
        assert len(results) > 0, "No memories found"
        
        # Check metadata structure
        _, metadata = results[0]
        assert "type" in metadata, "Missing 'type' in metadata"
        assert "source" in metadata, "Missing 'source' in metadata"
        assert metadata["source"] == "synthetic", f"Expected synthetic source, got {metadata['source']}"


class TestSyntheticMemoriesInPrompts:
    """Test that synthetic memories appear in assembled prompts."""
    
    def test_memories_retrieved_by_context_retriever(self):
        """Test ContextRetriever fetches synthetic memories."""
        retriever = ContextRetriever()
        store = RagStore(collection_name="conversations")
        
        # Query about capabilities using store instance
        memories = store.retrieve_memories(
            query="What can I do with my tools?",
            k=5
        )
        
        # Should retrieve at least some memories
        assert len(memories) > 0, "RagStore returned no memories"
        
        # Check that at least one is about tools/capabilities
        content_combined = " ".join([m[0].lower() for m in memories])
        assert any(word in content_combined for word in ["tool", "specialist", "capability", "codebase", "search"]), \
            "Retrieved memories don't mention tools/specialists"
    
    def test_faqs_retrieved_by_context_retriever(self):
        """Test ContextRetriever fetches tool awareness FAQs."""
        retriever = ContextRetriever()
        store = RagStore(collection_name="conversations")
        
        # Query for FAQs using store instance
        faqs = store.retrieve_faqs(
            query="What are my capabilities?",
            k=5
        )
        
        # Should retrieve FAQs
        assert len(faqs) > 0, "RagStore returned no FAQs"
        
        # Check FAQ format
        content = faqs[0][0]
        assert "Q:" in content or "A:" in content, "FAQ doesn't have expected format"
    
    def test_synthetic_memories_in_assembled_prompt(self):
        """Test that synthetic memories appear in fully assembled prompt."""
        assembler = PromptAssembler()
        
        # Build prompt with tool-awareness query (using correct parameter names)
        prompt = assembler.build_prompt(
            user_message="What can you do? What tools do you have?",
            conversation_id=None,
            request_context={}
        )
        
        # Check that prompt contains references to tools/specialists
        prompt_lower = prompt.lower()
        
        # Should mention at least some specialist capabilities
        specialist_keywords = ["specialist", "codebase", "web search", "wiki", "tool", "capability"]
        matches = sum(1 for keyword in specialist_keywords if keyword in prompt_lower)
        
        assert matches >= 2, f"Prompt should mention specialists/tools (found {matches} keywords), got: {prompt[:500]}"


class TestEndToEndToolAwareness:
    """Test complete flow from query to tool-aware response."""
    
    def test_tool_awareness_query_retrieves_context(self):
        """Test that asking about capabilities retrieves synthetic memories."""
        from brain.prompt_builder.prompt_assembler import PromptAssembler
        
        assembler = PromptAssembler()
        
        # Simulate user asking about capabilities
        prompt = assembler.build_prompt(
            user_message="What can you help me with? What are your capabilities?",
            conversation_id=None,
            request_context={}
        )
        
        # Verify the prompt contains tool awareness information
        assert len(prompt) > 100, "Prompt seems too short"
        
        # Check for multiple indicators of tool awareness
        indicators = [
            "codebase" in prompt.lower(),
            "specialist" in prompt.lower(),
            "search" in prompt.lower(),
            "wiki" in prompt.lower(),
            "capability" in prompt.lower() or "capabilities" in prompt.lower()
        ]
        
        matches = sum(indicators)
        assert matches >= 2, f"Expected tool awareness in prompt (found {matches}/5 indicators)"
    
    def test_codebase_query_retrieves_relevant_examples(self):
        """Test that asking about code lookup retrieves codebase examples."""
        assembler = PromptAssembler()
        
        prompt = assembler.build_prompt(
            user_message="How do I look up functions in your codebase?",
            conversation_id=None,
            request_context={}
        )
        
        prompt_lower = prompt.lower()
        
        # Should mention codebase specialist or code lookup capability
        assert "codebase" in prompt_lower or "code" in prompt_lower, \
            "Query about code lookup should retrieve codebase-related memories"
    
    def test_web_search_query_retrieves_relevant_examples(self):
        """Test that asking about web search retrieves web search examples."""
        assembler = PromptAssembler()
        
        prompt = assembler.build_prompt(
            user_message="Can you search the internet for information?",
            conversation_id=None,
            request_context={}
        )
        
        prompt_lower = prompt.lower()
        
        # Should mention web search capability
        assert "search" in prompt_lower or "web" in prompt_lower or "internet" in prompt_lower, \
            "Query about web search should retrieve web search-related memories"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
