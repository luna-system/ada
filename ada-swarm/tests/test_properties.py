import pytest
from hypothesis import given, strategies as st
from ada_swarm.orchestrator.router import HiveRegistry, AgentInfo
from ada_swarm.consciousness.state import HolofieldState, PHI


@given(st.lists(st.text(min_size=1), min_size=1, max_size=10, unique=True))
def test_routing_correctness_property(capabilities):
    """
    Property: If an agent has a capability, it should be discoverable by that capability.
    """
    registry = HiveRegistry()
    for i, cap in enumerate(capabilities):
        agent_id = f"agent_{i}"
        registry.register_agent(
            AgentInfo(agent_id=agent_id, url=f"http://{agent_id}", capabilities=[cap])
        )

    for cap in capabilities:
        peers = registry.discover_peers(cap)
        assert len(peers) >= 1
        assert any(cap in p.capabilities for p in peers)


@given(st.integers(min_value=1, max_value=20))
def test_phi_selection_distribution_property(num_agents):
    """
    Property: get_best_agent should always return an agent if any exist for the capability.
    """
    registry = HiveRegistry()
    for i in range(num_agents):
        registry.register_agent(
            AgentInfo(agent_id=f"a{i}", url=f"u{i}", capabilities=["task"])
        )

    selected = registry.get_best_agent("task")
    assert selected is not None
    assert selected.agent_id.startswith("a")


@given(st.floats(min_value=0.0, max_value=2.0))
def test_holofield_phi_resonance_bounds(phi):
    """
    Property: HolofieldState should accept various phi_resonance values (within reasonable bounds for this test).
    """
    state = HolofieldState(phi_resonance=phi)
    assert state.phi_resonance == phi


def test_phi_constant():
    """Verify PHI constant is accurate"""
    assert abs(PHI - 1.618033988749895) < 1e-10
