"""Tests for prompt building functionality."""
import pytest
from brain.prompt_builder import PromptAssembler


@pytest.mark.asyncio
async def test_prompt_building(rag_store, conversation_id):
    """Test full prompt building with RAG."""
    assembler = PromptAssembler(rag_store_instance=rag_store)
    final_prompt = assembler.build_prompt(
        user_message="tell me about web search",
        conversation_id=conversation_id,
        specialists=[],
        notices=[],
        request_context={}
    )
    
    # Check that prompt was built successfully
    assert isinstance(final_prompt, str), "Prompt should be a string"
    assert len(final_prompt) > 0, "Prompt should not be empty"
    assert "tell me about web search" in final_prompt, "User message should be in prompt"
    assert len(final_prompt) > 0, "Prompt should not be empty"


@pytest.mark.asyncio
async def test_prompt_includes_user_message(rag_store):
    """Test that user message is included in prompt."""
    user_msg = "What is the meaning of life?"
    final_prompt, _ = await build_prompt(
        user_prompt=user_msg,
        conversation_id=None,
        entity=None,
        media_info=None,
        user_timestamp="2025-12-16T00:00:00Z",
        rag_store=rag_store,
        turns_k=0,
        faq_k=0,
        memory_k=0
    )
    
    assert user_msg in final_prompt, "User message should be in prompt"
