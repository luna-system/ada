"""Terminal Specialist - Safe command execution for grounded context access.

Layer 4: Enables Ada to execute safe terminal commands like `git status`, `ls`, `pytest --collect-only`
for grounded, up-to-date information about the codebase.

@ai-indexable: specialist-plugin
@ai-purpose: Execute safe terminal commands for grounded context access in LLM responses
@ai-activation-trigger: Bidirectional - LLM outputs <terminal_command>cmd</terminal_command> tags
@ai-phase: layer4
@ai-safety-level: HIGH
"""

import subprocess
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum

from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistResult,
    SpecialistCapability,
    SpecialistPriority
)


logger = logging.getLogger(__name__)


class TerminalExecutionError(Exception):
    """Base exception for terminal execution errors."""
    pass


class TerminalSecurityError(TerminalExecutionError):
    """Raised when a command violates security policies."""
    pass


class CommandType(Enum):
    """Types of allowed commands."""
    GIT = "git"
    FILESYSTEM = "filesystem"
    TEST = "test"


@dataclass
class TerminalMetric:
    """Measurement from a terminal operation for Phase B research."""
    
    command: str
    success: bool
    exit_code: int
    latency_ms: float
    output_size_bytes: int
    output_lines: int
    error_detected: bool
    timestamp: datetime
    error_message: str = ""
    
    @property
    def groundedness_score(self) -> float:
        """0.0-1.0: How well did execution match expectations?"""
        if self.success and self.exit_code == 0 and self.output_size_bytes > 0:
            return 1.0
        elif not self.error_detected:
            return 0.5
        else:
            return 0.0
    
    @property
    def cognitive_load(self) -> float:
        """0.0-1.0: How much context does LLM need to interpret output?"""
        return min(1.0, self.output_lines / 100.0)


class TerminalSpecialist(BaseSpecialist):
    """Execute safe terminal commands for grounded context access."""
    
    # Security configuration
    ALLOWED_COMMANDS = {
        "git": {
            "description": "Git operations (read-only)",
            "allowed_subcommands": [
                "status", "log", "show", "diff", "branch", "tag", "remote", "rev-parse"
            ],
            "max_output": 50000
        },
        "ls": {
            "description": "List directory contents",
            "allowed_paths": ["brain/", "tests/", "scripts/", "docs/", ".ai/"],
            "max_output": 20000
        },
        "find": {
            "description": "Find files",
            "allowed_paths": ["brain/", "tests/", "scripts/", "docs/", ".ai/"],
            "max_output": 10000
        },
        "pytest": {
            "description": "Test discovery",
            "allowed_args": ["--collect-only", "--co", "-q", "-v"],
            "max_output": 50000
        }
    }
    
    # Resource limits
    MAX_OUTPUT_BYTES = 10 * 1024  # 10KB
    MAX_EXECUTION_TIME_S = 5
    MAX_COMMANDS_PER_CONVERSATION = 20
    
    # Regex patterns for security
    SHELL_METACHARACTERS = re.compile(r'[;&|`$\(\)\[\]{}<>\\]|>>|&&|;|\|\|')
    PATH_TRAVERSAL = re.compile(r'\.\./|\.\.\\')
    COMMAND_INJECTION = re.compile(r'\$\(.*\)|\`.*\`|\${.*}')
    
    def __init__(self):
        """Initialize the terminal specialist."""
        self._capability = SpecialistCapability(
            name="terminal",
            description="Execute safe terminal commands for grounded context access",
            version="1.0.0",
            context_priority=SpecialistPriority.HIGH,
            context_icon="⚡"
        )
        
        self.metrics: List[TerminalMetric] = []
        self.commands_executed = 0
    
    @property
    def capability(self) -> SpecialistCapability:
        """Return specialist capability metadata."""
        return self._capability
    
    def should_activate(self, context: dict) -> bool:
        """Never auto-activate - bidirectional only."""
        return False
    
    def process(self, request: dict) -> SpecialistResult:
        """Execute a terminal command safely."""
        command = request.get("command", "").strip()
        
        if not command:
            return SpecialistResult(
                success=False,
                specialist_name="terminal",
                context_text="❌ No command provided",
                metadata={"error": True}
            )
        
        try:
            self._validate_command(command)
            parsed = self._parse_command(command)
            
            if not parsed:
                return SpecialistResult(
                    success=False,
                    specialist_name="terminal",
                    context_text="❌ Command could not be parsed",
                    metadata={"error": True}
                )
            
            metric = self._execute_sandboxed(parsed)
            self._audit_log(metric)
            return self._format_result(metric)
            
        except TerminalSecurityError as e:
            logger.warning(f"Security check failed: {command}")
            return SpecialistResult(
                success=False,
                specialist_name="terminal",
                context_text=f"❌ Security check failed: {str(e)}",
                metadata={"error": True}
            )
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return SpecialistResult(
                success=False,
                specialist_name="terminal",
                context_text=f"❌ Execution error: {str(e)}",
                metadata={"error": True}
            )
    
    def _validate_command(self, command: str) -> None:
        """Validate command for security violations."""
        if self.SHELL_METACHARACTERS.search(command):
            raise TerminalSecurityError("Shell metacharacters not allowed")
        
        if self.PATH_TRAVERSAL.search(command):
            raise TerminalSecurityError("Path traversal not allowed")
        
        if self.COMMAND_INJECTION.search(command):
            raise TerminalSecurityError("Command substitution not allowed")
        
        parts = command.split()
        if not parts or parts[0] not in self.ALLOWED_COMMANDS:
            raise TerminalSecurityError(f"Command not in allowed list")
    
    def _parse_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse and validate command structure."""
        parts = command.split()
        if not parts:
            return None
        
        base_command = parts[0]
        parsed = {
            "base_command": base_command,
            "args": parts[1:],
            "command_type": None
        }
        
        # Validate git subcommands
        if base_command == "git":
            if len(parts) < 2:
                raise TerminalSecurityError("git requires a subcommand")
            subcommand = parts[1]
            if subcommand not in self.ALLOWED_COMMANDS["git"]["allowed_subcommands"]:
                raise TerminalSecurityError(f"git subcommand '{subcommand}' not allowed")
            parsed["subcommand"] = subcommand
            parsed["args"] = parts[2:]
            parsed["command_type"] = CommandType.GIT
        
        # Validate ls paths
        elif base_command == "ls":
            for arg in parts[1:]:
                if not arg.startswith("-") and not any(arg.startswith(p) for p in self.ALLOWED_COMMANDS["ls"]["allowed_paths"]):
                    raise TerminalSecurityError(f"Path '{arg}' not in allowed list")
            parsed["command_type"] = CommandType.FILESYSTEM
        
        # Validate pytest args
        elif base_command == "pytest":
            for arg in parts[1:]:
                if not arg.startswith("-") and arg not in self.ALLOWED_COMMANDS["pytest"]["allowed_args"] and not arg.endswith(".py"):
                    raise TerminalSecurityError(f"pytest argument '{arg}' not allowed")
            parsed["command_type"] = CommandType.TEST
        
        return parsed
    
    def _execute_sandboxed(self, parsed: Dict[str, Any]) -> TerminalMetric:
        """Execute command with resource limits."""
        command_str = " ".join([parsed["base_command"]] + parsed["args"])
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command_str.split(),
                capture_output=True,
                text=True,
                timeout=self.MAX_EXECUTION_TIME_S
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            output = result.stdout[:self.MAX_OUTPUT_BYTES]
            
            metric = TerminalMetric(
                command=command_str,
                success=result.returncode == 0,
                exit_code=result.returncode,
                latency_ms=latency_ms,
                output_size_bytes=len(output),
                output_lines=len(output.split('\n')),
                error_detected=len(result.stderr) > 0,
                timestamp=datetime.now(),
                error_message=result.stderr[:500]
            )
            
            self.metrics.append(metric)
            self.commands_executed += 1
            return metric
            
        except subprocess.TimeoutExpired:
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            metric = TerminalMetric(
                command=command_str,
                success=False,
                exit_code=-1,
                latency_ms=latency_ms,
                output_size_bytes=0,
                output_lines=0,
                error_detected=True,
                timestamp=datetime.now(),
                error_message="Command timeout"
            )
            self.metrics.append(metric)
            return metric
        except Exception as e:
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            metric = TerminalMetric(
                command=command_str,
                success=False,
                exit_code=-1,
                latency_ms=latency_ms,
                output_size_bytes=0,
                output_lines=0,
                error_detected=True,
                timestamp=datetime.now(),
                error_message=str(e)
            )
            self.metrics.append(metric)
            return metric
    
    def _format_result(self, metric: TerminalMetric) -> SpecialistResult:
        """Format execution result for LLM injection."""
        if not metric.success:
            context_text = f"Terminal Command Failed\nCommand: {metric.command}\nExit Code: {metric.exit_code}\nError: {metric.error_message}"
            success = False
        else:
            context_text = f"Terminal Command Output\nCommand: {metric.command}\nExit Code: {metric.exit_code}\nLatency: {metric.latency_ms:.1f}ms"
            success = True
        
        return SpecialistResult(
            success=success,
            specialist_name="terminal",
            context_text=context_text,
            data={"command": metric.command, "exit_code": metric.exit_code},
            metadata={"groundedness_score": metric.groundedness_score, "cognitive_load": metric.cognitive_load}
        )
    
    def _audit_log(self, metric: TerminalMetric) -> None:
        """Log execution for audit trail."""
        audit_record = {
            "timestamp": metric.timestamp.isoformat(),
            "command": metric.command,
            "exit_code": metric.exit_code,
            "latency_ms": metric.latency_ms,
            "output_size_bytes": metric.output_size_bytes,
            "success": metric.success,
            "error_detected": metric.error_detected,
            "groundedness_score": metric.groundedness_score,
            "allowed": True
        }
        logger.info(f"Terminal execution: {audit_record}")
    
    def _create_metric(self, command: str, success: bool, exit_code: int,
                       latency_ms: float, output_size_bytes: int,
                       output_lines: int, error_detected: bool) -> TerminalMetric:
        """Create a metric object."""
        return TerminalMetric(
            command=command,
            success=success,
            exit_code=exit_code,
            latency_ms=latency_ms,
            output_size_bytes=output_size_bytes,
            output_lines=output_lines,
            error_detected=error_detected,
            timestamp=datetime.now()
        )
    
    def _format_audit_log(self, metric: TerminalMetric) -> Dict[str, Any]:
        """Format metric as audit log entry."""
        return {
            "timestamp": metric.timestamp.isoformat(),
            "command": metric.command,
            "exit_code": metric.exit_code,
            "latency_ms": metric.latency_ms,
            "output_size_bytes": metric.output_size_bytes,
            "success": metric.success,
            "error_detected": metric.error_detected,
            "groundedness_score": metric.groundedness_score,
            "allowed": True
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of execution metrics for Phase B analysis."""
        if not self.metrics:
            return {"total_commands": 0}
        
        success_count = sum(1 for m in self.metrics if m.success)
        avg_latency = sum(m.latency_ms for m in self.metrics) / len(self.metrics)
        avg_groundedness = sum(m.groundedness_score for m in self.metrics) / len(self.metrics)
        
        return {
            "total_commands": len(self.metrics),
            "successful": success_count,
            "failed": len(self.metrics) - success_count,
            "success_rate": success_count / len(self.metrics),
            "avg_latency_ms": avg_latency,
            "avg_groundedness_score": avg_groundedness
        }


__all__ = ["TerminalSpecialist", "TerminalMetric", "TerminalSecurityError", "TerminalExecutionError"]
