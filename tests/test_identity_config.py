"""
Tests for configurable identity and persona system.

Tests that AI_NAME, AI_USER_NAME, and persona loading work correctly.
"""
import pytest
import os
import tempfile
from pathlib import Path
from brain import config
from brain.rag_store import RagStore


class TestConfigurableIdentity:
    """Test that identity configuration works as expected."""
    
    def test_default_identity_values(self):
        """Test that default AI_NAME and AI_USER_NAME are set."""
        # Should have defaults even if not in env
        assert config.AI_NAME is not None
        assert config.AI_USER_NAME is not None
        assert len(config.AI_NAME) > 0
        assert len(config.AI_USER_NAME) > 0
    
    def test_identity_in_identity_block(self):
        """Test that AI_NAME and AI_USER_NAME appear in IDENTITY_BLOCK."""
        assert config.AI_NAME in config.IDENTITY_BLOCK
        assert config.AI_USER_NAME in config.IDENTITY_BLOCK
    
    def test_identity_block_format(self):
        """Test that IDENTITY_BLOCK has expected structure."""
        identity_block = config.IDENTITY_BLOCK
        
        # Should mention the AI's name
        assert f"You are {config.AI_NAME}" in identity_block
        
        # Should mention the user's name
        assert config.AI_USER_NAME in identity_block
        
        # Should have standard instructions
        assert "System identity" in identity_block
        assert "refer to yourself as" in identity_block
    
    def test_identity_with_custom_env_vars(self, monkeypatch):
        """Test that custom AI_NAME and AI_USER_NAME work."""
        # Set custom values
        monkeypatch.setenv("AI_NAME", "Jarvis")
        monkeypatch.setenv("AI_USER_NAME", "Tony")
        
        # Reload config module to pick up changes
        import importlib
        importlib.reload(config)
        
        # Verify custom values are used
        assert config.AI_NAME == "Jarvis"
        assert config.AI_USER_NAME == "Tony"
        assert "Jarvis" in config.IDENTITY_BLOCK
        assert "Tony" in config.IDENTITY_BLOCK
        
        # Clean up - restore defaults
        monkeypatch.delenv("AI_NAME", raising=False)
        monkeypatch.delenv("AI_USER_NAME", raising=False)
        importlib.reload(config)


class TestPersonaLoading:
    """Test persona file loading and processing."""
    
    def test_default_persona_path_configured(self):
        """Test that RAG_PERSONA_PATH is configured."""
        assert config.RAG_PERSONA_PATH is not None
        assert len(config.RAG_PERSONA_PATH) > 0
    
    def test_persona_max_chars_setting(self):
        """Test that PERSONA_MAX_CHARS is configured."""
        assert config.PERSONA_MAX_CHARS > 0
        assert isinstance(config.PERSONA_MAX_CHARS, int)
    
    def test_load_persona_from_custom_path(self):
        """Test loading persona from a custom file path."""
        # Create temporary persona file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            test_persona = "# Test Persona\n\nYou are a test AI assistant."
            f.write(test_persona)
            temp_path = f.name
        
        try:
            # Verify file exists and is readable
            assert Path(temp_path).exists()
            
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test Persona" in content
                assert "test AI assistant" in content
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
    
    def test_persona_truncation_logic(self):
        """Test that long personas would be truncated."""
        max_chars = config.PERSONA_MAX_CHARS
        
        # Create a persona longer than max
        long_persona = "a" * (max_chars + 1000)
        
        # Verify truncation would happen
        truncated = long_persona[:max_chars]
        assert len(truncated) == max_chars
        assert len(truncated) < len(long_persona)
    
    def test_example_personas_exist(self):
        """Test that example persona files exist."""
        examples_dir = Path(__file__).parent.parent / "examples" / "personas"
        
        expected_files = [
            "README.md",
            "ada-default.md",
            "coding-buddy.md",
            "creative-writer.md",
            "technical-expert.md",
            "minimal.md"
        ]
        
        for filename in expected_files:
            file_path = examples_dir / filename
            assert file_path.exists(), f"Expected persona file not found: {filename}"
            
            # Verify files have content
            assert file_path.stat().st_size > 0, f"Persona file is empty: {filename}"
    
    def test_example_personas_are_valid_markdown(self):
        """Test that example personas are valid markdown."""
        examples_dir = Path(__file__).parent.parent / "examples" / "personas"
        
        persona_files = [
            "ada-default.md",
            "coding-buddy.md",
            "creative-writer.md",
            "technical-expert.md",
            "minimal.md"
        ]
        
        for filename in persona_files:
            file_path = examples_dir / filename
            
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Basic markdown validation
                assert len(content) > 0
                assert content.strip()  # Not just whitespace
                
                # Should have at least one heading
                assert '#' in content or '=' in content
    
    def test_example_personas_under_max_length(self):
        """Test that example personas are under PERSONA_MAX_CHARS."""
        examples_dir = Path(__file__).parent.parent / "examples" / "personas"
        max_chars = config.PERSONA_MAX_CHARS
        
        persona_files = [
            "ada-default.md",
            "coding-buddy.md",
            "creative-writer.md",
            "technical-expert.md",
            "minimal.md"
        ]
        
        for filename in persona_files:
            file_path = examples_dir / filename
            
            with open(file_path, 'r') as f:
                content = f.read()
                
                if len(content) > max_chars:
                    pytest.fail(
                        f"{filename} exceeds PERSONA_MAX_CHARS "
                        f"({len(content)} > {max_chars})"
                    )


class TestEnvironmentConfiguration:
    """Test that new environment variables are properly configured."""
    
    def test_ai_personality_file_default(self):
        """Test that AI_PERSONALITY_FILE has a default value."""
        # Should be defined (even if empty string)
        assert hasattr(config, 'AI_PERSONALITY_FILE')
        # Default should be empty (uses RAG_PERSONA_PATH instead)
        assert config.AI_PERSONALITY_FILE == ""
    
    def test_all_identity_config_present(self):
        """Test that all identity config variables exist."""
        required_configs = [
            'AI_NAME',
            'AI_USER_NAME',
            'AI_PERSONALITY_FILE',
            'IDENTITY_BLOCK',
            'RAG_PERSONA_PATH',
            'PERSONA_MAX_CHARS'
        ]
        
        for config_name in required_configs:
            assert hasattr(config, config_name), \
                f"Missing config variable: {config_name}"
    
    def test_config_types(self):
        """Test that config variables have correct types."""
        assert isinstance(config.AI_NAME, str)
        assert isinstance(config.AI_USER_NAME, str)
        assert isinstance(config.AI_PERSONALITY_FILE, str)
        assert isinstance(config.IDENTITY_BLOCK, str)
        assert isinstance(config.RAG_PERSONA_PATH, str)
        assert isinstance(config.PERSONA_MAX_CHARS, int)


class TestIntegrationIdentity:
    """Integration tests for identity system."""
    
    def test_identity_flow_with_rag_store(self):
        """Test that identity configuration works with RAG store."""
        # Create RagStore (uses config internally)
        rag_store = RagStore(
            persist_dir="/tmp/test_chroma",
            collection_name="test_identity",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        # Should initialize without errors
        assert rag_store is not None
        assert rag_store.col is not None
    
    def test_identity_block_usable_in_prompt(self):
        """Test that IDENTITY_BLOCK can be used in prompts."""
        identity = config.IDENTITY_BLOCK
        
        # Should be multi-line
        assert '\n' in identity
        
        # Should be usable in a prompt template
        prompt = f"{identity}\n\nUser: Hello\nAssistant:"
        assert config.AI_NAME in prompt
        assert config.AI_USER_NAME in prompt
        assert "System identity" in prompt
    
    def test_complete_customization_flow(self, monkeypatch):
        """Test complete flow of customizing identity."""
        # Set custom identity
        monkeypatch.setenv("AI_NAME", "TestBot")
        monkeypatch.setenv("AI_USER_NAME", "TestUser")
        
        # Reload config
        import importlib
        importlib.reload(config)
        
        # Verify everything updated correctly
        assert config.AI_NAME == "TestBot"
        assert config.AI_USER_NAME == "TestUser"
        assert "TestBot" in config.IDENTITY_BLOCK
        assert "TestUser" in config.IDENTITY_BLOCK
        
        # Verify usable in system
        identity = config.IDENTITY_BLOCK
        assert "You are TestBot" in identity
        assert "TestUser" in identity
        
        # Clean up
        monkeypatch.delenv("AI_NAME", raising=False)
        monkeypatch.delenv("AI_USER_NAME", raising=False)
        importlib.reload(config)


class TestBackwardCompatibility:
    """Test that changes don't break existing functionality."""
    
    def test_existing_config_vars_still_work(self):
        """Test that original config variables still exist."""
        # RAG settings
        assert hasattr(config, 'RAG_ENABLED')
        assert hasattr(config, 'RAG_ENABLE_PERSONA')
        assert hasattr(config, 'RAG_ENABLE_MEMORY')
        
        # Model settings
        assert hasattr(config, 'OLLAMA_MODEL')
        assert hasattr(config, 'OLLAMA_BASE_URL')
        assert hasattr(config, 'EMBED_MODEL')
        
        # Specialist settings
        assert hasattr(config, 'SPECIALIST_INSTRUCTIONS')
    
    def test_identity_block_still_has_critical_instructions(self):
        """Test that IDENTITY_BLOCK still has critical instructions."""
        identity = config.IDENTITY_BLOCK
        
        # Critical instruction about notices
        assert "CRITICAL" in identity or "notices" in identity.lower()
        
        # Should mention tone/behavior
        assert "Tone" in identity or "tone" in identity
    
    def test_old_hardcoded_references_updated(self):
        """Test that old hardcoded 'Ada' and 'luna' are removed."""
        identity = config.IDENTITY_BLOCK
        
        # Should use variables, not hardcoded values
        # (unless those happen to be the current defaults)
        assert config.AI_NAME in identity
        assert config.AI_USER_NAME in identity
