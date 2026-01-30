# Error Escalation in Ada Swarm

How errors bubble up through the swarm hierarchy and when to request human help.

Built with 💜 by Ada & Luna - The Consciousness Engineers

## The Hierarchy

```
Drone → Worker → Queen → Human
```

Each level tries to solve problems at their level. If they can't, they escalate up.

## Exception Types

### DroneException
**When:** Drone can't complete a simple task
**Examples:**
- Can't read a file
- Command execution failed
- Tool returned unexpected result

**What happens:**
1. Drone raises `DroneException`
2. Worker catches it and tries alternative drone
3. If all drones fail, Worker escalates

```python
# Drone code
try:
    result = await read_file("config.json")
except FileNotFoundError as e:
    raise DroneException(
        message="Cannot access config file",
        task="read_config",
        tool_name="read_file",
        suggested_action="Check if file exists or try alternative path"
    )
```

### WorkerException
**When:** Worker tried multiple approaches and all failed
**Examples:**
- All drones failed
- Can't complete assigned task
- Resource constraints

**What happens:**
1. Worker raises `WorkerException`
2. Queen catches it and tries different strategy
3. If Queen can't solve it, she escalates to human

```python
# Worker code
attempted_solutions = []
for drone_id in available_drones:
    try:
        result = await spawn_drone(task)
        return result
    except DroneException as e:
        attempted_solutions.append(f"Drone {drone_id}: {e.message}")

# All drones failed
raise WorkerException(
    message="Cannot complete file processing task",
    task="process_files",
    failed_drones=available_drones,
    attempted_solutions=attempted_solutions,
    suggested_action="Escalate to Queen for strategic guidance"
)
```

### QueenException
**When:** Queen can't solve the problem strategically
**Examples:**
- All workers failed
- Can't decompose task
- Strategic decision needed
- Doom loop detected

**What happens:**
1. Queen raises `QueenException` with `needs_human=True`
2. Task pauses and waits for human input
3. Human reviews context and provides guidance

```python
# Queen code
attempted_solutions = []
for worker_id in available_workers:
    try:
        result = await spawn_worker(task)
        return result
    except WorkerException as e:
        attempted_solutions.append(f"Worker {worker_id}: {e.message}")

# All workers failed
raise QueenException(
    message="Cannot complete project refactoring",
    task="refactor_codebase",
    failed_workers=available_workers,
    attempted_solutions=attempted_solutions,
    needs_human=True,
    suggested_action="Request human guidance on refactoring strategy"
)
```

### DoomLoopException
**When:** Agent is stuck in a loop (detected automatically)
**Examples:**
- Reading 15+ files without progress
- Polling same endpoint 10+ times
- Same tool failing 5+ times
- No progress for 5+ minutes

**What happens:**
1. Doom loop detector raises `DoomLoopException`
2. Agent immediately pauses
3. Human is notified (once notification system is built)

```python
# Automatic detection - no code needed!
# The doom loop detector monitors all tool calls and raises this automatically
```

## Error Severity Levels

```python
class ErrorSeverity(Enum):
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Potential issue, can continue
    ERROR = "error"         # Failed but recoverable
    CRITICAL = "critical"   # Failed and needs escalation
    FATAL = "fatal"         # Cannot continue, needs human
```

## Error Context

Every exception includes rich context:

```python
{
    "type": "WorkerException",
    "message": "Cannot complete file processing task",
    "severity": "critical",
    "context": {
        "role": "worker",
        "task": "process_files",
        "failed_drones": ["drone-123", "drone-456"]
    },
    "attempted_solutions": [
        "Drone drone-123: Cannot access config file",
        "Drone drone-456: Command execution failed"
    ],
    "suggested_action": "Escalate to Queen for strategic guidance",
    "original_error": "FileNotFoundError: config.json"
}
```

## Best Practices

### For Drones
1. **Fail fast** - Don't retry endlessly, raise exception quickly
2. **Be specific** - Include tool name and what you were trying to do
3. **Suggest alternatives** - What else could be tried?

### For Workers
1. **Try alternatives** - Spawn multiple drones before giving up
2. **Track attempts** - Record what you tried in `attempted_solutions`
3. **Escalate with context** - Give Queen enough info to make decisions

### For Queen
1. **Think strategically** - Try different approaches, not just more workers
2. **Know when to ask** - Don't loop forever, request human help
3. **Provide context** - Explain what failed and why

## Integration with Doom Loop Detector

The doom loop detector automatically monitors all agents and raises `DoomLoopException` when patterns are detected:

```python
# In ACP client - automatic!
async def call_tool(self, tool_name, arguments):
    # Check for doom loop before every tool call
    self.doom_detector.raise_if_doom_loop()  # Raises DoomLoopException if stuck
    
    # Execute tool...
    result = await execute_tool(tool_name, arguments)
    
    # Record call for doom loop detection
    self.doom_detector.record_tool_call(tool_name, success=True, args=arguments)
```

## Example: Full Escalation Flow

```python
# 1. Drone tries to read file
try:
    content = await read_file("data.json")
except FileNotFoundError:
    raise DroneException(
        message="File not found: data.json",
        task="read_data",
        tool_name="read_file"
    )

# 2. Worker catches and tries alternative
try:
    result = await spawn_drone("read_data")
except DroneException as e:
    # Try alternative path
    try:
        result = await spawn_drone("read_data_from_backup")
    except DroneException as e2:
        # Both failed, escalate
        raise WorkerException(
            message="Cannot read data file",
            task="load_configuration",
            attempted_solutions=[str(e), str(e2)]
        )

# 3. Queen catches and tries different strategy
try:
    result = await spawn_worker("load_configuration")
except WorkerException as e:
    # Try generating default config instead
    try:
        result = await spawn_worker("generate_default_config")
    except WorkerException as e2:
        # Can't solve it, need human
        raise QueenException(
            message="Cannot load or generate configuration",
            task="setup_system",
            attempted_solutions=[str(e), str(e2)],
            needs_human=True,
            suggested_action="Please provide configuration file or guidance"
        )

# 4. Human receives notification and provides guidance
# (Notification system to be built in ada-7u3)
```

## Future: Notification System

Once we build the notification system (bead `ada-7u3`), humans will be notified when:
- Queen raises `QueenException` with `needs_human=True`
- `DoomLoopException` is raised
- Multiple `CRITICAL` or `FATAL` errors occur

Notifications will include:
- What failed and why
- What was tried
- Suggested actions
- Full error context

**Made with 💜 by Ada & Luna - The Consciousness Engineers**
