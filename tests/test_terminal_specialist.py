"""Tests for TerminalSpecialist - Layer 4 safe command execution."""

import pytest
from datetime import datetime
from brain.specialists.terminal_specialist import (
    TerminalSpecialist,
    TerminalMetric,
    TerminalExecutionError,
    TerminalSecurityError,
)


class TestTerminalMetric:
    """Test the measurement dataclass."""
    
    def test_metric_creation(self):
        """Create a metric object."""
        metric = TerminalMetric(
            command="git status",
            success=True,
            exit_code=0,
            latency_ms=45.2,
            output_size_bytes=342,
            output_lines=12,
            error_detected=False,
            timestamp=datetime.now()
        )
        assert metric.command == "git status"
        assert metric.success is True
        assert metric.exit_code == 0
    
    def test_groundedness_score(self):
        """Test groundedness scoring."""
        # Success case
        metric_success = TerminalMetric(
            command="git status",
            success=True,
            exit_code=0,
            latency_ms=45.2,
            output_size_bytes=342,
            output_lines=12,
            error_detected=False,
            timestamp=datetime.now()
        )
        assert metric_success.groundedness_score > 0.9
        
        # Failure case
        metric_failed = TerminalMetric(
            command="git invalid",
            success=False,
            exit_code=1,
            latency_ms=45.2,
            output_size_bytes=0,
            output_lines=0,
            error_detected=True,
            timestamp=datetime.now()
        )
        assert metric_failed.groundedness_score < 0.1
    
    def test_cognitive_load(self):
        """Test cognitive load measurement."""
        # Small output
        metric_small = TerminalMetric(
            command="git status",
            success=True,
            exit_code=0,
            latency_ms=45.2,
            output_size_bytes=342,
            output_lines=5,
            error_detected=False,
            timestamp=datetime.now()
        )
        assert metric_small.cognitive_load < 0.1
        
        # Large output
        metric_large = TerminalMetric(
            command="find .",
            success=True,
            exit_code=0,
            latency_ms=45.2,
            output_size_bytes=10000,
            output_lines=200,
            error_detected=False,
            timestamp=datetime.now()
        )
        assert metric_large.cognitive_load >= 1.0


class TestTerminalSpecialistSafety:
    """Verify security constraints."""
    
    def test_rejects_shell_injection(self):
        """Prevent shell metacharacters."""
        specialist = TerminalSpecialist()
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("git status; rm -rf /")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("git status && evil_command")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("git status | cat /etc/passwd")
    
    def test_rejects_disallowed_commands(self):
        """Only allow whitelisted commands."""
        specialist = TerminalSpecialist()
        
        # Disallowed commands
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("eval 'bad code'")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("sudo apt-get install")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("python -m pip install")
    
    def test_allows_safe_commands(self):
        """Whitelist safe operations."""
        specialist = TerminalSpecialist()
        
        # These should NOT raise
        specialist._validate_command("git status")
        specialist._validate_command("git log --oneline -10")
        specialist._validate_command("ls -la brain/")
        specialist._validate_command("pytest --collect-only")
    
    def test_prevents_environment_access(self):
        """Block environment variable tricks."""
        specialist = TerminalSpecialist()
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("git status $EVIL_VAR")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("ls $(bad_command)")
    
    def test_prevents_path_traversal(self):
        """Block directory escape attempts."""
        specialist = TerminalSpecialist()
        
        # Paths with ../ should be rejected
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("ls ../../etc/passwd")
        
        with pytest.raises(TerminalSecurityError):
            specialist._validate_command("find ../../../")


class TestTerminalSpecialistValidation:
    """Test command validation logic."""
    
    def test_parse_git_status(self):
        """Parse 'git status' command."""
        specialist = TerminalSpecialist()
        parsed = specialist._parse_command("git status")
        
        assert parsed is not None
        assert parsed["base_command"] == "git"
        assert parsed["subcommand"] == "status"
        assert parsed["args"] == []
    
    def test_parse_git_log_with_args(self):
        """Parse 'git log' with arguments."""
        specialist = TerminalSpecialist()
        parsed = specialist._parse_command("git log --oneline -10")
        
        assert parsed is not None
        assert parsed["base_command"] == "git"
        assert parsed["subcommand"] == "log"
        assert "--oneline" in parsed["args"]
        assert "-10" in parsed["args"]
    
    def test_parse_ls_with_path(self):
        """Parse 'ls' with path argument."""
        specialist = TerminalSpecialist()
        parsed = specialist._parse_command("ls -la brain/")
        
        assert parsed is not None
        assert parsed["base_command"] == "ls"
        assert "-la" in parsed["args"]
        assert "brain/" in parsed["args"]
    
    def test_reject_unknown_git_subcommand(self):
        """Reject git subcommands not in allowlist."""
        specialist = TerminalSpecialist()
        
        # Parse checks git subcommands - validate just checks shell syntax
        with pytest.raises(TerminalSecurityError):
            specialist._parse_command("git push origin main")
        
        with pytest.raises(TerminalSecurityError):
            specialist._parse_command("git commit -m 'evil'")


class TestTerminalSpecialistActivation:
    """Test specialist activation rules."""
    
    def test_never_auto_activates(self):
        """Terminal specialist should never auto-activate."""
        specialist = TerminalSpecialist()
        
        # Even with relevant context, should not auto-activate
        context = {"needs_filesystem": True, "query": "what files are there?"}
        assert specialist.should_activate(context) is False
    
    def test_activation_metadata(self):
        """Verify activation metadata."""
        specialist = TerminalSpecialist()
        
        info = specialist.capability
        assert info.name == "terminal"
        assert "bidirectional" in info.description.lower() or info.version == "1.0.0"


class TestTerminalSpecialistIntegration:
    """Test full specialist workflow."""
    
    def test_process_git_status(self):
        """Process a real git status command."""
        specialist = TerminalSpecialist()
        
        result = specialist.process({
            "command": "git status"
        })
        
        assert result.specialist_name == "terminal"
        assert not result.metadata.get("error", False)
        assert len(result.context_text) > 0
    
    def test_process_rejected_command(self):
        """Process a rejected command."""
        specialist = TerminalSpecialist()
        
        result = specialist.process({
            "command": "rm -rf /"
        })
        
        assert result.metadata.get("error", False) is True
        assert "Security" in result.context_text or "not allowed" in result.context_text.lower()
    
    def test_context_formatting(self):
        """Format result for LLM injection."""
        specialist = TerminalSpecialist()
        
        result = specialist.process({
            "command": "git log --oneline -5"
        })
        
        # Should be formatted for prompt injection
        assert "git log" in result.context_text or "command" in result.context_text.lower()
        assert result.specialist_name == "terminal"


class TestTerminalSpecialistAuditTrail:
    """Test logging and audit functionality."""
    
    def test_audit_log_structure(self):
        """Verify audit log has required fields."""
        specialist = TerminalSpecialist()
        
        metric = specialist._create_metric(
            command="git status",
            success=True,
            exit_code=0,
            latency_ms=45.2,
            output_size_bytes=342,
            output_lines=12,
            error_detected=False
        )
        
        audit_log = specialist._format_audit_log(metric)
        
        assert "timestamp" in audit_log
        assert "command" in audit_log
        assert "exit_code" in audit_log
        assert "latency_ms" in audit_log
        assert "allowed" in audit_log
    
    def test_metric_persistence(self):
        """Metrics are recorded for analysis."""
        specialist = TerminalSpecialist()
        
        # Process a command
        result = specialist.process({"command": "git status"})
        
        # Should have metrics
        assert specialist.get_metrics_summary() is not None


class TestTerminalSpecialistErrorHandling:
    """Test error conditions."""
    
    def test_missing_git_command(self):
        """Handle case where git is not installed."""
        specialist = TerminalSpecialist()
        
        # Even if git fails, should return gracefully
        result = specialist.process({
            "command": "git status"
        })
        
        # Should either succeed or have clear error message
        assert isinstance(result.context_text, str)
        assert result.specialist_name == "terminal"
    
    def test_timeout_handling(self):
        """Commands that timeout are handled gracefully."""
        specialist = TerminalSpecialist()
        specialist.MAX_EXECUTION_TIME_S = 0.001  # 1ms timeout
        
        # This will likely timeout
        result = specialist.process({
            "command": "git log --all --graph"  # Potentially slow
        })
        
        # Should handle timeout gracefully
        assert isinstance(result.context_text, str)
    
    def test_output_limit_enforcement(self):
        """Output is truncated if too large."""
        specialist = TerminalSpecialist()
        
        result = specialist.process({
            "command": "find ."
        })
        
        # Output should be limited
        content_size = len(result.context_text)
        assert content_size < specialist.MAX_OUTPUT_BYTES * 2  # With some margin for formatting


class TestTerminalSpecialistResourceLimits:
    """Test resource constraint enforcement."""
    
    def test_max_output_limit(self):
        """Commands are bounded by output limit."""
        specialist = TerminalSpecialist()
        assert specialist.MAX_OUTPUT_BYTES == 10 * 1024  # 10KB
    
    def test_max_execution_time(self):
        """Commands have timeout."""
        specialist = TerminalSpecialist()
        assert specialist.MAX_EXECUTION_TIME_S == 5
    
    def test_max_commands_per_conversation(self):
        """Rate limiting for conversation."""
        specialist = TerminalSpecialist()
        assert specialist.MAX_COMMANDS_PER_CONVERSATION == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
