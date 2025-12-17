"""
Prompt assembly and context building for Ada brain.

This module provides backward-compatible build_prompt() function that now uses
the new modular prompt_builder package internally.

Migration path:
- Old: Monolithic build_prompt() function in this file
- New: Modular components in brain/prompt_builder/ package
- This file: Compatibility shim for existing code

Eventually this file can be removed once all callers migrate to new API.
"""
# @ai-indexable: core-functionality-legacy
# @ai-purpose: Backward-compatible shim for old build_prompt() API
# @ai-migration-target: brain/prompt_builder/ package
# @ai-note: New code should import from brain.prompt_builder package directly

import asyncio
import datetime
import logging
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

from brain.config import (
    SYSTEM_PROMPT,
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
    SPECIALIST_RAG_DOCS,
    AI_NAME,
    AI_USER_NAME,
)
from brain.rag_store import RagStore
from brain.media import format_media_for_prompt
from brain.notices_client import get_active_notices
from brain.specialists import execute_specialists
from brain.specialists.specialist_docs import get_relevant_specialist_docs

# Import new modular components
from brain.prompt_builder import ContextRetriever, SectionBuilder, PromptAssembler

if TYPE_CHECKING:
    from brain.token_monitor import TokenBudgetMonitor

logger = logging.getLogger(__name__)


async def build_prompt(
    user_prompt: str,
    conversation_id: Optional[str],
    entity: Optional[str],
    media_info: Optional[Dict[str, Any]],
    user_timestamp: str,
    rag_store: Optional[RagStore],
    turns_k: Optional[int] = None,
    faq_k: Optional[int] = None,
    memory_k: Optional[int] = None,
    ocr_context: Optional[Dict[str, Any]] = None,
    token_monitor: Optional['TokenBudgetMonitor'] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Assemble a complete prompt from all available context.
    
    This is a LEGACY compatibility shim. New code should use the modular
    brain.prompt_builder package directly.
    
    Migration in progress: This function now uses ContextRetriever,
    SectionBuilder, and PromptAssembler internally, but maintains the
    original API for backward compatibility.
    
    Returns: (final_prompt, used_context)
    
    used_context tracks what was actually included for debugging/logging.
    """
    turns_k = turns_k or RAG_TURN_TOP_K
    faq_k = faq_k or RAG_FAQ_TOP_K
    memory_k = memory_k or RAG_MEMORY_TOP_K
    
    sections: List[str] = []
    used_context: Dict[str, Any] = {
        'persona': None,
        'faqs': [],
        'memories': [],
        'turns': [],
        'summaries': [],
        'entity': entity,
        'media': None,
    }

    # --- System Notices Injection ---
    notices = get_active_notices()
    if notices:
        # Only show up to 3, truncate message to 200 chars each
        notice_lines = []
        for n in notices[:3]:
            msg = n['message'][:200] + ("..." if len(n['message']) > 200 else "")
            severity_label = n['severity'].upper()
            notice_lines.append(f"⚠️ {severity_label} ALERT [{n['component']}.{n['code']}]: {msg}")
        notice_section = "🔔 SYSTEM NOTICES — Acknowledge these immediately before responding to the user:\n" + "\n".join(notice_lines)
        sections.append(notice_section)
        if token_monitor:
            token_monitor.track("system_notices", notice_section)
    
    # Always include system prompt (identity)
    sections.append(SYSTEM_PROMPT)
    if token_monitor:
        token_monitor.track("system_prompt", SYSTEM_PROMPT)
    
    # --- Dynamic Specialist Documentation (RAG-based) ---
    if SPECIALIST_RAG_DOCS and rag_store is not None:
        specialist_docs = get_relevant_specialist_docs(user_prompt, rag_store, k=2)
        if specialist_docs:
            sections.append(specialist_docs)
            used_context['specialist_docs'] = True
            if token_monitor:
                token_monitor.track("specialist_docs", specialist_docs)
    
    # --- Execute Specialist Plugins ---
    request_context = {
        'prompt': user_prompt,
        'conversation_id': conversation_id,
        'entity': entity,
        'media': media_info,
        'ocr_context': ocr_context,
        'user_timestamp': user_timestamp,
    }
    
    try:
        specialist_results = await execute_specialists(request_context)
        
        for result in specialist_results:
            if result.success and result.context_text:
                sections.append(result.context_text)
                
                if token_monitor:
                    token_monitor.track(f"specialist_{result.specialist_name}", result.context_text)
                
                specialist_name = result.specialist_name
                if specialist_name not in used_context:
                    used_context[specialist_name] = []
                used_context[specialist_name].append({
                    'success': True,
                    'metadata': result.metadata
                })
            elif not result.success:
                logger.warning(f"Specialist {result.specialist_name} failed: {result.error}")
    
    except Exception as e:
        logger.error(f"Specialist execution failed: {e}", exc_info=True)
    
    # --- RAG Context (using new components) ---
    if rag_store is not None:
        # Use ContextRetriever to get RAG data
        retriever = ContextRetriever(rag_store=rag_store, config=None)
        
        # Persona
        if RAG_ENABLE_PERSONA:
            persona_doc = retriever.get_persona()
            if persona_doc:
                short_persona = persona_doc if len(persona_doc) <= PERSONA_MAX_CHARS else persona_doc[:PERSONA_MAX_CHARS]
                persona_section = "Persona and style guidelines (global):\n" + short_persona
                sections.append(persona_section)
                if token_monitor:
                    token_monitor.track("persona", persona_section)
                used_context['persona'] = {'included': True}
        
        # Memories
        if RAG_ENABLE_MEMORY and memory_k > 0:
            mem_hits = retriever.get_memories(query=user_prompt, k=memory_k, entity=entity)
            if mem_hits:
                mem_lines = []
                for mem_dict in mem_hits:
                    text_m = mem_dict.get('text', '')
                    meta_m = mem_dict.get('metadata', {})
                    imp = meta_m.get('importance')
                    scope = meta_m.get('scope', 'global')
                    tag_str = ''
                    tags = meta_m.get('tags')
                    if isinstance(tags, list) and tags:
                        tag_str = f" tags={','.join(tags)}"
                    if imp is not None:
                        mem_lines.append(f"- ({scope}, importance={imp}{tag_str}) {text_m}")
                    else:
                        mem_lines.append(f"- ({scope}{tag_str}) {text_m}")
                    used_context['memories'].append(text_m)
                memory_section = "Long-term memory:\n" + "\n".join(mem_lines)
                sections.append(memory_section)
                if token_monitor:
                    token_monitor.track("memories", memory_section)
        
        # FAQs
        if RAG_ENABLE_FAQ and faq_k > 0:
            faq_hits = retriever.get_faqs(query=user_prompt, k=faq_k)
            if faq_hits:
                faq_lines = []
                for faq_dict in faq_hits:
                    text = faq_dict.get('text', '')
                    meta = faq_dict.get('metadata', {})
                    topic = meta.get('topic', 'faq')
                    faq_lines.append(f"- ({topic}) {text}")
                    used_context['faqs'].append(text)
                faq_section = "Reference snippets (FAQs):\n" + "\n".join(faq_lines)
                sections.append(faq_section)
                if token_monitor:
                    token_monitor.track("faqs", faq_section)
        
        # Conversation turns
        if RAG_ENABLE_TURN and turns_k > 0:
            turn_hits = retriever.get_turns(conversation_id=conversation_id, k=turns_k, query=user_prompt)
            if turn_hits:
                turn_lines = []
                for turn_dict in turn_hits:
                    text = turn_dict.get('text', '')
                    meta = turn_dict.get('metadata', {})
                    role = meta.get('role', 'context')
                    ts = meta.get('timestamp')
                    if ts:
                        turn_lines.append(f"- {role} [{ts}]: {text}")
                    else:
                        turn_lines.append(f"- {role}: {text}")
                    used_context['turns'].append(text)
                turn_section = "Recent conversation turns (most relevant first):\n" + "\n".join(turn_lines)
                sections.append(turn_section)
                if token_monitor:
                    token_monitor.track("turns", turn_section)
        
        # Summaries
        if RAG_ENABLE_SUMMARY and conversation_id:
            sum_hits = retriever.get_summaries(conversation_id=conversation_id, k=RAG_SUMMARY_TOP_K)
            if sum_hits:
                sum_texts = [s.get('text', '') for s in sum_hits]
                used_context['summaries'] = sum_texts
                summary_section = "Conversation summaries:\n" + "\n".join(f"- {t}" for t in sum_texts)
                sections.append(summary_section)
                if token_monitor:
                    token_monitor.track("summaries", summary_section)
    
    # Instructions and reminders
    instructions = (
        "You are a helpful assistant. Follow the persona and policies above. Use the reference snippets and "
        "conversation memory when relevant. If the user asks about times or durations, use the provided "
        "UTC ISO timestamps to compute precise differences and express them in human-friendly units."
    )
    reminder = f"Reminder: You are {AI_NAME}, {AI_USER_NAME}'s assistant. Always identify as {AI_NAME}."
    current_ts_line = f"Current user message timestamp (UTC): {user_timestamp}"
    
    # Assemble final prompt
    assembled = ("\n\n".join(sections) + "\n\n" if sections else "") + instructions + "\n" + reminder + "\n" + current_ts_line
    
    if token_monitor:
        token_monitor.track("instructions", instructions + "\n" + reminder + "\n" + current_ts_line)
        token_monitor.track("user_prompt", user_prompt)
    
    final_prompt = f"{assembled}\nUser: {user_prompt}\nAssistant:"
    
    return final_prompt, used_context
