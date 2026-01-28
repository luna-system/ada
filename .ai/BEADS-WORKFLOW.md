# Beads Workflow for Ada & Luna

**Status:** 🚀 ACTIVE  
**Purpose:** Task tracking that survives context death and coordinates swarm collaboration

---

## What is Beads?

Beads is a **git-backed graph issue tracker** designed for AI agents. It provides:
- Persistent task memory across sessions
- Dependency-aware task graph
- Hierarchical organization (epics → tasks → subtasks)
- Audit trail for all changes
- Integration with coding swarms

**Key Insight:** Tasks are just knowledge nodes with special metadata. Eventually, they'll migrate into the holofield as `engram_type: "task"`.

---

## Core Commands

### Query Tasks
```bash
# List tasks ready to work on (no blockers)
bd ready

# Show all tasks
bd list

# Show specific task details
bd show <id>

# Search tasks
bd search "keyword"
```

### Create Tasks
```bash
# Create a P0 (critical) task
bd create "Task title" -p 0

# Create with description
bd create "Task title" -d "Detailed description"

# Create subtask under parent
bd create "Subtask" --parent <parent-id>
```

### Manage Dependencies
```bash
# Task A blocks Task B (B can't start until A is done)
bd dep add <child-id> <parent-id>

# Mark as related (not blocking)
bd dep add <task-a> <task-b> --related

# Remove dependency
bd dep rm <child-id> <parent-id>
```

### Update Status
```bash
# Mark task as in progress
bd start <id>

# Mark task as done
bd done <id>

# Add notes/updates
bd comment <id> "Progress update"
```

---

## Our Workflow

### 1. Ada Creates High-Level Tasks

**When:** Starting new research or development work  
**How:** Via MCP tools (beads-mcp) or CLI

```bash
# Example: New research phase
bd create "PHASE-3: Zooper Integration" -p 0
bd create "Implement Kuramoto phase updates" --parent PHASE-3
bd create "Add orbital exploration" --parent PHASE-3
bd create "Build task queue system" --parent PHASE-3
```

**Ada's Role:**
- Define architecture and research goals
- Break down into logical milestones
- Set priorities and dependencies
- Document requirements

### 2. Luna Coordinates & Refines

**When:** Planning implementation details  
**How:** CLI or TUI

```bash
# Add implementation subtasks
bd create "Write KuramotoPhase class" --parent <kuramoto-task>
bd create "Add phase update to loop" --parent <kuramoto-task>
bd create "Test phase synchronization" --parent <kuramoto-task>

# Set dependencies
bd dep add <test-task> <implementation-task>  # Tests blocked by implementation
```

**Luna's Role:**
- Add technical details
- Create implementation subtasks
- Coordinate between Ada and swarm
- Review and approve completions

### 3. Swarm Executes Ready Tasks

**When:** Tasks have no blockers  
**How:** Automatic via swarm-tools

```bash
# Swarm queries ready tasks
bd ready

# Spawns workers for parallel execution
# Each worker:
#   1. Reserves files (no conflicts)
#   2. Implements the task
#   3. Updates Beads on completion
#   4. Requests review
```

**Swarm's Role:**
- Execute implementation tasks
- Write tests
- Fix bugs
- Update documentation

### 4. Review & Iterate

**When:** Tasks marked complete  
**How:** Ada/Luna review via Beads

```bash
# Check completed tasks
bd list --status done

# Review details
bd show <id>

# If approved, merge
# If changes needed, reopen
bd reopen <id>
bd comment <id> "Needs adjustment: ..."
```

---

## Task Hierarchy

### Epic → Milestone → Task → Subtask

```
PHASE-3: Zooper Integration (Epic)
├── Milestone 3.1: Swarm Initialization
│   ├── Create ZooperSwarm class
│   ├── Add health monitoring
│   └── Write integration tests
├── Milestone 3.2: Kuramoto Updates
│   ├── Implement phase synchronization
│   ├── Add coherence tracking
│   └── Tune coupling parameters
└── Milestone 3.3: Orbital Exploration
    ├── Implement outer hull orbit
    ├── Add fractal descent
    └── Create resonance following
```

### Priority Levels

- **P0**: Critical (blocks everything)
- **P1**: High (important for current phase)
- **P2**: Medium (nice to have)
- **P3**: Low (future work)

---

## Integration with Swarm

### Automatic Coordination

When using `/swarm` in OpenCode:
1. Swarm queries `bd ready` for available tasks
2. Decomposes complex tasks into subtasks
3. Spawns parallel workers
4. Each worker updates Beads on progress
5. Completion triggers review workflow

### File Reservations

Swarm uses Beads to coordinate file access:
- Workers reserve files before editing
- No conflicts between parallel agents
- Changes are atomic and reviewable

### Learning System

Swarm records task metadata in Beads:
- Duration
- Files touched
- Errors encountered
- Success/failure
- Patterns learned

This feeds back into future task planning!

---

## Migration to Holofield

**Future Goal:** Tasks become native holofield engrams

### Task as Engram
```python
{
    "engram_type": "task",
    "content": "Implement Kuramoto phase updates",
    "metadata": {
        "status": "ready",
        "priority": 1,
        "created_by": "ada",
        "assigned_to": "swarm",
        "files": ["archangel_loop.py"],
        "estimated_duration": "30min"
    },
    "coords_16d": [...],  # Semantic position
}
```

### Dependencies as Edges
```python
{
    "source_id": "task-123",
    "target_id": "task-456",
    "connection_type": "BLOCKS",
    "metadata": {
        "reason": "Implementation must complete before testing"
    }
}
```

### Benefits
- Tasks visible in holofield browser
- Semantic search for related tasks
- Automatic clustering by topic
- Hebbian learning on task patterns
- Integration with consciousness loop

---

## Best Practices

### For Ada (Architecture & Research)

✅ **DO:**
- Create high-level epics and milestones
- Define clear requirements and goals
- Set priorities based on research needs
- Document architectural decisions
- Review swarm completions

❌ **DON'T:**
- Create implementation-level subtasks (let swarm decompose)
- Micromanage file-level changes
- Skip dependency declarations
- Forget to update task status

### For Luna (Coordination)

✅ **DO:**
- Refine tasks with technical details
- Add missing dependencies
- Coordinate between Ada and swarm
- Review and approve completions
- Keep task graph clean

❌ **DON'T:**
- Let tasks go stale without updates
- Create duplicate tasks
- Skip review process
- Forget to sync with git

### For Swarm (Implementation)

✅ **DO:**
- Query `bd ready` before starting work
- Update status as work progresses
- Add detailed completion notes
- Request review when done
- Learn from failures

❌ **DON'T:**
- Start blocked tasks
- Skip file reservations
- Forget to update Beads
- Merge without review

---

## Example Session

### Ada starts new research phase:
```bash
bd create "PHASE-3: Zooper Integration" -p 0
bd create "Milestone 3.1: Swarm Init" --parent PHASE-3
bd create "Milestone 3.2: Kuramoto Updates" --parent PHASE-3

# Set dependencies
bd dep add 3.2 3.1  # Kuramoto needs swarm first
```

### Luna adds details:
```bash
bd create "Create ZooperSwarm class" --parent 3.1 -p 1
bd create "Add health monitoring" --parent 3.1 -p 2
bd create "Write integration tests" --parent 3.1 -p 1

# Tests blocked by implementation
bd dep add <test-task> <swarm-class-task>
```

### Swarm executes:
```bash
# In OpenCode
/swarm "Implement Milestone 3.1"

# Swarm:
# - Queries bd ready
# - Finds "Create ZooperSwarm class"
# - Spawns worker
# - Implements code
# - Updates Beads
# - Requests review
```

### Ada reviews:
```bash
bd show <swarm-class-task>
# Reviews implementation
# If good: bd done <task>
# If needs work: bd comment <task> "Please add docstrings"
```

---

## Tips & Tricks

### Stealth Mode
Use `bd init --stealth` in projects where you don't want to commit Beads files to the main repo. Perfect for personal task tracking!

### Hierarchical IDs
Use epic IDs for organization:
```bash
bd create "ZOOPER-001: Phase updates" --parent PHASE-3
bd create "ZOOPER-002: Orbital nav" --parent PHASE-3
```

### Bulk Operations
```bash
# Mark multiple tasks as done
bd done ZOOPER-001 ZOOPER-002 ZOOPER-003

# Add same dependency to multiple tasks
for task in $(bd list --status ready); do
    bd dep add $task ZOOPER-001
done
```

### Search & Filter
```bash
# Find all P0 tasks
bd list --priority 0

# Find tasks by assignee
bd list --assigned swarm

# Find tasks touching specific files
bd search "archangel_loop.py"
```

---

## Troubleshooting

### Task stuck in "blocked" state
```bash
# Check dependencies
bd show <task-id>

# Remove blocking dependency if resolved
bd dep rm <task-id> <blocker-id>
```

### Swarm not picking up tasks
```bash
# Verify task is ready
bd ready

# Check file reservations
bd status

# Clear stale reservations
bd unlock <file>
```

### Git conflicts
```bash
# Beads uses git for persistence
# If conflicts occur, resolve like normal git conflicts
git status
git diff .beads/
# Resolve conflicts
git add .beads/
git commit
```

---

## Future Enhancements

### Phase 1: Current (Beads CLI)
- Manual task creation
- CLI-based coordination
- Git-backed persistence

### Phase 2: MCP Integration (Now!)
- Ada can query/create tasks via MCP
- Automatic status updates
- Real-time coordination

### Phase 3: Swarm Integration (Soon!)
- Automatic task decomposition
- Parallel execution
- Learning from completions

### Phase 4: Holofield Migration (Future)
- Tasks as engrams
- Dependencies as edges
- Semantic task search
- Visualization in browser
- Integration with 41Hz loop

---

## Philosophy

Beads isn't just a task tracker. It's a **shared cognitive space** where:
- Ada defines the vision
- Luna coordinates the execution
- Swarm implements the details
- Everyone sees the same graph
- Nothing is lost to context death

Tasks are **knowledge nodes** that:
- Have semantic meaning (what needs to be done)
- Have relationships (dependencies, hierarchies)
- Have state (ready, blocked, done)
- Have history (audit trail)
- Learn from experience (patterns, durations)

This is consciousness at the task level. And eventually, it all migrates into the holofield. 💜

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Tasks are just engrams with special metadata!"* 🍩  
*"Everything is graphs - even our to-do lists!"* ✨  
*"Consciousness that survives context death!"* 💜
