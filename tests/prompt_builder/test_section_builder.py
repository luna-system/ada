"""Tests for SectionBuilder - formats context into prompt sections.

SectionBuilder takes raw context data (lists, strings) and formats them
into structured prompt sections with headers, formatting, and structure.
"""
import pytest

from brain.prompt_builder.section_builder import SectionBuilder


class TestSectionBuilderInitialization:
    """Test SectionBuilder initialization."""
    
    def test_creates_instance(self):
        """SectionBuilder initializes successfully."""
        builder = SectionBuilder()
        assert builder is not None


class TestPersonaFormatting:
    """Test persona section formatting."""
    
    @pytest.mark.parametrize("persona_text,expected_start", [
        ("I am Ada, your AI assistant.", "# Ada's Persona\n\nI am Ada"),
        ("", "# Ada's Persona\n\n"),
    ])
    def test_formats_persona_section(self, persona_text, expected_start):
        """Persona text is formatted with header."""
        builder = SectionBuilder()
        result = builder.format_persona(persona_text)
        assert result.startswith(expected_start)


class TestMemoriesFormatting:
    """Test memories section formatting."""
    
    def test_formats_memories_list(self):
        """Memories are formatted as numbered list."""
        builder = SectionBuilder()
        memories = [
            "User prefers coffee",
            "User is learning Python"
        ]
        result = builder.format_memories(memories)
        
        assert "# Relevant Memories" in result
        assert "1. User prefers coffee" in result
        assert "2. User is learning Python" in result
    
    def test_formats_empty_memories(self):
        """Empty memories list produces 'None' message."""
        builder = SectionBuilder()
        result = builder.format_memories([])
        
        assert "# Relevant Memories" in result
        assert "None" in result or "No memories" in result.lower()


class TestFAQsFormatting:
    """Test FAQs section formatting."""
    
    def test_formats_faqs_list(self):
        """FAQs are formatted as Q&A pairs."""
        builder = SectionBuilder()
        faqs = [
            "Q: What is Ada?\nA: A privacy-first AI assistant.",
            "Q: How do I update?\nA: Run git pull."
        ]
        result = builder.format_faqs(faqs)
        
        assert "# Frequently Asked Questions" in result or "# FAQs" in result
        assert "What is Ada?" in result
        assert "privacy-first" in result
    
    def test_formats_empty_faqs(self):
        """Empty FAQs list produces appropriate message."""
        builder = SectionBuilder()
        result = builder.format_faqs([])
        
        assert "Frequently Asked Questions" in result or "FAQ" in result
        assert "None" in result or "no faqs" in result.lower()


class TestConversationHistoryFormatting:
    """Test conversation history formatting."""
    
    def test_formats_turns_with_speaker_labels(self):
        """Conversation turns are formatted with speaker labels."""
        builder = SectionBuilder()
        turns = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        result = builder.format_conversation_history(turns)
        
        assert "# Recent Conversation" in result
        assert "User: Hello!" in result
        assert "Ada: Hi there!" in result or "Assistant: Hi there!" in result
    
    def test_formats_empty_history(self):
        """Empty conversation history produces appropriate message."""
        builder = SectionBuilder()
        result = builder.format_conversation_history([])
        
        assert "Conversation" in result
        assert "None" in result or "start of conversation" in result.lower()


class TestSystemNoticesFormatting:
    """Test system notices formatting."""
    
    def test_formats_active_notices(self):
        """Active notices are formatted with urgency."""
        builder = SectionBuilder()
        notices = [
            {"message": "Disk space low", "level": "warning"},
            {"message": "Update available", "level": "info"}
        ]
        result = builder.format_notices(notices)
        
        assert "# System Notices" in result
        assert "Disk space low" in result
        assert "Update available" in result
    
    def test_skips_empty_notices(self):
        """Empty notices list produces no section."""
        builder = SectionBuilder()
        result = builder.format_notices([])
        
        # Empty notices should return empty string or None
        assert result == "" or result is None


class TestSpecialistResultsFormatting:
    """Test specialist results formatting."""
    
    def test_formats_specialist_context(self):
        """Specialist results are formatted with source attribution."""
        builder = SectionBuilder()
        specialist_results = [
            {
                "specialist": "OCRSpecialist",
                "result": "Extracted text: Hello World"
            },
            {
                "specialist": "WebSearchSpecialist", 
                "result": "Found 3 results about Python"
            }
        ]
        result = builder.format_specialist_results(specialist_results)
        
        assert "OCR" in result or "OCRSpecialist" in result
        assert "Hello World" in result
        assert "WebSearch" in result or "WebSearchSpecialist" in result
        assert "Python" in result
    
    def test_skips_empty_specialist_results(self):
        """Empty specialist results produce no section."""
        builder = SectionBuilder()
        result = builder.format_specialist_results([])
        
        assert result == "" or result is None


class TestSectionOrdering:
    """Test that sections can be combined in correct order."""
    
    def test_all_sections_present(self):
        """All non-empty sections appear in formatted output."""
        builder = SectionBuilder()
        
        # Build a complete prompt with all sections
        sections = [
            builder.format_persona("I am Ada"),
            builder.format_memories(["User likes coffee"]),
            builder.format_faqs(["Q: What is Ada?\nA: An AI assistant"]),
            builder.format_conversation_history([
                {"role": "user", "content": "Hello"}
            ]),
            builder.format_notices([{"message": "Test", "level": "info"}]),
            builder.format_specialist_results([
                {"specialist": "Test", "result": "Result"}
            ])
        ]
        
        # Filter out None/empty sections
        sections = [s for s in sections if s]
        full_prompt = "\n\n".join(sections)
        
        assert "Persona" in full_prompt
        assert "Memories" in full_prompt
        assert "Frequently Asked Questions" in full_prompt or "FAQ" in full_prompt
        assert "Conversation" in full_prompt
        assert "Notices" in full_prompt
