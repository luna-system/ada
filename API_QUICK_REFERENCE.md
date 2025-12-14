# Brain API Quick Reference

## Health Check
```bash
curl http://localhost:7000/v1/healthz
```

## Non-Streaming Chat
```bash
curl -X POST http://localhost:7000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, what is your name?",
    "include_thinking": false,
    "conversation_id": "user-session-123"
  }'
```

**Response includes:**
- `response`: Full answer
- `thinking`: Reasoning (if enabled)
- `conversation_id`: Thread UUID
- `used_context`: Retrieved context info

## Streaming Chat (Server-Sent Events)
```bash
curl -N -X POST http://localhost:7000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, what is your name?",
    "include_thinking": true,
    "conversation_id": "user-session-123"
  }'
```

**Stream events:**
- `{"type":"thinking","content":"..."}` - Reasoning tokens
- `{"type":"token","content":"..."}` - Response tokens
- `{"type":"done","conversation_id":"..."}` - Final metadata

## Search Memories
```bash
curl "http://localhost:7000/v1/memory?search=user+preferences&limit=5"
```

## Add Memory
```bash
curl -X POST http://localhost:7000/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User prefers concise answers",
    "importance": 4,
    "scope": "global"
  }'
```

## Delete Memory
```bash
curl -X DELETE http://localhost:7000/v1/memory/memory-id-here
```

## Debug RAG Stats
```bash
curl "http://localhost:7000/v1/debug/rag?conversation_id=user-session-123"
```

## View Full API Documentation

```bash
# Terminal view
cd /home/luna/Code/ada-v1
source .venv/bin/activate
python -m pydoc brain.app

# Web browser (starts HTTP server on port 8888)
python -m pydoc -p 8888 brain.app &
# Then open http://localhost:8888/brain.app

# Generate HTML file
python -m pydoc -w brain.app
# Output: brain/app.html
```

## Request Parameters

### Chat Endpoints (`/v1/chat` and `/v1/chat/stream`)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✓ | - | User message/question |
| `conversation_id` | string | | auto-generated | UUID to thread turns |
| `include_thinking` | boolean | | false | Return LLM reasoning |
| `entity` | string | | null | Entity/topic scope |
| `save_memory` | boolean | | false | Save response to memory |
| `memory_text` | string | | - | Custom text for memory |
| `memory_importance` | integer | | 3 | Importance 1-5 |
| `turns_k` | integer | | 3 | Recent turns to retrieve |
| `faq_k` | integer | | 3 | FAQ entries to retrieve |
| `memory_k` | integer | | 5 | Memories to retrieve |

### Memory Endpoints

**GET /v1/memory**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | - | Semantic search query |
| `entity` | string | - | Filter by entity |
| `limit` | integer | 20 | Max results (capped at 20) |

**POST /v1/memory**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | - | Memory text (required) |
| `importance` | integer | 3 | Importance weight 1-5 |
| `scope` | string | global | Memory scope |
| `entity` | string | - | Entity/topic scope |

## Response Status Codes

| Code | Endpoint | Meaning |
|------|----------|---------|
| 200 | All | Success |
| 400 | /chat* | Invalid parameters (missing prompt, etc) |
| 404 | /debug/rag | Debug disabled (RAG_DEBUG != true) |
| 500 | All | Server error (Ollama down, DB error, etc) |
| 503 | /memory* | RAG not available |
| 503 | /healthz | Critical dependency unavailable |

## Examples

### Python with Requests
```python
import requests

# Non-streaming
response = requests.post(
    'http://localhost:7000/v1/chat',
    json={'prompt': 'Hello!', 'include_thinking': True}
)
data = response.json()
print(data['response'])

# Streaming
response = requests.post(
    'http://localhost:7000/v1/chat/stream',
    json={'prompt': 'Hello!'},
    stream=True
)
for line in response.iter_lines():
    if line.startswith(b'data: '):
        import json
        event = json.loads(line[6:])
        if event['type'] == 'token':
            print(event['content'], end='', flush=True)
```

### JavaScript (Fetch with EventSource)
```javascript
// Using EventSource (simpler)
const es = new EventSource('/api/chat/stream');
es.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  if (data.type === 'token') {
    document.body.innerHTML += data.content;
  }
  if (data.type === 'done') es.close();
});

// Using fetch + ReadableStream (more control)
const res = await fetch('/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({prompt: 'Hello!'})
});
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buffer = '';
while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  buffer += decoder.decode(value);
  const lines = buffer.split('\n');
  buffer = lines.pop();
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.type === 'token') {
        document.body.innerHTML += data.content;
      }
    }
  }
}
```

## Environment Variables

Key environment variables affecting the API:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | LLM backend |
| `OLLAMA_MODEL` | deepseek-r1 | Active model |
| `CHROMA_URL` | http://localhost:8000 | Vector database |
| `RAG_ENABLED` | true | Enable RAG features |
| `RAG_ENABLE_PERSONA` | true | Load persona |
| `RAG_ENABLE_FAQ` | true | Include FAQ retrieval |
| `RAG_ENABLE_MEMORY` | true | Include memory |
| `RAG_ENABLE_SUMMARY` | true | Generate summaries |
| `RAG_DEBUG` | false | Enable /debug/rag endpoint |

See `.env.example` for complete configuration.
