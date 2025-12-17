"""Tests for PromptAssembler - orchestrates prompt building.

PromptAssembler is the top-level coordinator that:
- Uses ContextRetriever to fetch RAG data
- Uses SectionBuilder to format sections
- Coordinates specialist activation and integration
- Assembles complete prompts in correct order
"""
import pytest
from unittest.mock import Mock, MagicMock

from brain.prompt_builder.prompt_assembler import PromptAssembler
from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.section_builder import SectionBuilder


class TestPromptAssemblerInitialization:
    """Test PromptAssembler initialization and setup."""
    
    def test_creates_with_dependencies(self):
        """PromptAssembler initializes with retriever and builder."""
        retriever = Mock(spec=ContextRetriever)
        builder = Mock(spec=SectionBuilder)
        
        assembler = PromptAssembler(retriever, builder)
        
        assert assembler is not None
        assert assembler.retriever == retriever
        assert assembler.builder == builder
    
    def test_creates_with_defaults(self):
        """PromptAssembler can create default dependencies."""
        assembler = PromptAssembler()
        
        assert assembler is not None
        assert isinstance(assembler.retriever, ContextRetriever)
        assert isinstance(assembler.builder, SectionBuilder)


class TestBasicPromptBuilding:
    """Test basic prompt assembly without specialists."""
    
    def test_builds_minimal_prompt(self, mock_retriever, mock_builder):
        """Assembles prompt with just user message."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        # Configure mocks
        mock_retriever.get_persona.return_value = "I am Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        
        mock_builder.format_persona.return_value = "# Ada's Persona\n\nI am Ada"
        mock_builder.format_memories.return_value = "# Memories\n\nNone"
        mock_builder.format_faqs.return_value = "# FAQs\n\nNone"
        mock_builder.format_conversation_history.return_value = "# Recent\n\nNone"
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="Hello!",
            conversation_id="test-123"
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert "Hello!" in result
        assert "Ada" in result
    
    def test_sections_in_correct_order(self, mock_retriever, mock_builder):
        """Sections appear in priority order: notices > persona > memories > history."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        # Configure mocks with distinct markers
        mock_retriever.get_persona.return_value = "PERSONA"
        mock_retriever.get_memories.return_value = ["MEMORY"]
        mock_retriever.get_faqs.return_value = ["FAQ"]
        mock_retriever.get_turns.return_value = [{"role": "user", "content": "TURN"}]
        mock_retriever.get_summaries.return_value = []
        
        mock_builder.format_persona.return_value = "SECTION_PERSONA"
        mock_builder.format_memories.return_value = "SECTION_MEMORIES"
        mock_builder.format_faqs.return_value = "SECTION_FAQS"
        mock_builder.format_conversation_history.return_value = "SECTION_HISTORY"
        mock_builder.format_notices.return_value = "SECTION_NOTICES"
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="Test",
            conversation_id="test"
        )
        
        # Check ordering by finding indices
        notices_idx = result.find("SECTION_NOTICES")
        persona_idx = result.find("SECTION_PERSONA")
        memories_idx = result.find("SECTION_MEMORIES")
        history_idx = result.find("SECTION_HISTORY")
        
        assert notices_idx < persona_idx < memories_idx < history_idx


class TestConversationContext:
    """Test conversation history and turn management."""
    
    def test_includes_conversation_history(self, mock_retriever, mock_builder):
        """Recent conversation turns are included."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        turns = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        mock_retriever.get_turns.return_value = turns
        mock_builder.format_conversation_history.return_value = "# History\n\nUser: Previous question\nAda: Previous answer"
        
        # Other mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "# Persona\n\nAda"
        mock_builder.format_memories.return_value = ""
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="New question",
            conversation_id="conv-123"
        )
        
        assert "Previous question" in result
        assert "Previous answer" in result


class TestRAGContextIntegration:
    """Test RAG context retrieval and integration."""
    
    def test_retrieves_relevant_memories(self, mock_retriever, mock_builder):
        """Memories are retrieved based on query relevance."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        user_message = "What's my favorite color?"
        mock_retriever.get_memories.return_value = ["User likes blue"]
        mock_builder.format_memories.return_value = "# Memories\n\n1. User likes blue"
        
        # Other mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "# Persona\n\nAda"
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_conversation_history.return_value = ""
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message=user_message,
            conversation_id="test"
        )
        
        # Verify query was passed to retriever
        mock_retriever.get_memories.assert_called_once()
        assert "blue" in result


class TestSpecialistIntegration:
    """Test specialist activation and result integration."""
    
    def test_activates_specialists(self, mock_retriever, mock_builder):
        """Specialists are activated based on context."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        # Mock specialist
        specialist = Mock()
        specialist.capability.name = "TestSpecialist"
        specialist.should_activate.return_value = True
        specialist.process.return_value = "Specialist result"
        
        # Setup mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "# Persona\n\nAda"
        mock_builder.format_memories.return_value = ""
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_conversation_history.return_value = ""
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = "# Specialist\n\nTestSpecialist: Specialist result"
        
        result = assembler.build_prompt(
            user_message="Test",
            conversation_id="test",
            specialists=[specialist]
        )
        
        # Verify specialist was checked and processed
        specialist.should_activate.assert_called_once()
        specialist.process.assert_called_once()
        assert "Specialist result" in result
    
    def test_skips_inactive_specialists(self, mock_retriever, mock_builder):
        """Specialists that shouldn't activate are skipped."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        specialist = Mock()
        specialist.capability.name = "InactiveSpecialist"
        specialist.should_activate.return_value = False
        
        # Setup mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "# Persona\n\nAda"
        mock_builder.format_memories.return_value = ""
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_conversation_history.return_value = ""
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="Test",
            conversation_id="test",
            specialists=[specialist]
        )
        
        # Verify specialist was checked but not processed
        specialist.should_activate.assert_called_once()
        specialist.process.assert_not_called()


class TestSystemNotices:
    """Test system notices handling."""
    
    def test_includes_active_notices(self, mock_retriever, mock_builder):
        """Active system notices appear at top of prompt."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        notices = [{"message": "Low disk space", "level": "warning"}]
        
        # Setup mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "PERSONA_SECTION"
        mock_builder.format_memories.return_value = ""
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_conversation_history.return_value = ""
        mock_builder.format_notices.return_value = "NOTICES_SECTION"
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="Test",
            conversation_id="test",
            notices=notices
        )
        
        # Notices should appear before persona
        notices_idx = result.find("NOTICES_SECTION")
        persona_idx = result.find("PERSONA_SECTION")
        assert notices_idx < persona_idx


class TestPromptStructure:
    """Test overall prompt structure and formatting."""
    
    def test_user_message_at_end(self, mock_retriever, mock_builder):
        """User message appears at the end as the instruction."""
        assembler = PromptAssembler(mock_retriever, mock_builder)
        
        # Minimal mocks
        mock_retriever.get_persona.return_value = "Ada"
        mock_retriever.get_memories.return_value = []
        mock_retriever.get_faqs.return_value = []
        mock_retriever.get_turns.return_value = []
        mock_retriever.get_summaries.return_value = []
        mock_builder.format_persona.return_value = "CONTEXT"
        mock_builder.format_memories.return_value = ""
        mock_builder.format_faqs.return_value = ""
        mock_builder.format_conversation_history.return_value = ""
        mock_builder.format_notices.return_value = None
        mock_builder.format_specialist_results.return_value = None
        
        result = assembler.build_prompt(
            user_message="FINAL_MESSAGE",
            conversation_id="test"
        )
        
        # User message should be at/near the end
        lines = result.strip().split("\n")
        last_section = "\n".join(lines[-5:])  # Last 5 lines as text
        assert "FINAL_MESSAGE" in last_section


# Fixtures
@pytest.fixture
def mock_retriever():
    """Create mock ContextRetriever."""
    return Mock(spec=ContextRetriever)


@pytest.fixture
def mock_builder():
    """Create mock SectionBuilder."""
    return Mock(spec=SectionBuilder)
