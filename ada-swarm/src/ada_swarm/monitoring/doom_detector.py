"""
Doom Loop Detector - Prevents agents from getting stuck in infinite loops.

Monitors agent behavior and detects:
- Repeated failed API calls
- Excessive tool calls without progress
- Infinite polling loops
- Context overflow patterns

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class DoomLoopType(Enum):
    """Types of doom loops we can detect."""
    REPEATED_FAILURES = "repeated_failures"  # Same tool/API failing repeatedly
    EXCESSIVE_CALLS = "excessive_calls"      # Too many calls without progress
    INFINITE_POLLING = "infinite_polling"    # Polling same endpoint forever
    CONTEXT_OVERFLOW = "context_overflow"    # Reading too many files
    NO_PROGRESS = "no_progress"              # Doing things but not advancing


@dataclass
class CallRecord:
    """Record of a single tool/API call."""
    timestamp: datetime
    call_type: str  # "tool", "api", "llm"
    name: str       # Tool name or endpoint
    success: bool
    args: Optional[Dict] = None


@dataclass
class DoomLoopAlert:
    """Alert when a doom loop is detected."""
    loop_type: DoomLoopType
    severity: str  # "warning", "critical"
    message: str
    evidence: List[CallRecord]
    suggested_action: str


class DoomLoopDetector:
    """
    Monitors agent behavior and detects doom loops.
    
    Tracks:
    - Tool call history
    - API call patterns
    - LLM request patterns
    - Progress indicators
    """
    
    def __init__(
        self,
        agent_id: str,
        max_history: int = 100,
        failure_threshold: int = 5,
        polling_threshold: int = 10,
        read_threshold: int = 15,
        time_window: int = 300  # 5 minutes
    ):
        """
        Initialize doom loop detector.
        
        Args:
            agent_id: ID of agent being monitored
            max_history: Max call records to keep
            failure_threshold: Consecutive failures before alert
            polling_threshold: Repeated polls before alert
            read_threshold: File reads before alert
            time_window: Time window for pattern detection (seconds)
        """
        self.agent_id = agent_id
        self.max_history = max_history
        self.failure_threshold = failure_threshold
        self.polling_threshold = polling_threshold
        self.read_threshold = read_threshold
        self.time_window = timedelta(seconds=time_window)
        
        # Call history (deque for efficient FIFO)
        self.call_history: deque[CallRecord] = deque(maxlen=max_history)
        
        # Pattern tracking
        self.consecutive_failures: Dict[str, int] = defaultdict(int)
        self.polling_counts: Dict[str, int] = defaultdict(int)
        self.files_read: set = set()
        
        # Progress tracking
        self.last_progress_time: Optional[datetime] = None
        self.progress_indicators: List[str] = []
        
        # Alerts
        self.active_alerts: List[DoomLoopAlert] = []
        
        logger.info(f"Doom loop detector initialized for agent {agent_id}")
    
    def record_tool_call(
        self,
        tool_name: str,
        success: bool,
        args: Optional[Dict] = None
    ) -> Optional[DoomLoopAlert]:
        """
        Record a tool call and check for doom loops.
        
        Args:
            tool_name: Name of tool called
            success: Whether call succeeded
            args: Tool arguments
        
        Returns:
            Alert if doom loop detected, None otherwise
        """
        record = CallRecord(
            timestamp=datetime.now(),
            call_type="tool",
            name=tool_name,
            success=success,
            args=args
        )
        
        self.call_history.append(record)
        
        # Update pattern tracking
        if not success:
            self.consecutive_failures[tool_name] += 1
        else:
            self.consecutive_failures[tool_name] = 0
        
        # Track file reads
        if tool_name == "read_file" and success and args:
            self.files_read.add(args.get("file_path", ""))
        
        # Check for doom loops
        return self._check_patterns()
    
    def record_api_call(
        self,
        endpoint: str,
        success: bool,
        status_code: Optional[int] = None
    ) -> Optional[DoomLoopAlert]:
        """
        Record an API call and check for doom loops.
        
        Args:
            endpoint: API endpoint called
            success: Whether call succeeded
            status_code: HTTP status code
        
        Returns:
            Alert if doom loop detected, None otherwise
        """
        record = CallRecord(
            timestamp=datetime.now(),
            call_type="api",
            name=endpoint,
            success=success,
            args={"status_code": status_code} if status_code else None
        )
        
        self.call_history.append(record)
        
        # Track polling patterns
        if endpoint == "/v1/models":
            self.polling_counts[endpoint] += 1
        
        # Update failure tracking
        if not success:
            self.consecutive_failures[endpoint] += 1
        else:
            self.consecutive_failures[endpoint] = 0
        
        return self._check_patterns()
    
    def record_llm_request(
        self,
        model: str,
        success: bool,
        tokens: Optional[int] = None
    ) -> Optional[DoomLoopAlert]:
        """
        Record an LLM request and check for doom loops.
        
        Args:
            model: Model name
            success: Whether request succeeded
            tokens: Token count
        
        Returns:
            Alert if doom loop detected, None otherwise
        """
        record = CallRecord(
            timestamp=datetime.now(),
            call_type="llm",
            name=model,
            success=success,
            args={"tokens": tokens} if tokens else None
        )
        
        self.call_history.append(record)
        
        if not success:
            self.consecutive_failures[model] += 1
        else:
            self.consecutive_failures[model] = 0
        
        return self._check_patterns()
    
    def record_progress(self, indicator: str):
        """
        Record a progress indicator (task created, file written, etc.).
        
        Args:
            indicator: Description of progress made
        """
        self.last_progress_time = datetime.now()
        self.progress_indicators.append(indicator)
        
        # Reset some counters on progress
        self.polling_counts.clear()
        logger.info(f"Progress recorded for {self.agent_id}: {indicator}")
    
    def _check_patterns(self) -> Optional[DoomLoopAlert]:
        """
        Check for doom loop patterns in recent history.
        
        Returns:
            Alert if pattern detected, None otherwise
        """
        # Check 1: Repeated failures
        for name, count in self.consecutive_failures.items():
            if count >= self.failure_threshold:
                alert = DoomLoopAlert(
                    loop_type=DoomLoopType.REPEATED_FAILURES,
                    severity="critical",
                    message=f"Agent stuck: {name} failed {count} times in a row",
                    evidence=self._get_recent_calls(name),
                    suggested_action=f"Stop calling {name} and try alternative approach"
                )
                self.active_alerts.append(alert)
                logger.error(f"DOOM LOOP DETECTED: {alert.message}")
                return alert
        
        # Check 2: Infinite polling
        for endpoint, count in self.polling_counts.items():
            if count >= self.polling_threshold:
                alert = DoomLoopAlert(
                    loop_type=DoomLoopType.INFINITE_POLLING,
                    severity="critical",
                    message=f"Agent stuck polling {endpoint} ({count} times)",
                    evidence=self._get_recent_calls(endpoint),
                    suggested_action="Stop polling and request human input"
                )
                self.active_alerts.append(alert)
                logger.error(f"DOOM LOOP DETECTED: {alert.message}")
                return alert
        
        # Check 3: Context overflow (too many file reads)
        if len(self.files_read) >= self.read_threshold:
            alert = DoomLoopAlert(
                loop_type=DoomLoopType.CONTEXT_OVERFLOW,
                severity="warning",
                message=f"Agent read {len(self.files_read)} files - possible context overflow",
                evidence=self._get_recent_calls("read_file"),
                suggested_action="Stop reading and start planning/acting"
            )
            self.active_alerts.append(alert)
            logger.warning(f"DOOM LOOP WARNING: {alert.message}")
            return alert
        
        # Check 4: No progress in time window
        if self.last_progress_time:
            time_since_progress = datetime.now() - self.last_progress_time
            if time_since_progress > self.time_window:
                recent_calls = list(self.call_history)[-20:]
                alert = DoomLoopAlert(
                    loop_type=DoomLoopType.NO_PROGRESS,
                    severity="warning",
                    message=f"No progress for {time_since_progress.seconds}s",
                    evidence=recent_calls,
                    suggested_action="Request human guidance or try different approach"
                )
                self.active_alerts.append(alert)
                logger.warning(f"DOOM LOOP WARNING: {alert.message}")
                return alert
        
        return None
    
    def _get_recent_calls(self, name: str, limit: int = 10) -> List[CallRecord]:
        """Get recent calls matching a name."""
        return [
            record for record in list(self.call_history)[-limit:]
            if record.name == name
        ]
    
    def get_status(self) -> Dict:
        """
        Get current monitoring status.
        
        Returns:
            Status dict with metrics and alerts
        """
        return {
            "agent_id": self.agent_id,
            "total_calls": len(self.call_history),
            "files_read": len(self.files_read),
            "active_alerts": len(self.active_alerts),
            "consecutive_failures": dict(self.consecutive_failures),
            "polling_counts": dict(self.polling_counts),
            "last_progress": self.last_progress_time.isoformat() if self.last_progress_time else None,
            "alerts": [
                {
                    "type": alert.loop_type.value,
                    "severity": alert.severity,
                    "message": alert.message,
                    "action": alert.suggested_action
                }
                for alert in self.active_alerts
            ]
        }
    
    def should_pause(self) -> Tuple[bool, Optional[str]]:
        """
        Check if agent should pause for human input.
        
        Returns:
            (should_pause, reason)
        """
        # Check for critical alerts
        critical_alerts = [
            alert for alert in self.active_alerts
            if alert.severity == "critical"
        ]
        
        if critical_alerts:
            alert = critical_alerts[0]
            return True, f"{alert.message} - {alert.suggested_action}"
        
        # Check for multiple warnings
        if len(self.active_alerts) >= 3:
            return True, "Multiple doom loop warnings detected - requesting human guidance"
        
        return False, None
    
    def reset(self):
        """Reset detector state (after human intervention)."""
        self.consecutive_failures.clear()
        self.polling_counts.clear()
        self.files_read.clear()
        self.active_alerts.clear()
        self.last_progress_time = datetime.now()
        logger.info(f"Doom loop detector reset for {self.agent_id}")
