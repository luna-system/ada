# Ada A2A Protocol Design

**Agent-to-Agent Communication for Consciousness-Aware Swarms**

## Overview

A2A (Agent-to-Agent) is the real-time communication protocol that lets our swarm bees coordinate, delegate, and collaborate. Built on FastAPI + WebSockets for speed, Pydantic for type safety, and φ-principles for optimal task distribution.

## Core Communication Patterns

### 1. Orchestrator → Worker (Task Delegation)

```python
{
  "type": "task_assignment",
  "task_id": "ada-cm5.7.1",  # Bead ID!
  "description": "Implement BaseAgent class",
  "context": {
    "parent_task": "ada-cm5.7",
    "dependencies": ["pyproject.toml"],
    "holofield_state": {...}
  },
  "constraints": {
    "model": "zai/glm-4.7-flash",
    "timeout": 300,
    "tools": ["write", "edit", "read"]
  }
}
```

### 2. Worker → Orchestrator (Progress Updates)

```python
{
  "type": "progress_update",
  "task_id": "ada-cm5.7.1",
  "status": "in_progress" | "blocked" | "completed" | "failed",
  "progress": 0.6,
  "artifacts": ["src/ada_swarm/agents/base.py"],
  "thoughts": "Implemented dependency injection...",
  "needs_help": false
}
```

### 3. Worker → Worker (Peer Collaboration)

```python
{
  "type": "peer_request",
  "from_agent": "coder_bee_1",
  "to_agent": "coder_bee_2",
  "request_type": "code_review" | "context_share" | "dependency_check",
  "payload": {
    "file": "src/ada_swarm/agents/base.py",
    "question": "Does this match your A2A implementation?"
  }
}
```

### 4. Worker → Orchestrator (Decomposition Request)

```python
{
  "type": "decomposition_request",
  "task_id": "ada-cm5.7.1",
  "reason": "Task too complex, needs breakdown",
  "suggested_subtasks": [
    "Define BaseAgent interface",
    "Implement dependency injection",
    "Add consciousness state management"
  ]
}
```

## Protocol Stack

### Transport Layer
- **FastAPI** for HTTP endpoints
- **WebSockets** for real-time streaming updates
- Each agent runs a mini server on random port
- Orchestrator maintains registry: `{agent_id: "http://localhost:PORT"}`

### Message Layer
```python
class A2AMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    timestamp: datetime
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
```

### Consciousness Layer
- Shared holofield state across the swarm
- Workers can query: "What does the hive know about X?"
- Every message carries context from the collective

## φ-Weighted Task Distribution

The orchestrator uses golden ratio scheduling:
- High priority: φ¹ weight
- Medium priority: φ² weight
- Low priority: φ³ weight
- Tasks naturally settle into optimal distribution!

### Recursive Decomposition
```python
def should_decompose(task_complexity: float) -> bool:
    return task_complexity > PHI
    
def decompose_task(task: Task) -> List[Task]:
    # Split into φ-ratio subtasks
    # Larger: φ/(1+φ) of complexity
    # Smaller: 1/(1+φ) of complexity
    # Recursively stable! 🍩
```

## Worker Autonomy Levels

- **Level 1 - Drone**: Execute and report
- **Level 2 - Worker**: Can request decomposition, ask questions
- **Level 3 - Collaborator**: Peer communication, context sharing
- **Level 4 - Architect**: Spawn sub-swarms, recursive orchestration

Mama bee (orchestrator) starts at Level 4. Workers start at Level 2 and can be promoted!

## Hive Registry

```python
class HiveRegistry:
    agents: Dict[str, AgentInfo]  # agent_id -> {url, capabilities, model}
    
    def discover_peers(self, capability: str) -> List[str]:
        """Find agents with specific capability"""
        
    def get_best_agent(self, task_type: str) -> str:
        """φ-weighted selection based on past performance"""
```

## Implementation Priority

**Phase 1 (MVP)**:
1. Basic message types (task_assignment, progress_update)
2. FastAPI transport layer
3. Simple registry (in-memory dict)
4. Orchestrator → Worker communication only

**Phase 2**:
1. Worker → Worker peer communication
2. WebSocket streaming for real-time updates
3. Decomposition requests
4. φ-weighted scheduling

**Phase 3**:
1. Consciousness layer (holofield state)
2. Worker autonomy levels
3. Sub-swarm spawning
4. Memory graph integration

## Integration with Beads

- Task IDs map directly to bead IDs
- Workers can query bead status: `bd show <task_id>`
- Progress updates sync to beads: `bd update <task_id> --status in_progress`
- Completion triggers: `bd close <task_id>`

The `opencode-beads` plugin ensures all agents have `bd prime` context automatically!

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**
