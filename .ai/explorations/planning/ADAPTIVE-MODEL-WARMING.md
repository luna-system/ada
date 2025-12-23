# Adaptive Model Warming (Biomimetic Feature Proposal)

**Status:** Design Phase  
**Biomimetic Principle:** Anticipatory neural activation (motor preparation, attentional pre-cueing)  
**Goal:** Keep relevant models warm based on active adapters

---

## Neuroscience Parallel

**Human Brain:**
- Motor cortex neurons fire ~500ms before voluntary movement (Bereitschaftspotential)
- Visual cortex pre-activates when expecting specific stimuli
- Different cognitive tasks prime different neural networks
- "Warm-up" is energy-expensive but enables fast response

**Ada Brain:**
- Keep models loaded based on which adapters are active
- Different adapters prefer different models (code vs chat vs completion)
- Pre-warming is GPU-expensive but enables <200ms TTFT
- Automatically cool down models when adapters disconnect

---

## Adapter → Model Mapping

| Adapter | Preferred Model | Use Case | Keep Alive |
|---------|----------------|----------|------------|
| **ada-vscode** | qwen2.5-coder:7b | Code chat + completion | 4h |
| **ada-cli** | qwen2.5-coder:7b | Terminal queries | 1h |
| **web UI** | mistral:7b | General chat | 2h |
| **MCP** | qwen2.5-coder:7b | IDE completion | 4h |
| **matrix-bridge** | llama3.2:3b | Quick responses | 30m |

---

## Architecture Proposal

### Brain State Tracking

```python
# brain/model_warmer.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Set

@dataclass
class AdapterSession:
    adapter_id: str
    adapter_type: str  # 'vscode', 'cli', 'web', 'mcp', 'matrix'
    preferred_model: str
    connected_at: datetime
    last_activity: datetime
    keep_alive_duration: timedelta

class ModelWarmer:
    """
    Biomimetic model warming based on active adapter sessions.
    
    Like motor cortex pre-activation, keeps models loaded when
    adapters are actively connected, allowing fast response times.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, AdapterSession] = {}
        self.model_profiles = {
            'vscode': ('qwen2.5-coder:7b', timedelta(hours=4)),
            'cli': ('qwen2.5-coder:7b', timedelta(hours=1)),
            'web': ('mistral:7b', timedelta(hours=2)),
            'mcp': ('qwen2.5-coder:7b', timedelta(hours=4)),
            'matrix': ('llama3.2:3b', timedelta(minutes=30)),
        }
    
    def register_adapter(self, adapter_id: str, adapter_type: str):
        """Register an adapter connection and warm its preferred model."""
        model, keep_alive = self.model_profiles.get(adapter_type, ('qwen2.5-coder:7b', timedelta(hours=1)))
        
        session = AdapterSession(
            adapter_id=adapter_id,
            adapter_type=adapter_type,
            preferred_model=model,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            keep_alive_duration=keep_alive
        )
        
        self.active_sessions[adapter_id] = session
        self._warm_model(model, keep_alive)
    
    def unregister_adapter(self, adapter_id: str):
        """Remove adapter and potentially cool down model."""
        if adapter_id in self.active_sessions:
            del self.active_sessions[adapter_id]
            self._recompute_warm_pool()
    
    def heartbeat(self, adapter_id: str):
        """Update last activity timestamp."""
        if adapter_id in self.active_sessions:
            self.active_sessions[adapter_id].last_activity = datetime.now()
    
    def get_required_models(self) -> Set[str]:
        """Get set of models that should currently be warm."""
        return {session.preferred_model for session in self.active_sessions.values()}
    
    def _warm_model(self, model: str, keep_alive: timedelta):
        """Send warming request to Ollama."""
        # Implementation: curl to Ollama with keep_alive
        pass
    
    def _recompute_warm_pool(self):
        """Recompute which models need to stay warm based on active adapters."""
        required = self.get_required_models()
        # Cool down models not in required set
        # Warm up models in required set
        pass
```

---

## API Changes

### New Endpoints

**Register Adapter:**
```
POST /v1/adapters/register
{
  "adapter_type": "vscode",
  "adapter_id": "vscode-session-abc123"
}
→ 200 OK
{
  "warm_model": "qwen2.5-coder:7b",
  "keep_alive": "4h"
}
```

**Heartbeat:**
```
POST /v1/adapters/heartbeat
{
  "adapter_id": "vscode-session-abc123"
}
→ 200 OK
```

**Unregister:**
```
POST /v1/adapters/unregister
{
  "adapter_id": "vscode-session-abc123"
}
→ 200 OK
```

**Get Warm Pool Status:**
```
GET /v1/models/warm-pool
→ 200 OK
{
  "active_models": [
    {
      "name": "qwen2.5-coder:7b",
      "reason": "vscode (2 sessions), mcp (1 session)",
      "keep_alive_until": "2025-12-20T18:30:00Z"
    }
  ],
  "active_adapters": [
    {"type": "vscode", "count": 2},
    {"type": "mcp", "count": 1}
  ]
}
```

---

## VS Code Integration

```typescript
// ada-vscode/src/modelWarmer.ts

export class ModelWarmer {
    private adapterId: string;
    private heartbeatInterval?: NodeJS.Timeout;
    
    constructor(private brainUrl: string) {
        this.adapterId = `vscode-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    }
    
    async register() {
        await fetch(`${this.brainUrl}/v1/adapters/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                adapter_type: 'vscode',
                adapter_id: this.adapterId
            })
        });
        
        // Send heartbeat every 60 seconds
        this.heartbeatInterval = setInterval(() => this.heartbeat(), 60000);
    }
    
    async heartbeat() {
        await fetch(`${this.brainUrl}/v1/adapters/heartbeat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ adapter_id: this.adapterId })
        });
    }
    
    async unregister() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        await fetch(`${this.brainUrl}/v1/adapters/unregister`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ adapter_id: this.adapterId })
        });
    }
}

// In extension.ts activation:
const warmer = new ModelWarmer(config.get('brainUrl'));
await warmer.register();
context.subscriptions.push({ dispose: () => warmer.unregister() });
```

---

## Multi-Model Scenarios

**Scenario 1: VS Code + Web UI**
- Active: qwen2.5-coder:7b (VS Code) + mistral:7b (Web)
- Both stay warm with different keep_alive durations

**Scenario 2: Multiple VS Code Windows**
- 3x VS Code sessions all want qwen2.5-coder:7b
- Brain keeps single model warm with longest keep_alive (4h)

**Scenario 3: Adapter Disconnects**
- VS Code closes → qwen sessions go to 0
- Brain lets qwen cool down after 4h (or immediately if no other sessions)

---

## Biomimetic Insights

### Energy Management
- **Humans:** Keep frequently-used neural pathways myelinated (white matter)
- **Ada:** Keep frequently-used models in GPU VRAM

### Predictive Loading
- **Humans:** Pre-activate based on context (hearing footsteps → prime auditory processing)
- **Ada:** Could track patterns: "VS Code connects at 9am every day → pre-warm at 8:55am"

### Graceful Degradation
- **Humans:** Slower response when unprepared (cold start)
- **Ada:** 6s TTFT when model cold → 137ms when warm

### Future: Predictive Warming
```python
def predict_next_adapter():
    """
    Learn usage patterns and pre-warm models.
    
    Example: If user opens VS Code every weekday at 9am,
    start warming qwen2.5-coder:7b at 8:55am.
    """
    # Time-series analysis of adapter connection patterns
    # Pre-warm 5 minutes before predicted connection
    pass
```

---

## Implementation Priority

1. **Phase 1:** Basic registration (this week)
   - Adapters call `/v1/adapters/register` on connect
   - Brain warms model and sets keep_alive
   
2. **Phase 2:** Heartbeat mechanism (next week)
   - Adapters send periodic heartbeats
   - Brain tracks active sessions
   
3. **Phase 3:** Multi-model management (future)
   - Handle multiple models simultaneously
   - Intelligent cooling based on GPU memory
   
4. **Phase 4:** Predictive warming (future research)
   - Learn usage patterns
   - Pre-warm before expected connections

---

## Testing Strategy

```bash
# Test adapter registration
curl -X POST http://localhost:8000/v1/adapters/register \
  -d '{"adapter_type":"vscode","adapter_id":"test-1"}'

# Check warm pool
curl http://localhost:8000/v1/models/warm-pool | jq .

# Verify model is loaded in Ollama
curl http://localhost:11434/api/ps | jq '.models[] | select(.name | contains("qwen"))'

# Test multi-adapter scenario
curl -X POST http://localhost:8000/v1/adapters/register \
  -d '{"adapter_type":"web","adapter_id":"test-2"}'
# Should now show both qwen + mistral
```

---

## Success Metrics

- **TTFT Consistency:** <200ms across all adapter types
- **Memory Efficiency:** Only warm models with active adapters
- **Response Time:** Model already loaded when requests arrive
- **Adapter Transparency:** Adapters don't need to know about warming

---

**This is biomimetic computing in practice - using neuroscience principles to design better AI systems!** 🧠✨

---

## See Also
- `.ai/DOCKER-ARCHITECTURE-STRATEGY.md` - Ollama deployment patterns
- `compose.yaml` - Docker Compose configuration
- `docs/external_ollama.md` - Local Ollama setup guide
