"""SectionBuilder - formats RAG context into structured prompt sections.

This component takes raw context data (lists of memories, FAQs, conversation
turns, etc.) and formats them into well-structured prompt sections with
consistent headers, formatting, and organization.
"""
# @ai-indexable: core-component
# @ai-purpose: Format RAG context into structured prompt sections
# @ai-dependencies: none (pure formatting logic)

from typing import Any


class SectionBuilder:
    """Formats context data into structured prompt sections.
    
    Each method produces a formatted section with:
    - Clear section header
    - Consistent formatting
    - Appropriate handling of empty data
    """
    
    def format_persona(self, persona_text: str | None) -> str:
        """Format persona text with header.
        
        Args:
            persona_text: Raw persona description (can be None)
            
        Returns:
            Formatted persona section with header, or empty string if None
        """
        if not persona_text:
            return ""
        header = "# Ada's Persona\n\n"
        return header + persona_text
    
    def format_memories(self, memories: list[str]) -> str:
        """Format memories as numbered list.
        
        Args:
            memories: List of memory strings
            
        Returns:
            Formatted memories section
        """
        header = "# Relevant Memories\n\n"
        
        if not memories:
            return header + "None"
        
        formatted_memories = "\n".join(
            f"{i+1}. {memory}" for i, memory in enumerate(memories)
        )
        return header + formatted_memories
    
    def format_faqs(self, faqs: list[str]) -> str:
        """Format FAQs as Q&A pairs.
        
        Args:
            faqs: List of FAQ strings (Q: ... A: ... format)
            
        Returns:
            Formatted FAQs section
        """
        header = "# Frequently Asked Questions\n\n"
        
        if not faqs:
            return header + "None"
        
        # FAQs are already formatted as Q:/A: pairs
        formatted_faqs = "\n\n".join(faqs)
        return header + formatted_faqs
    
    def format_conversation_history(self, turns: list[dict[str, Any]]) -> str:
        """Format conversation history with speaker labels.
        
        Args:
            turns: List of conversation turns with role/content
            
        Returns:
            Formatted conversation history section
        """
        header = "# Recent Conversation\n\n"
        
        if not turns:
            return header + "None (start of conversation)"
        
        formatted_turns = []
        for turn in turns:
            # Handle both tuple format (text, metadata) and dict format
            if isinstance(turn, tuple):
                # New format from retrieve_turns: (text, metadata)
                content, metadata = turn
                role = (metadata or {}).get("role", "unknown")
            else:
                # Old format (backwards compatibility): dict with 'role' and 'content'
                role = turn.get("role", "unknown")
                content = turn.get("content", "")
            
            # Map role to speaker label
            speaker = "User" if role == "user" else "Ada"
            formatted_turns.append(f"{speaker}: {content}")
        
        return header + "\n".join(formatted_turns)
    
    def format_notices(self, notices: list[dict[str, Any]]) -> str | None:
        """Format system notices with urgency indication.
        
        Args:
            notices: List of notice dicts with message/level
            
        Returns:
            Formatted notices section, or None if no notices
        """
        if not notices:
            return None
        
        header = "# System Notices\n\n"
        
        formatted_notices = []
        for notice in notices:
            message = notice.get("message", "")
            level = notice.get("level", "info")
            
            # Add urgency indicator
            indicator = "⚠️" if level == "warning" else "ℹ️"
            formatted_notices.append(f"{indicator} {message}")
        
        return header + "\n".join(formatted_notices)
    
    def format_specialist_results(self, results: list[dict[str, Any]]) -> str | None:
        """Format specialist results with source attribution.
        
        Args:
            results: List of specialist result dicts
            
        Returns:
            Formatted specialist results, or None if no results
        """
        if not results:
            return None
        
        header = "# Specialist Context\n\n"
        
        formatted_results = []
        for result in results:
            specialist = result.get("specialist", "Unknown")
            content = result.get("result", "")
            
            # Format with source attribution
            formatted_results.append(f"**{specialist}:**\n{content}")
        
        return header + "\n\n".join(formatted_results)
