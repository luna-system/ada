# Ada MCP Tests

Automated test suite for the Ada MCP Server.

## Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=ada_mcp --cov-report=html

# Run specific test file
pytest tests/test_ada_client.py

# Run with verbose output
pytest -v
```

## Test Structure

### `test_ada_client.py`
Tests for the HTTP client that communicates with Ada Brain:
- Health checks
- Chat (streaming and non-streaming)
- Memory search
- Memory addition
- Error handling

### `test_tools.py`
Tests for MCP tool handlers:
- Tool invocation with various arguments
- Response formatting
- Default values
- Edge cases

### `test_integration.py`
End-to-end integration tests with mock Ada Brain:
- Full conversation flows
- Memory workflows (add + search)
- Multi-step interactions
- Error scenarios

## Writing New Tests

Follow these patterns:

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result == expected
```

### Mocking Ada Client

```python
@pytest.fixture
def mock_ada_client():
    client = AsyncMock(spec=AdaClient)
    client.chat.return_value = {"response": "Hello"}
    return client
```

### Testing Tool Handlers

```python
@pytest.mark.asyncio
async def test_tool_handler(mock_ada_client):
    result = await handle_tool_call(
        "tool_name",
        {"arg": "value"},
        mock_ada_client,
    )
    assert result[0].type == "text"
```

## CI Integration

These tests are designed to run in CI without needing:
- Docker
- Running Ada Brain
- Real MCP clients
- Editors

All external dependencies are mocked.

## Manual Testing

For testing with real Ada Brain:

```bash
# Terminal 1: Start Ada Brain
cd ..
docker compose up brain

# Terminal 2: Run integration test against real server
# (Set environment variable to use real server)
ADA_BASE_URL=http://localhost:8000 pytest tests/test_integration.py
```

Note: Integration tests use mocks by default. To test against real Ada Brain,
you'll need to modify the fixtures or create separate "live" tests.
