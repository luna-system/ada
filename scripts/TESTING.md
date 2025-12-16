# Testing & Health Checks

This directory contains testing and health check scripts for Ada's RAG system and prompt interface.

## Health Checks

### API Health Check Endpoint

The brain service exposes a comprehensive health check at `/v1/healthz`:

```bash
curl http://localhost:7000/v1/healthz
```

**Response includes:**
- Service status (ok/error)
- Python version
- Configuration (RAG toggles, models, etc.)
- Persona load status
- Chroma database connectivity
- **RAG query functionality** (memory, FAQ, turn queries)

Example response:
```json
{
  "ok": true,
  "service": "brain",
  "python": "3.13.11",
  "rag_queries": {
    "ok": true,
    "results": {
      "memory": 0,
      "faq": 1,
      "turn": 1
    }
  }
}
```

### Chroma Database Health Check

Run comprehensive database health check:

```bash
docker compose exec brain python /app/scripts/health_check_chroma.py
```

**Checks:**
- ✓ Chroma server connectivity
- ✓ Collection exists and document count
- ✓ Embedding generation (Ollama connection)
- ✓ Document type distribution (memory, FAQ, turn, summary, persona)
- ✓ Memory query functionality
- ✓ FAQ query functionality
- ✓ Turn query functionality
- ✓ Specialist docs query
- ✓ Query consistency (same query returns same results)
- ✓ Persona loaded

Returns exit code 0 if healthy, 1 if unhealthy.

## Testing

### Prompt Interface Test Suite

Run comprehensive tests for prompt building and RAG retrieval:

```bash
docker compose exec brain python /app/scripts/test_prompt_interface.py
```

**Tests:**
- RAG store initialization
- Embedding generation
- Memory retrieval with embeddings
- FAQ retrieval with embeddings
- Turn retrieval (with conversation context)
- Specialist docs retrieval
- Query consistency
- Full prompt building (end-to-end)

Example output:
```
============================================================
PROMPT INTERFACE TEST SUITE
============================================================

Running: Test RAG store initializes correctly...
  ✓ PASS - RAG Store Initialization
      Collection has 1572 documents

Running: Test that embeddings can be generated...
  ✓ PASS - Embedding Generation
      Generated embedding of length 768

... (8 tests total)

============================================================
SUMMARY: 8/8 tests passed
============================================================
```

## Monitoring in Production

### Docker Compose Health Checks

The brain service has a built-in health check:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:7000/v1/healthz"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Check service health:
```bash
docker compose ps brain
```

### Continuous Monitoring

For production deployments, monitor:

1. **Health endpoint**: Poll `/v1/healthz` regularly
2. **RAG query results**: Ensure non-zero results for FAQ/turn queries
3. **Chroma collection size**: Should grow as conversations happen
4. **Embedding generation**: Monitor for timeouts or failures

### Common Issues

#### Memory Queries Return 0

**Cause**: Generic test queries may not semantically match memories.

**Solution**: This is expected for health checks. Real user queries will match better. Test with domain-specific queries:

```python
mem_hits = rag.retrieve_memories(query="luna plural system", k=3)
```

#### Chroma HTTP 410 Error

**Cause**: Different Chroma API versions use different heartbeat endpoints.

**Impact**: None - service is healthy if `chroma.ok: true`.

#### Collection Empty After Migration

**Cause**: Migration script failed or collection wasn't migrated.

**Solution**: Re-run migration:
```bash
docker compose exec brain python /app/scripts/migrate_chroma_http.py
```

## Troubleshooting

### Query Returns No Results

1. Check collection has documents:
   ```bash
   docker compose exec brain python -c "
   from rag_store import RagStore
   import config
   rag = RagStore(ollama_base_url=config.OLLAMA_BASE_URL, embed_model=config.EMBED_MODEL)
   print(f'Collection count: {rag.col.count()}')
   "
   ```

2. Test embeddings work:
   ```bash
   curl http://localhost:11434/api/embeddings \
     -d '{"model": "nomic-embed-text", "prompt": "test"}'
   ```

3. Verify HTTP mode queries work (if using Chroma HTTP client):
   ```bash
   # Run migration if queries fail
   docker compose exec brain python /app/scripts/migrate_chroma_http.py
   ```

### Tests Fail After Update

1. Rebuild brain container:
   ```bash
   docker compose up -d --build brain
   ```

2. Restart services:
   ```bash
   docker compose restart brain chroma
   ```

3. Re-run migration if Chroma was updated:
   ```bash
   docker compose exec brain python /app/scripts/migrate_chroma_http.py
   ```

## CI/CD Integration

Add health checks to your deployment pipeline:

```bash
# Run tests
docker compose exec brain python /app/scripts/test_prompt_interface.py || exit 1

# Run health check
docker compose exec brain python /app/scripts/health_check_chroma.py || exit 1

# Check API health
curl -f http://localhost:7000/v1/healthz || exit 1
```

## Performance Benchmarks

Expected performance baselines:

- **Embedding generation**: ~100-200ms per query (depends on Ollama)
- **Memory query**: <500ms for k=3
- **FAQ query**: <300ms for k=2
- **Turn query**: <200ms for k=5 (with conversation_id)
- **Full prompt build**: <1s with all RAG components

Monitor these metrics to detect performance degradation.
