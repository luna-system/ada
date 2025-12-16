# Ada v1 - Conversational LLM with RAG

Ada is a conversational AI system featuring Retrieval-Augmented Generation (RAG), extensible specialist plugins, and real-time streaming responses.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.13+ and uv for local development

### Start All Services

```bash
docker compose up
```

Then visit:
- **Frontend:** http://localhost:5000
- **Documentation:** http://localhost:5000/docs/
- **System Info:** http://localhost:5000/api/info
- **Data Schemas:** http://localhost:5000/api/schema
- **Specialists:** http://localhost:5000/api/specialists
- **Health Check:** http://localhost:5000/api/healthz

### Run Tests

```bash
./scripts/run.sh test
```

## 📚 Documentation

**Full documentation is served at http://localhost:5000/docs** when running via Docker Compose.

Documentation is automatically built during the frontend build process. To rebuild:

```bash
docker compose build web
docker compose up -d web
```

**Quick Links:**

- **[Getting Started](docs/getting_started.rst)** - Installation and configuration
- **[API Usage Guide](docs/api_usage.rst)** - Complete API reference with examples
- **[Specialist System](docs/specialists.rst)** - Extensible plugin architecture
- **[Testing Guide](docs/testing.rst)** - Running tests and adding new tests
- **[Development Tools](docs/development.rst)** - Scripts container and workflows
- **[Streaming](docs/streaming.rst)** - Server-Sent Events (SSE) streaming
- **[Memory](docs/memory.rst)** - RAG and memory management
- **[Examples](docs/examples.rst)** - Code examples and patterns

## 🏗️ Architecture

### Services

- **brain** - FastAPI backend with LLM orchestration
- **frontend** - Nginx + static frontend with SSE streaming
- **chroma** - Vector database for RAG
- **ollama** - LLM inference (DeepSeek-R1)
- **memory-consolidation** - Nightly memory summarization
- **scripts** - Tooling container for utilities and tests

### Key Features

✅ **Retrieval-Augmented Generation (RAG)** - Semantic search over persona, FAQ, memories, and conversation history  
✅ **Streaming Responses** - Real-time token delivery via Server-Sent Events  
✅ **Specialist Plugins** - Extensible capabilities (OCR, media, web search)  
✅ **Bidirectional Specialists** - LLM can request specialist execution mid-response  
✅ **Memory Consolidation** - Automatic nightly summarization  
✅ **Self-Documenting** - Introspectable schemas, specialists, and system capabilities  
✅ **Testing Infrastructure** - Pytest-based with containerized execution  
✅ **Type Safety** - Full type hints with Pylance validation

### 🔍 Introspection & Self-Documentation

Ada is designed to be fully self-describing through introspection endpoints:

- **`GET /v1/info`** - System version, features, capabilities, available endpoints
- **`GET /v1/specialists`** - List all specialist plugins with schemas and capabilities
- **`GET /v1/schema`** - JSON Schema definitions for all data models (Pydantic-based)
- **`GET /v1/schema?doc_type=memory`** - Specific schema for memory documents
- **`GET /v1/healthz`** - Detailed health check with dependency status

All data models are defined with Pydantic and exposed via `/v1/schema`, making the system fully introspectable at runtime. See [Data Model Reference](docs/data_model.rst) for complete documentation.  

## 🔌 Specialist System

Drop a new `*_specialist.py` file into `brain/specialists/` and it's automatically discovered:

```python
from .protocol import BaseSpecialist, SpecialistCapability

class MySpecialist(BaseSpecialist):
    def should_activate(self, request_context: dict) -> bool:
        return request_context.get('my_trigger') is not None
    
    async def process(self, **kwargs) -> SpecialistResult:
        # Your logic here
        return self.success_result(context_text="Results...")
```

**Current Specialists:**
- 📄 **OCR** - Extract text from images (Tesseract)
- 🎧 **Media** - ListenBrainz music context
- 🔍 **Web Search** - Real-time web search via SearxNG

See [Specialist System](docs/specialists.rst) for full documentation.

## 🧪 Testing

Run the full test suite:

```bash
# All tests
./scripts/run.sh test

# Specific test file
docker compose run --rm scripts pytest tests/test_rag.py

# With verbose output
docker compose run --rm scripts pytest -vv

# Pattern matching
docker compose run --rm scripts pytest -k "memory"
```

**Current Test Coverage:**
- ✅ RAG retrieval (6 tests)
- ✅ Prompt building (2 tests)
- ✅ Specialist system (1 test)
- ⚠️ Need: API endpoint tests, error handling tests

See [Testing Guide](docs/testing.rst) for details.

## 🛠️ Development

### Scripts Container

All utility scripts run in a dedicated container for consistency:

```bash
./scripts/run.sh health        # Health check
./scripts/run.sh test          # Run tests
./scripts/run.sh shell         # Python REPL
./scripts/run.sh migrate       # Database migration
./scripts/run.sh bash          # Bash shell
```

See [Development Tools](docs/development.rst) for full reference.

### Local Development

```bash
# Install dependencies
uv sync --extra dev

# Run backend locally
source .venv/bin/activate
python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000 --reload

# Run tests locally (not recommended, use container instead)
pytest
```

### Adding New Features

1. Write feature code
2. Add tests in `tests/test_<feature>.py`
3. Run tests: `./scripts/run.sh test`
4. Update documentation
5. Create pull request

## 📖 API Quick Reference

### Health Check

```bash
curl http://localhost:7000/v1/healthz
```

### Chat (Streaming)

```bash
curl -N -X POST http://localhost:7000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "conversation_id": "chat-1"}'
```

### Memory Search

```bash
curl "http://localhost:7000/v1/memory?query=preferences&limit=5"
```

### Create Memory

```bash
curl -X POST http://localhost:7000/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "User likes Python", "memory_type": "fact"}'
```

See [API Usage Guide](docs/api_usage.rst) for complete documentation.

## 🌐 Environment Variables

Key configuration in `.env`:

```bash
# LLM Backend
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-r1:14b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Vector Database
CHROMA_URL=http://chroma:8000

# Optional Features
SEARXNG_URL=https://hunt.airsi.de        # Web search
LISTENBRAINZ_USER=your_username          # Music context
LISTENBRAINZ_TOKEN=your_token
RAG_DEBUG=true                           # Debug endpoints
```

## 📦 Project Structure

```
ada-v1/
├── brain/              # FastAPI backend
│   ├── app.py         # Main application
│   ├── config.py      # Configuration
│   ├── rag_store.py   # RAG/Chroma integration
│   ├── llm.py         # LLM interface
│   ├── prompt_builder.py
│   └── specialists/   # Plugin system
├── frontend/          # Static frontend + Nginx
├── tests/             # Pytest test suite
├── scripts/           # Utility scripts
├── docs/              # Sphinx documentation
├── seed/              # Initial data
└── compose.yaml       # Docker services
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run test suite: `./scripts/run.sh test`
6. Submit a pull request

## 📄 License

**CC0 1.0 Universal - Public Domain Dedication**

This software has been dedicated to the public domain under CC0 1.0 Universal.

⚠️ **Provenance Notice:** This software was developed with the assistance of generative AI models and has been dedicated to the public domain by its creators.

See [LICENSE](LICENSE) for full legal text.

## 🔗 Resources

- **Documentation:** `docs/_build/html/index.html` (build with `make html`)
- **API Docs:** http://localhost:7000/docs (interactive Swagger UI)
- **FastAPI:** https://fastapi.tiangolo.com/
- **Chroma:** https://www.trychroma.com/
- **Ollama:** https://ollama.ai/

## 🆘 Support

- Check [Getting Started](docs/getting_started.rst) for setup help
- See [Troubleshooting](docs/development.rst#troubleshooting) for common issues
- Run health check: `./scripts/run.sh health`
- View logs: `docker compose logs brain`

---

Built with ❤️ by Luna Team
