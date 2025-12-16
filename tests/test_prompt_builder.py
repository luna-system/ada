"""Tests for prompt building functionality."""
import pytest
from brain.prompt_builder import build_prompt


@pytest.mark.asyncio
async def test_prompt_building(rag_store, conversation_id):
    """Test full prompt building with RAG."""
    final_prompt, used_context = await build_prompt(
        user_prompt="tell me about web search",
        conversation_id=conversation_id,
        entity=None,
        media_info=None,
        user_timestamp="2025-12-16T00:00:00Z",
        rag_store=rag_store,
        turns_k=3,
        faq_k=2,
        memory_k=2
    )
    
    # Check that context was retrieved
    has_persona = used_context.get('persona', {}).get('included', False)
    has_context = (
        len(used_context.get('faqs', [])) > 0 or 
        len(used_context.get('turns', [])) > 0
    )
    
    assert has_persona, "Prompt should include persona"
    assert has_context, "Prompt should include some context (FAQs or turns)"
    assert isinstance(final_prompt, str), "Prompt should be a string"
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
