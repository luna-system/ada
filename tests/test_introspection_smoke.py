"""Smoke test: Verify the full ada-chat → ada-brain pipeline works.

This test simulates what happens when a user types "find a task" in ada-chat
and it gets sent to ada-brain's /v1/chat/stream endpoint.
"""

import json
from unittest.mock import MagicMock, patch


def test_chat_stream_receives_specialist_enabled_request():
    """Simulate the full flow: ada-chat → brain chat endpoint → specialist activation."""
    
    # This test documents what happens in the real flow
    # without needing to run the full server
    
    # 1. Ada-chat sends a request like this
    chat_request = {
        "prompt": "find a task we can work on",
        "message": "find a task we can work on",
        "conversation_id": "test-123",
        "entity": None,
        "save_memory": False,
    }
    
    # 2. Brain's chat_stream_v1 receives it and extracts user_message
    user_message = chat_request.get('message', '').strip()
    assert user_message == "find a task we can work on"
    
    # 3. request_context is built with 'message' field
    request_context = {
        'entity': chat_request.get('entity'),
        'media': None,
        'ocr_context': None,
        'message': user_message,  # THIS IS THE KEY FIELD
    }
    
    # 4. All specialists are loaded
    from brain.specialists import list_specialists
    all_specialists = list_specialists()
    
    assert len(all_specialists) > 0, "Should have some specialists"
    
    # 5. Find our workspace introspection specialist
    from brain.specialists import get_specialist
    introspection_specialist = get_specialist("workspace_introspection")
    assert introspection_specialist is not None
    
    # 6. Check if it would activate for this message
    should_activate = introspection_specialist.should_activate(request_context)
    assert should_activate, "Specialist should activate for 'find a task' query"
    
    # 7. Verify other specialists don't activate (no media/ocr)
    ocr_specialist = get_specialist("ocr")
    if ocr_specialist:
        assert not ocr_specialist.should_activate(request_context), \
            "OCR specialist should NOT activate (no image)"


def test_specialist_activation_chain():
    """Test the specialist activation chain in PromptAssembler."""
    from brain.prompt_builder.prompt_assembler import PromptAssembler
    from brain.specialists import list_specialists
    
    # Mock RAG store
    mock_rag_store = MagicMock()
    
    assembler = PromptAssembler(rag_store_instance=mock_rag_store)
    all_specialists = list_specialists()
    
    # Simulate what happens in build_prompt
    user_message = "find a task we can work on"
    request_context = {"message": user_message}
    
    # This calls _activate_specialists_parallel internally
    prompt = assembler.build_prompt(
        user_message=user_message,
        conversation_id="test-123",
        specialists=all_specialists,
        request_context=request_context
    )
    
    # Should produce a non-empty prompt
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    
    # The prompt should be ready to send to Ollama LLM
    assert "User:" in prompt or "Assistant:" in prompt or len(prompt) > 10


def test_metadata_extraction_pattern():
    """Verify that response metadata can be extracted for VSCode display."""
    import re
    
    # Example response from specialist
    response = """Based on workspace analysis:

🔍 **Workspace Introspection Analysis**
📂 Files Analyzed: context.md, codebase-map.json, GOTCHAS.md, TODO.md, CONVENTIONS.md
⏱️ Analysis Time: 42ms

**Current State:**
- 42 modules documented
- 2 major optimization opportunities in v2.10
- 3 pending research tasks in docs/

**Recommendations:**
1. Complete Phase 2D optimization (memory-aware caching)
2. Document new streaming patterns for V3
3. Add more test coverage for edge cases

You could work on any of these areas!"""
    
    # Pattern for ada-chat MetadataParser
    files_pattern = r"📂 Files Analyzed:([^\n]+)"
    time_pattern = r"⏱️\s+Analysis Time:\s+(\d+)ms"
    
    files_match = re.search(files_pattern, response)
    time_match = re.search(time_pattern, response)
    
    assert files_match is not None, "Should find files marker"
    assert time_match is not None, "Should find time marker"
    
    files_text = files_match.group(1).strip()
    time_ms = int(time_match.group(1))
    
    assert "context.md" in files_text
    assert "codebase-map.json" in files_text
    assert time_ms == 42


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
