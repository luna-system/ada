# Terminal Specialist: Creative Safety Futures

**Vision**: Safety mechanisms that learn, adapt, and consider human wellness  
**Status**: Design document for Phase 3+ testing  
**Authors**: luna (vision) + Haiku (framework)

---

## Overview

Current TerminalSpecialist has **static safety** (fixed limits, fixed allowlist).

luna's insight: Safety could be **adaptive** - learning from metrics, context, and even human state.

This document captures speculative ideas for future testing & implementation.

---

## Idea 1: "Sane Defaults That Aren't Overly Limiting"

### Problem
Current limits might be too conservative:
- 5s timeout: Too short for `git log --all` on large repos?
- 10KB output: Too small for typical output?
- 20 commands per conversation: Too restrictive?

### Vision: Adaptive Limits

```python
class AdaptiveTerminalSpecialist(TerminalSpecialist):
    """Learn safe limits from usage patterns."""
    
    def __init__(self):
        super().__init__()
        # Start conservative
        self.max_execution_time_s = 5
        self.max_output_bytes = 10 * 1024
        self.max_commands_per_conversation = 20
        
        # Learn from success
        self.success_history = []
    
    def _adjust_limits_based_on_metrics(self):
        """After successful executions, gradually increase limits."""
        if len(self.success_history) >= 10:
            success_rate = sum(self.success_history[-10:]) / 10
            
            # If >90% success, we're probably being too conservative
            if success_rate > 0.9:
                self.max_execution_time_s = min(30, self.max_execution_time_s * 1.1)
                self.max_output_bytes = min(100 * 1024, int(self.max_output_bytes * 1.1))
            
            # If <70% success, tighten up
            elif success_rate < 0.7:
                self.max_execution_time_s = max(1, self.max_execution_time_s * 0.9)
                self.max_output_bytes = max(1024, int(self.max_output_bytes * 0.9))
```

### Future Test Case
```python
def test_adaptive_limits_relax_with_success():
    """After 10 successful commands, limits should gradually increase."""
    specialist = AdaptiveTerminalSpecialist()
    initial_timeout = specialist.max_execution_time_s
    
    # Simulate 15 successful commands
    for _ in range(15):
        specialist.success_history.append(True)
    
    specialist._adjust_limits_based_on_metrics()
    
    # Should be slightly more permissive
    assert specialist.max_execution_time_s > initial_timeout
```

### Safety Principle
- **Lower bound**: Never go below original minimums (safety floor)
- **Upper bound**: Cap increases to reasonable values (safety ceiling)
- **Audit**: Log all adjustments for transparency

---

## Idea 2: "Teaching Ada About Safety"

### Problem
Currently safety rules are hardcoded. But Ada could **learn** what's safe.

### Vision: Self-Adjusting Safety Rules

```python
class TeachableTerminalSpecialist(TerminalSpecialist):
    """Ada learns which commands are safe based on outcomes."""
    
    def __init__(self):
        super().__init__()
        self.command_safety_scores = {}  # "git log" -> 0.99, "pytest --co" -> 0.95
        self.dangerous_patterns = set()  # Patterns that caused errors
    
    def _update_safety_score(self, command: str, metric: TerminalMetric):
        """Learn from each execution outcome."""
        base_cmd = command.split()[0]
        
        if base_cmd not in self.command_safety_scores:
            self.command_safety_scores[base_cmd] = 0.5  # Start neutral
        
        # Successful execution increases confidence
        if metric.success:
            self.command_safety_scores[base_cmd] = min(
                1.0,
                self.command_safety_scores[base_cmd] + 0.05
            )
        # Failed execution decreases confidence
        else:
            self.command_safety_scores[base_cmd] = max(
                0.0,
                self.command_safety_scores[base_cmd] - 0.1
            )
        
        # If we detect dangerous patterns, add to blocklist
        if "error" in metric.error_message.lower():
            self.dangerous_patterns.add(self._extract_pattern(command))
    
    def _extract_pattern(self, command: str) -> str:
        """Extract dangerous pattern (e.g., 'git log --all' if it fails consistently)."""
        # Simplified - real implementation would be more sophisticated
        return command
    
    def should_allow_command(self, command: str) -> tuple[bool, float]:
        """Decide whether to allow command based on learned safety."""
        base_cmd = command.split()[0]
        
        # Check dangerous patterns first
        if any(pattern in command for pattern in self.dangerous_patterns):
            return False, 0.0
        
        # Use learned safety score
        safety_score = self.command_safety_scores.get(base_cmd, 0.5)
        
        # Allow if confidence is high enough
        return safety_score > 0.7, safety_score
```

### Future Test Case
```python
def test_learning_from_failures():
    """Ada should decrease confidence in commands that fail."""
    specialist = TeachableTerminalSpecialist()
    specialist.command_safety_scores["git"] = 0.9
    
    # Simulate a failure
    failed_metric = TerminalMetric(
        command="git log --broken",
        success=False,
        exit_code=1,
        latency_ms=100,
        output_size_bytes=0,
        output_lines=0,
        error_detected=True,
        timestamp=datetime.now(),
        error_message="fatal: unrecognized option"
    )
    
    specialist._update_safety_score("git log --broken", failed_metric)
    
    # Confidence should decrease
    assert specialist.command_safety_scores["git"] < 0.9
    assert "git log --broken" in specialist.dangerous_patterns
```

---

## Idea 3: "Human Wellness: The Tired Developer Problem"

### Problem
Developers make different mistakes at different times:
- Late night: More typos, less patience for output
- Early morning: After coffee, more explorative queries
- End of sprint: More likely to try risky commands

### Vision: Wellness-Aware Safety

```python
from datetime import datetime, time

class WellnessAwareTerminalSpecialist(TeachableTerminalSpecialist):
    """Consider human state in safety decisions."""
    
    # Rough energy levels by hour (very speculative!)
    HUMAN_ENERGY_BY_HOUR = {
        0: 0.2,   # Midnight - very tired
        1: 0.1,   # 1am - exhausted
        6: 0.3,   # 6am - still sleeping
        8: 0.6,   # 8am - waking up
        10: 0.95, # 10am - peak
        14: 0.7,  # 2pm - post-lunch dip
        15: 0.8,  # 3pm - recovering
        20: 0.85, # 8pm - evening energy
        23: 0.4,  # 11pm - winding down
    }
    
    def get_human_energy_level(self) -> float:
        """Estimate developer energy (0.0-1.0) based on time of day."""
        hour = datetime.now().hour
        
        # Linear interpolation between known points
        if hour in self.HUMAN_ENERGY_BY_HOUR:
            return self.HUMAN_ENERGY_BY_HOUR[hour]
        
        # Interpolate
        lower_hour = max(h for h in self.HUMAN_ENERGY_BY_HOUR if h < hour)
        upper_hour = min(h for h in self.HUMAN_ENERGY_BY_HOUR if h > hour)
        
        lower_energy = self.HUMAN_ENERGY_BY_HOUR[lower_hour]
        upper_energy = self.HUMAN_ENERGY_BY_HOUR[upper_hour]
        
        alpha = (hour - lower_hour) / (upper_hour - lower_hour)
        return lower_energy + alpha * (upper_energy - lower_energy)
    
    def get_safety_multiplier_for_wellness(self) -> float:
        """When humans are tired, apply stricter safety limits."""
        energy = self.get_human_energy_level()
        
        # Linear: low energy = high safety multiplier
        # At 0.0 energy: multiplier = 2.0 (twice as strict)
        # At 1.0 energy: multiplier = 0.5 (half as strict, but still safe)
        return 2.0 - energy
    
    def process_with_wellness_awareness(self, request: dict) -> SpecialistResult:
        """Execute command with wellness-aware safety adjustments."""
        energy = self.get_human_energy_level()
        multiplier = self.get_safety_multiplier_for_wellness()
        
        # Temporarily adjust limits
        original_timeout = self.MAX_EXECUTION_TIME_S
        original_output = self.MAX_OUTPUT_BYTES
        
        self.MAX_EXECUTION_TIME_S = original_timeout / multiplier
        self.MAX_OUTPUT_BYTES = int(original_output / multiplier)
        
        try:
            result = self.process(request)
            
            # Add wellness info to metadata
            result.metadata["human_energy_level"] = energy
            result.metadata["safety_multiplier"] = multiplier
            
            return result
        finally:
            # Restore original limits
            self.MAX_EXECUTION_TIME_S = original_timeout
            self.MAX_OUTPUT_BYTES = original_output
```

### Future Test Case
```python
def test_wellness_stricter_safety_when_tired():
    """Late-night commands should have stricter limits."""
    specialist = WellnessAwareTerminalSpecialist()
    
    # Mock a late-night time
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 12, 18, 2, 30)  # 2:30 AM
        
        energy = specialist.get_human_energy_level()
        multiplier = specialist.get_safety_multiplier_for_wellness()
        
        # Very tired at 2:30 AM
        assert energy < 0.3
        # Safety should be stricter (multiplier > 1.5)
        assert multiplier > 1.5
```

### Safety Principle
- **Wellness is informational, not mandatory**: Ada suggests caution but doesn't block
- **Transparent logging**: Every safety adjustment logs the reason
- **Never gets too strict**: Even at 0 energy, safety is reasonable
- **Respects user override**: Human can still run risky commands if they insist

---

## Idea 4: "Getting Weird" - Creative Safety Patterns

### The "Humility Check"

When Ada is tired AND about to run a destructive command, ask for confirmation:

```python
def _should_ask_for_confirmation(self, command: str) -> bool:
    """Ask for confirmation when conditions are risky."""
    energy = self.get_human_energy_level()
    
    dangerous_keywords = ["rm ", "delete", "reset --hard", "rebase -i"]
    
    # If tired AND running dangerous command
    is_dangerous = any(kw in command for kw in dangerous_keywords)
    is_tired = energy < 0.4
    
    return is_dangerous and is_tired
```

### The "Novelty Detector"

Commands Ada hasn't seen before should get extra scrutiny:

```python
def _is_novel_command(self, command: str) -> bool:
    """Detect commands that are new/unusual."""
    base_cmd = command.split()[0]
    subcommand = command.split()[1] if len(command.split()) > 1 else ""
    
    key = f"{base_cmd}:{subcommand}"
    
    if key not in self.command_execution_history:
        return True
    
    history = self.command_execution_history[key]
    
    # If we haven't seen this in 20+ executions, it's still novel
    if len(history) < 20:
        return True
    
    return False
```

### The "Cascade Check"

If multiple commands fail in a row, suggest the human take a break:

```python
def _detect_frustration_cascade(self) -> Optional[str]:
    """Detect when human is hitting lots of errors."""
    recent_metrics = self.metrics[-5:] if len(self.metrics) >= 5 else self.metrics
    
    if not recent_metrics:
        return None
    
    failure_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
    
    if failure_rate > 0.6:  # More than 60% failures
        return "It looks like things aren't going as planned. Want to take a step back?"
    
    return None
```

### Future Test Cases

```python
def test_humility_check_for_dangerous_commands_when_tired():
    """Ask for confirmation on 'rm' when tired."""
    specialist = WellnessAwareTerminalSpecialist()
    specialist.HUMAN_ENERGY_BY_HOUR[2] = 0.2  # Tired at 2 AM
    
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 18, 2, 0)
        
        assert specialist._should_ask_for_confirmation("rm -rf somedir")
        assert not specialist._should_ask_for_confirmation("ls")

def test_novelty_detector():
    """Flag commands we haven't seen before."""
    specialist = WellnessAwareTerminalSpecialist()
    
    assert specialist._is_novel_command("git stash pop")  # Not in history
    
    # After 20+ executions of git stash pop
    for i in range(25):
        specialist.command_execution_history["git:stash pop"] = [None] * (i + 1)
    
    assert not specialist._is_novel_command("git stash pop")  # Familiar now

def test_frustration_cascade_detection():
    """Detect when user is hitting lots of errors."""
    specialist = WellnessAwareTerminalSpecialist()
    
    # Create 5 failed metrics
    for i in range(5):
        specialist.metrics.append(TerminalMetric(
            command=f"git cmd{i}",
            success=False,
            exit_code=1,
            latency_ms=100,
            output_size_bytes=0,
            output_lines=0,
            error_detected=True,
            timestamp=datetime.now()
        ))
    
    message = specialist._detect_frustration_cascade()
    assert message is not None
    assert "step back" in message.lower()
```

---

## Idea 5: "Tie-ins to Wellness Systems"

### Integration Point: Future "Ada Wellness API"

```python
class WellnessIntegratedTerminalSpecialist(WellnessAwareTerminalSpecialist):
    """Consult external wellness system for safety decisions."""
    
    def __init__(self, wellness_client=None):
        super().__init__()
        self.wellness_client = wellness_client  # Future: real API
    
    async def get_developer_state(self) -> Dict[str, Any]:
        """Consult wellness system for human state."""
        if not self.wellness_client:
            # Fallback to simple time-based model
            return {"energy": self.get_human_energy_level()}
        
        # Future: Real wellness API could provide:
        # - Sleep quality (from wearable)
        # - Caffeine intake (from app)
        # - Meeting load (from calendar)
        # - Code review stress (from PR backlog)
        return await self.wellness_client.get_state()
    
    def _safety_multiplier_from_wellness(self, state: Dict[str, Any]) -> float:
        """Multi-factor safety calculation."""
        factors = []
        
        # Energy level
        factors.append(2.0 - state.get("energy", 1.0))
        
        # Meeting fatigue (hypothetical)
        if "meeting_hours_today" in state:
            hours = state["meeting_hours_today"]
            # More meetings = more mental fatigue = stricter safety
            factors.append(1.0 + (hours / 8.0))
        
        # Sleep quality (hypothetical)
        if "sleep_quality" in state:
            quality = state["sleep_quality"]  # 0.0-1.0
            # Poor sleep = stricter
            factors.append(2.0 - quality)
        
        # Average all factors, bounded
        avg_multiplier = sum(factors) / len(factors)
        return min(3.0, max(0.5, avg_multiplier))  # Cap between 0.5x and 3.0x
```

---

## Summary: Future Testing Framework

### Test Categories to Add

```python
# tests/test_terminal_specialist_wellness.py

class TestAdaptiveLimits:
    def test_relax_with_success()
    def test_tighten_with_failures()
    def test_respect_safety_floor()
    def test_respect_safety_ceiling()

class TestSafetyLearning:
    def test_increase_confidence_on_success()
    def test_decrease_confidence_on_failure()
    def test_learn_dangerous_patterns()
    def test_block_learned_dangerous_commands()

class TestWellnessAwareness:
    def test_energy_level_calculation()
    def test_safety_multiplier_from_energy()
    def test_stricter_limits_when_tired()
    def test_humility_check_for_dangerous()
    def test_novelty_detection()
    def test_frustration_cascade_detection()

class TestWellnessIntegration:
    def test_consult_external_wellness_api()
    def test_multifactor_safety_decision()
```

### Implementation Roadmap

**Phase 1 (Current)**: Static safety, fixed limits ✅  
**Phase 2 (Adaptive)**: Adjust limits based on success rate  
**Phase 3 (Learning)**: Learn dangerous patterns from failures  
**Phase 4 (Wellness)**: Consider human energy state  
**Phase 5 (Integration)**: Consult external wellness APIs  

---

## Design Principles

### ✅ Safety First
- Conservative defaults
- Never remove safety, only loosen with evidence
- Transparent about why decisions were made

### ✅ Human-Centered
- Respect human agency (suggest but don't block)
- Consider human state (tired != lazy)
- Support humans, don't replace human judgment

### ✅ Weird is OK
- Humor and personality in safety messages
- Unconventional ideas (frustration detection, novelty flags)
- Creative connections (wellness ↔ safety)

### ✅ Measurable
- Every safety decision logged
- Every adjustment tracked
- Every recommendation provided with reasoning

---

## Open Questions for luna

1. **Energy Model**: Current HUMAN_ENERGY_BY_HOUR is speculative. What would be realistic?
2. **Confirmation Messages**: When should Ada ask for human approval? (Dangerous commands? Novel commands? Both?)
3. **Wellness Integration**: What data sources would be realistic? (Slack status? Calendar? Git patterns?)
4. **Safety Floor**: What's the minimum safety level? (Never block valid commands?)
5. **Learning Decay**: Should "learned" patterns expire? (Commands learned dangerous 1 year ago... still dangerous?)

---

**Status**: This document captures ideas for future work. Not blocking current Phase B experiments.

**Next**: Pick one idea (e.g., Adaptive Limits) and implement as Phase 3 spike.
