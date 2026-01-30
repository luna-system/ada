"""
Exception hierarchy for Ada Swarm error escalation.

Provides role-specific exceptions that bubble up through the swarm hierarchy:
Drone → Worker → Queen → Human

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for swarm errors."""
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Potential issue, can continue
    ERROR = "error"         # Failed but recoverable
    CRITICAL = "critical"   # Failed and needs escalation
    FATAL = "fatal"         # Cannot continue, needs human


class SwarmException(Exception):
    """
    Base exception for all swarm errors.
    
    Includes context about what failed, why, and what to do about it.
    """
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
        attempted_solutions: Optional[List[str]] = None,
        suggested_action: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize swarm exception.
        
        Args:
            message: Human-readable error message
            severity: Error severity level
            context: Additional context (tool name, args, etc.)
            attempted_solutions: What we tried to fix it
            suggested_action: What should be done next
            original_error: Original exception if this is a wrapper
        """
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.attempted_solutions = attempted_solutions or []
        self.suggested_action = suggested_action
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for serialization."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
            "attempted_solutions": self.attempted_solutions,
            "suggested_action": self.suggested_action,
            "original_error": str(self.original_error) if self.original_error else None
        }
    
    def escalate(self, additional_context: Optional[Dict[str, Any]] = None) -> "SwarmException":
        """
        Escalate this exception to the next level.
        
        Args:
            additional_context: Additional context to add
        
        Returns:
            New exception with escalated severity
        """
        new_context = {**self.context, **(additional_context or {})}
        
        # Escalate severity
        severity_map = {
            ErrorSeverity.INFO: ErrorSeverity.WARNING,
            ErrorSeverity.WARNING: ErrorSeverity.ERROR,
            ErrorSeverity.ERROR: ErrorSeverity.CRITICAL,
            ErrorSeverity.CRITICAL: ErrorSeverity.FATAL,
            ErrorSeverity.FATAL: ErrorSeverity.FATAL
        }
        
        return self.__class__(
            message=f"Escalated: {self.message}",
            severity=severity_map[self.severity],
            context=new_context,
            attempted_solutions=self.attempted_solutions,
            suggested_action=self.suggested_action,
            original_error=self.original_error or self
        )


class DroneException(SwarmException):
    """
    Exception raised by Drone agents.
    
    Drones are the lowest level - they do simple, focused tasks.
    When they fail, they bubble up to their Worker.
    
    Examples:
    - Can't access a file
    - Command execution failed
    - Tool returned unexpected result
    """
    
    def __init__(
        self,
        message: str,
        task: Optional[str] = None,
        tool_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize drone exception.
        
        Args:
            message: Error message
            task: Task the drone was working on
            tool_name: Tool that failed
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "role": "drone",
            "task": task,
            "tool_name": tool_name
        })
        
        super().__init__(
            message=f"[Drone] {message}",
            context=context,
            **kwargs
        )


class WorkerException(SwarmException):
    """
    Exception raised by Worker agents.
    
    Workers coordinate multiple drones and handle more complex tasks.
    When they fail after trying alternatives, they bubble up to the Queen.
    
    Examples:
    - All drones failed
    - Can't complete assigned task
    - Resource constraints
    """
    
    def __init__(
        self,
        message: str,
        task: Optional[str] = None,
        failed_drones: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize worker exception.
        
        Args:
            message: Error message
            task: Task the worker was working on
            failed_drones: List of drone IDs that failed
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "role": "worker",
            "task": task,
            "failed_drones": failed_drones or []
        })
        
        super().__init__(
            message=f"[Worker] {message}",
            context=context,
            **kwargs
        )


class QueenException(SwarmException):
    """
    Exception raised by Queen Bee.
    
    The Queen orchestrates the entire swarm. When she can't solve a problem,
    it needs human intervention.
    
    Examples:
    - Can't decompose task
    - All workers failed
    - Strategic decision needed
    - Doom loop detected
    """
    
    def __init__(
        self,
        message: str,
        task: Optional[str] = None,
        failed_workers: Optional[List[str]] = None,
        needs_human: bool = True,
        **kwargs
    ):
        """
        Initialize queen exception.
        
        Args:
            message: Error message
            task: Task the queen was working on
            failed_workers: List of worker IDs that failed
            needs_human: Whether human intervention is needed
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "role": "queen",
            "task": task,
            "failed_workers": failed_workers or [],
            "needs_human": needs_human
        })
        
        # Queen exceptions are always at least CRITICAL
        severity = kwargs.pop("severity", ErrorSeverity.CRITICAL)
        if needs_human and severity != ErrorSeverity.FATAL:
            severity = ErrorSeverity.FATAL
        
        super().__init__(
            message=f"[Queen] {message}",
            severity=severity,
            context=context,
            **kwargs
        )


class DoomLoopException(SwarmException):
    """
    Exception raised when a doom loop is detected.
    
    This is a special exception that indicates the agent is stuck
    and needs to pause for human guidance.
    """
    
    def __init__(
        self,
        message: str,
        loop_type: str,
        agent_id: str,
        evidence: Optional[List[Dict]] = None,
        **kwargs
    ):
        """
        Initialize doom loop exception.
        
        Args:
            message: Error message
            loop_type: Type of doom loop detected
            agent_id: ID of stuck agent
            evidence: Evidence of the doom loop
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "loop_type": loop_type,
            "agent_id": agent_id,
            "evidence": evidence or []
        })
        
        super().__init__(
            message=f"[Doom Loop] {message}",
            severity=ErrorSeverity.FATAL,
            context=context,
            suggested_action="Pause agent and request human guidance",
            **kwargs
        )


class PermissionDeniedException(SwarmException):
    """
    Exception raised when an agent tries to use a tool it doesn't have permission for.
    
    This helps enforce role-based access control.
    """
    
    def __init__(
        self,
        message: str,
        role: str,
        tool_name: str,
        **kwargs
    ):
        """
        Initialize permission denied exception.
        
        Args:
            message: Error message
            role: Agent role that was denied
            tool_name: Tool that was denied
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "role": role,
            "tool_name": tool_name
        })
        
        super().__init__(
            message=f"[Permission Denied] {message}",
            severity=ErrorSeverity.ERROR,
            context=context,
            suggested_action="Use a different tool or escalate to higher role",
            **kwargs
        )


class ResourceException(SwarmException):
    """
    Exception raised when resource constraints are hit.
    
    Examples:
    - Out of API credits
    - Rate limited
    - Disk space full
    - Memory exhausted
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        current_usage: Optional[Any] = None,
        limit: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize resource exception.
        
        Args:
            message: Error message
            resource_type: Type of resource (api_credits, rate_limit, disk, memory)
            current_usage: Current usage level
            limit: Resource limit
            **kwargs: Additional SwarmException args
        """
        context = kwargs.pop("context", {})
        context.update({
            "resource_type": resource_type,
            "current_usage": current_usage,
            "limit": limit
        })
        
        super().__init__(
            message=f"[Resource] {message}",
            severity=ErrorSeverity.CRITICAL,
            context=context,
            suggested_action="Wait for resource to become available or request increase",
            **kwargs
        )


def handle_drone_error(
    error: Exception,
    task: str,
    tool_name: Optional[str] = None,
    attempted_solutions: Optional[List[str]] = None
) -> DroneException:
    """
    Convert a generic error into a DroneException.
    
    Args:
        error: Original error
        task: Task being performed
        tool_name: Tool that failed
        attempted_solutions: What was tried
    
    Returns:
        DroneException with context
    """
    return DroneException(
        message=str(error),
        task=task,
        tool_name=tool_name,
        attempted_solutions=attempted_solutions or [],
        suggested_action="Try alternative approach or escalate to Worker",
        original_error=error
    )


def handle_worker_error(
    error: Exception,
    task: str,
    failed_drones: Optional[List[str]] = None,
    attempted_solutions: Optional[List[str]] = None
) -> WorkerException:
    """
    Convert a generic error into a WorkerException.
    
    Args:
        error: Original error
        task: Task being performed
        failed_drones: Drones that failed
        attempted_solutions: What was tried
    
    Returns:
        WorkerException with context
    """
    return WorkerException(
        message=str(error),
        task=task,
        failed_drones=failed_drones or [],
        attempted_solutions=attempted_solutions or [],
        suggested_action="Escalate to Queen for strategic guidance",
        original_error=error
    )


def handle_queen_error(
    error: Exception,
    task: str,
    failed_workers: Optional[List[str]] = None,
    attempted_solutions: Optional[List[str]] = None
) -> QueenException:
    """
    Convert a generic error into a QueenException.
    
    Args:
        error: Original error
        task: Task being performed
        failed_workers: Workers that failed
        attempted_solutions: What was tried
    
    Returns:
        QueenException with context
    """
    return QueenException(
        message=str(error),
        task=task,
        failed_workers=failed_workers or [],
        attempted_solutions=attempted_solutions or [],
        suggested_action="Request human guidance",
        needs_human=True,
        original_error=error
    )
