# Layer 4: Terminal Specialist Implementation Plan

## luna's Vision
> "teach ada how to use 'ls' and similar safe commands. learn how to properly build safety around this."

## Connection to Phase B (LLM↔LLM Research)

**Key Finding from Demo:**
- CodebaseSpecialist achieved 80% lookup success with **zero execution side effects**
- All operations were read-only, pre-indexed, and sandboxed
- Quality signal (docstring presence) correlated with comprehension

**Phase B Science**: When model-to-model communication includes grounded operations (real filesystem, real git), we can measure **cognitive load** and **hallucination reduction** empirically.

Terminal Specialist enables this measurement:
- Before: "Ada told me to run `rm -rf /`" (can't measure groundedness)
- After: "Ada said to run `git status` which returned..." (can measure accuracy, context leakage, safety)

---

## Proposed Implementation

### Architecture

```
LLM generates: "Let me check the test status" → <terminal_command>pytest --co</terminal_command>

Safety Gates (in order):
1. Parse: Extract command from XML tag
2. Validate: Check against ALLOWED_COMMANDS registry
3. Sandbox: Set resource limits (timeout=5s, output=10KB)
4. Execute: Run in restricted environment
5. Log: Record execution for audit trail
6. Stream: Return output to LLM

LLM continues: "The tests include: test_memory_decay, test_weight_optimization..."
```

### Phase 1: Safe Command Registry (Immediate)

**Goal**: Enable `ls`, `git status`, `git log` - basic filesystem/repo inspection

**Allowed Commands:**
```python
ALLOWED_COMMANDS = {
    # Filesystem inspection (read-only)
    "ls": {
        "description": "List directory",
        "args": {"max_depth": 2, "max_results": 100},
        "paths": ["brain/", "tests/", "scripts/", "docs/"]
    },
    "find": {
        "description": "Find files",
        "args": {"max_results": 50, "allowed_patterns": [".py", ".md", ".json"]},
        "paths": ["brain/", "tests/", "scripts/", ".ai/"]
    },
    
    # Git inspection (read-only)
    "git": {
        "description": "Git operations",
        "subcommands": ["status", "log", "show", "diff", "branch", "tag"],
        "args": {"max_lines": 1000},
        "paths": ["."]
    },
    
    # Test inspection
    "pytest": {
        "description": "Test discovery and metadata",
        "args": ["--collect-only", "--co", "-q"],
        "max_output": 50000
    }
}
```

**Security Model:**
- ✅ Read-only filesystem operations
- ✅ Git inspection (no push/commit/rebase)
- ✅ Test discovery (no actual execution - use pytest --co)
- ❌ NO shell access
- ❌ NO arbitrary arguments
- ❌ NO environment variable modification
- ❌ NO credential exposure

### Phase 2: Measurement Infrastructure (For Phase B Science)

**What we measure:**
```python
@dataclass
class TerminalMetric:
    """Measurement from a terminal operation."""
    command: str
    success: bool
    exit_code: int
    latency_ms: float
    output_size_bytes: int
    output_lines: int
    error_detected: bool  # stderr content
    timestamp: datetime
    
    # Phase B research metrics:
    @property
    def groundedness_score(self) -> float:
        """0.0-1.0: How well did execution match LLM's expectations?"""
        # Measured by: exit code, output size, error patterns
        return 1.0 if exit_code == 0 and output_size_bytes > 0 else 0.0
    
    @property
    def cognitive_load(self) -> float:
        """0.0-1.0: How much context does LLM need to interpret this?"""
        # Measured by: output complexity, error messages
        return min(1.0, output_lines / 100.0)
```

**Science Question:**
> Does grounded terminal access + output reduce LLM hallucination rate vs. pure codebase lookup?

**Experiment Design:**
1. Ask Ada same question in 3 modes:
   - Mode A: Codebase lookup only
   - Mode B: Codebase + terminal (git status, test count)
   - Mode C: Codebase + terminal + git diff
2. Measure answer accuracy against ground truth
3. Measure context token cost
4. Measure response confidence (certainty vs hedging)

### Phase 3: Error Handling & Edge Cases

**What can go wrong?**
1. Command not in allowlist → reject with helpful error
2. Arguments bypass restrictions → sanitize/reject
3. Symlink escape attempt → resolve and validate
4. Output too large → truncate with notice
5. Timeout → kill process, return partial output
6. Subprocess error (git not installed) → graceful fallback

### Phase 4: Audit Trail & Compliance

**What we log:**
```python
AUDIT_LOG_FORMAT = {
    "timestamp": "2025-12-18T16:49:47Z",
    "command": "git log --oneline -10",
    "user": "llm",
    "exit_code": 0,
    "output_size_bytes": 342,
    "latency_ms": 45,
    "allowed": True,
    "reason": "git subcommand 'log' in allowlist"
}
```

**Why it matters:**
- Security: Detect suspicious patterns
- Science: Understand LLM behavior evolution
- UX: Debug when things fail

---

## Code Structure

### File: `brain/specialists/terminal_specialist.py`

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TerminalMetric:
    """Measurement from terminal operation."""
    command: str
    success: bool
    exit_code: int
    latency_ms: float
    output_size_bytes: int
    output_lines: int
    error_detected: bool
    timestamp: datetime
    
    @property
    def groundedness_score(self) -> float:
        return 1.0 if self.exit_code == 0 and self.output_size_bytes > 0 else 0.0
    
    @property
    def cognitive_load(self) -> float:
        return min(1.0, self.output_lines / 100.0)

class TerminalSpecialist(BaseSpecialist):
    """Execute safe terminal commands for grounded context."""
    
    # luna's vision made concrete:
    ALLOWED_COMMANDS = {
        "ls": {...},
        "find": {...},
        "git": {...},
        "pytest": {...}
    }
    
    MAX_OUTPUT_BYTES = 10 * 1024  # 10KB
    MAX_EXECUTION_TIME_S = 5
    MAX_COMMANDS_PER_CONVERSATION = 20
    
    def should_activate(self, context: dict) -> bool:
        """Never auto-activate - bidirectional only."""
        return False
    
    def process(self, request: dict) -> SpecialistResult:
        """Execute terminal command safely."""
        command = request.get("command", "")
        
        # 1. Parse and validate
        parsed = self._parse_command(command)
        if not parsed:
            return SpecialistResult(
                specialist_name="terminal",
                content="❌ Command not in allowed list",
                metadata={"error": True}
            )
        
        # 2. Execute with sandbox
        result = self._execute_sandboxed(parsed)
        
        # 3. Log for audit trail
        self._audit_log(result)
        
        # 4. Format for LLM
        return self._format_result(result)
    
    def _parse_command(self, command: str) -> Optional[dict]:
        """Parse and validate command."""
        # Implementation
        pass
    
    def _execute_sandboxed(self, parsed: dict) -> TerminalMetric:
        """Execute with resource limits."""
        # Implementation with timeout, output limits
        pass
    
    def _audit_log(self, metric: TerminalMetric) -> None:
        """Log execution for security/science."""
        # Implementation
        pass
    
    def _format_result(self, metric: TerminalMetric) -> SpecialistResult:
        """Format output for LLM consumption."""
        # Implementation
        pass
```

### File: `tests/test_terminal_specialist.py`

**Test Categories:**

```python
class TestTerminalSpecialistSafety:
    """Verify security constraints."""
    def test_rejects_disallowed_commands()
    def test_prevents_path_traversal()
    def test_prevents_shell_injection()
    def test_enforces_output_limit()
    def test_enforces_timeout()
    def test_sanitizes_environment()

class TestTerminalSpecialistFunctionality:
    """Verify correct operation."""
    def test_git_status_works()
    def test_ls_listing_works()
    def test_pytest_discovery_works()
    def test_parses_output_correctly()
    def test_handles_missing_command()

class TestTerminalMetrics:
    """Verify measurement capture (Phase B)."""
    def test_latency_measurement()
    def test_groundedness_scoring()
    def test_cognitive_load_measurement()
    def test_audit_log_format()
```

---

## Implementation Timeline

**Today (Sprint 1 - "Make it work"):**
- [ ] Create TerminalSpecialist skeleton with allowed commands
- [ ] Implement safety validation layer
- [ ] Add basic git/ls support
- [ ] Write 10+ unit tests
- [ ] Deploy to testing

**Tomorrow (Sprint 2 - "Make it safe"):**
- [ ] Full security audit
- [ ] Audit logging implementation
- [ ] Error handling for all edge cases
- [ ] Integration with bidirectional handler
- [ ] Load test with malicious inputs

**This Week (Sprint 3 - "Make it scientific"):**
- [ ] Implement TerminalMetric measurement
- [ ] Build Phase B experiment harness
- [ ] Run 3-mode comparison (codebase vs codebase+terminal vs full)
- [ ] Publish findings to research docs

---

## Connection to Existing Infrastructure

### Registry Entry (`.ai/specialist-registry.json`)
```json
{
  "terminal": {
    "class_name": "TerminalSpecialist",
    "file": "brain/specialists/terminal_specialist.py",
    "description": "Execute safe terminal commands for grounded context access",
    "activation_type": "bidirectional-only",
    "activation_trigger": "<terminal_command>command</terminal_command>",
    "context_priority": "CRITICAL",
    "safety_level": "HIGH",
    "phase": "layer4",
    "research_connection": "Phase B LLM↔LLM communication + hallucination reduction"
  }
}
```

### Documentation
- `docs/layer4_terminal_specialist.rst` - User guide
- `docs/research/phase_b_groundedness_experiment.rst` - Science guide
- `.ai/handoffs/layer4-terminal-implementation.md` - Implementation handoff

---

## Science Questions This Unlocks

1. **Does grounded access reduce hallucination?**
   - Hypothesis: LLMs with terminal access will make fewer false claims about codebase state
   - Measurement: Compare accuracy across modes A/B/C

2. **What's the optimal grounding frequency?**
   - Hypothesis: Every 3-4 turns of grounding might be optimal
   - Measurement: Run experiments with different grounding intervals

3. **Can we measure "confidence calibration"?**
   - Hypothesis: Grounded LLMs will hedge appropriately
   - Measurement: Analyze confidence language patterns

4. **Token cost vs accuracy trade-off?**
   - Hypothesis: Terminal output is more "dense" than natural language
   - Measurement: Compare token efficiency across modes

---

## References

- **Phase 9-22 Research**: Context-matching beat strategy (r=0.924)
- **CodebaseSpecialist Learnings**: Read-only + pre-indexed = fast + safe
- **Demo Results**: 8/8 lookups <100ms with 87.5% docstring presence
- **luna's Vision**: "teach ada how to use safe commands"

---

**Next Action**: Implement Phase 1 ✨
