"""
Prompt assembly and context building for Ada brain.

Combines persona, memories, FAQs, recent turns, and other context into a coherent prompt.
"""
import datetime
from typing import Dict, Any, List, Optional, Tuple
from config import (
    IDENTITY_BLOCK,
    RAG_ENABLE_PERSONA,
    RAG_ENABLE_FAQ,
    RAG_ENABLE_MEMORY,
    RAG_ENABLE_SUMMARY,
    RAG_ENABLE_TURN,
    RAG_TURN_TOP_K,
    RAG_FAQ_TOP_K,
    RAG_MEMORY_TOP_K,
    RAG_SUMMARY_TOP_K,
    PERSONA_MAX_CHARS,
)
from rag_store import RagStore
from media import format_media_for_prompt
from notices_client import get_active_notices


def build_prompt(
    user_prompt: str,
    conversation_id: Optional[str],
    entity: Optional[str],
    media_info: Optional[Dict[str, Any]],
    user_timestamp: str,
    rag_store: Optional[RagStore],
    turns_k: Optional[int] = None,
    faq_k: Optional[int] = None,
    memory_k: Optional[int] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Assemble a complete prompt from all available context.
    
    Returns: (final_prompt, used_context)
    
    used_context tracks what was actually included for debugging/logging.
    """
    turns_k = turns_k or RAG_TURN_TOP_K
    faq_k = faq_k or RAG_FAQ_TOP_K
    memory_k = memory_k or RAG_MEMORY_TOP_K
    
    sections: List[str] = []

    # --- System Notices Injection ---
    notices = get_active_notices()
    if notices:
        # Only show up to 3, truncate message to 200 chars each
        notice_lines = []
        for n in notices[:3]:
            msg = n['message'][:200] + ("..." if len(n['message']) > 200 else "")
            severity_label = n['severity'].upper()
            notice_lines.append(f"⚠️ {severity_label} ALERT [{n['component']}.{n['code']}]: {msg}")
        sections.append("🔔 SYSTEM NOTICES — Acknowledge these immediately before responding to the user:\n" + "\n".join(notice_lines))
    used_context: Dict[str, Any] = {
        'persona': None,
        'faqs': [],
        'memories': [],
        'turns': [],
        'summaries': [],
        'entity': entity,
        'media': None,
    }
    
    # Always include identity guardrail
    sections.append(IDENTITY_BLOCK)
    
    # Media (ListenBrainz) if provided
    if media_info and isinstance(media_info, dict):
        media_line = format_media_for_prompt(media_info)
        if media_line:
            sections.append(media_line)
            used_context['media'] = media_info
    
    # Persona block
    if RAG_ENABLE_PERSONA and rag_store is not None:
        persona_doc = rag_store.load_persona_block()
        if persona_doc:
            if isinstance(persona_doc, tuple):
                p_text, p_meta = persona_doc
            else:
                p_text, p_meta = str(persona_doc), {}
            short_persona = p_text if len(p_text) <= PERSONA_MAX_CHARS else p_text[:PERSONA_MAX_CHARS]
            sections.append("Persona and style guidelines (global):\n" + short_persona)
            used_context['persona'] = {
                'included': True,
                'version': (p_meta or {}).get('version'),
                'timestamp': (p_meta or {}).get('timestamp'),
            }
        else:
            used_context['persona'] = {'included': False}
    
    # Long-term memory
    if RAG_ENABLE_MEMORY and rag_store is not None and memory_k > 0:
        mem_hits = rag_store.retrieve_memories(query=user_prompt, k=memory_k, entity=entity)
        if mem_hits:
            mem_lines = []
            for text_m, meta_m in mem_hits:
                imp = (meta_m or {}).get('importance')
                scope = (meta_m or {}).get('scope', 'global')
                tag_str = ''
                tags = (meta_m or {}).get('tags')
                if isinstance(tags, list) and tags:
                    tag_str = f" tags={','.join(tags)}"
                if imp is not None:
                    mem_lines.append(f"- ({scope}, importance={imp}{tag_str}) {text_m}")
                else:
                    mem_lines.append(f"- ({scope}{tag_str}) {text_m}")
                used_context['memories'].append(text_m)
            sections.append("Long-term memory:\n" + "\n".join(mem_lines))
    
    # FAQs/reference
    if RAG_ENABLE_FAQ and rag_store is not None and faq_k > 0:
        faq_hits = rag_store.retrieve_faqs(query=user_prompt, k=faq_k)
        if faq_hits:
            faq_lines = []
            for text, meta in faq_hits:
                topic = (meta or {}).get('topic', 'faq')
                faq_lines.append(f"- ({topic}) {text}")
                used_context['faqs'].append(text)
            sections.append("Reference snippets (FAQs):\n" + "\n".join(faq_lines))
    
    # Conversation turns
    if RAG_ENABLE_TURN and rag_store is not None and turns_k > 0:
        hits = rag_store.retrieve_turns(query=user_prompt, k=turns_k, conversation_id=conversation_id)
        if hits:
            turn_lines = []
            for text, meta in hits:
                role = (meta or {}).get('role', 'context')
                ts = (meta or {}).get('timestamp')
                if ts:
                    turn_lines.append(f"- {role} [{ts}]: {text}")
                else:
                    turn_lines.append(f"- {role}: {text}")
                used_context['turns'].append(text)
            sections.append("Recent conversation turns (most relevant first):\n" + "\n".join(turn_lines))
    
    # Conversation summaries
    if RAG_ENABLE_SUMMARY and rag_store is not None and conversation_id:
        sum_hits = rag_store.retrieve_summaries(conversation_id=conversation_id, k=RAG_SUMMARY_TOP_K)
        if sum_hits:
            used_context['summaries'] = [t for t, _ in sum_hits]
            sections.append("Conversation summaries:\n" + "\n".join(f"- {t}" for t, _ in sum_hits))
    
    # Instructions and reminders
    instructions = (
        "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
        "conversation memory when relevant. If the user asks about times or durations, use the provided "
        "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
    )
    reminder = "Reminder: You are Ada, Luna's assistant. Always identify as Ada."
    current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
    
    # Assemble final prompt
    assembled = ("\n\n".join(sections) + "\n\n" if sections else "") + instructions + "\n" + reminder + "\n" + current_ts_line
    final_prompt = f"{assembled}\nUser: {user_prompt}\nAssistant:"
    
    return final_prompt, used_context
