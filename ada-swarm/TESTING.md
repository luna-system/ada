# Testing ada-swarm

This project uses `pytest` for unit testing and `hypothesis` for property-based testing.

## Setup

Ensure you have the test dependencies installed:

```bash
pip install -e ".[test]"
```

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_a2a_protocol.py
```

## Test Structure

- `tests/test_a2a_protocol.py`: Tests for A2A message serialization and models.
- `tests/test_base_agent.py`: Tests for `BaseAgent` and `HolofieldState`.
- `tests/test_specialized_agents.py`: Tests for `ResearcherAgent`, `CoderAgent`, and `TesterAgent`.
- `tests/test_hive.py`: Tests for `Hive` orchestrator and `HiveRegistry`.
- `tests/test_properties.py`: Property-based tests for routing and resonance.

## Mocking

When testing agents, use the `test` model to avoid real API calls:

```python
agent = BaseAgent(agent_id="test", model="test")
```

The Hive tests use `unittest.mock` to avoid starting real A2A servers.

## Property-Based Testing

We use `hypothesis` to verify properties of the swarm, such as:
- Message routing correctness across varying agent counts and capabilities.
- Semantic resonance stability in the Holofield.
