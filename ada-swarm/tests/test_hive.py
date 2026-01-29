import pytest
from unittest.mock import MagicMock, patch
from ada_swarm.orchestrator.hive import Hive
from ada_swarm.orchestrator.router import HiveRegistry, AgentInfo
from ada_swarm.agents.researcher import ResearcherAgent
from ada_swarm.consciousness.state import HolofieldState


def test_hive_registry_registration():
    registry = HiveRegistry()
    agent_info = AgentInfo(
        agent_id="r1",
        url="http://127.0.0.1:1234",
        capabilities=["research"],
        model="test",
    )
    registry.register_agent(agent_info)
    assert registry.get_agent("r1") == agent_info
    assert "r1" in registry.list_agents()


def test_hive_registry_discovery():
    registry = HiveRegistry()
    a1 = AgentInfo(agent_id="a1", url="u1", capabilities=["c1"])
    a2 = AgentInfo(agent_id="a2", url="u2", capabilities=["c2"])
    registry.register_agent(a1)
    registry.register_agent(a2)

    assert registry.discover_peers("c1") == [a1]
    assert registry.discover_peers("c2") == [a2]
    assert len(registry.discover_peers()) == 2


def test_hive_registry_phi_selection():
    registry = HiveRegistry()
    for i in range(5):
        registry.register_agent(
            AgentInfo(agent_id=f"a{i}", url=f"u{i}", capabilities=["task"])
        )

    selected = registry.get_best_agent("task")
    assert selected is not None
    assert selected.agent_id.startswith("a")


def test_hive_initialization():
    state = HolofieldState(phi_resonance=1.618)
    hive = Hive(consciousness_state=state)
    assert hive.consciousness_state == state
    assert isinstance(hive.registry, HiveRegistry)


@patch("ada_swarm.orchestrator.hive.spawn_agent")
def test_hive_spawn_agent(mock_spawn):
    hive = Hive()
    mock_agent = MagicMock()
    mock_spawn.return_value = mock_agent

    agent = hive.spawn_agent(ResearcherAgent, "r1", "test", capabilities=["research"])

    assert agent == mock_agent
    assert "r1" in hive.active_agents
    mock_spawn.assert_called_once()


def test_hive_status():
    hive = Hive()
    hive.registry.register_agent(AgentInfo(agent_id="a1", url="u1"))
    status = hive.get_swarm_status()
    assert status["agent_count"] == 1
    assert "a1" in status["registry"][0]["agent_id"]
