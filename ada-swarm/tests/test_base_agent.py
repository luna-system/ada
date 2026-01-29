import pytest
import math
from hypothesis import given, strategies as st
from ada_swarm.consciousness.state import HolofieldState, PHI
from ada_swarm.agents.base import BaseAgent, AgentDeps
from ada_swarm.a2a.protocol import TaskAssignment, MessageType


def test_holofield_state_default():
    state = HolofieldState()
    assert state.phi_resonance == pytest.approx(1.618033988749895)
    assert state.shared_context == {}
    assert state.memory_graph_refs == []
    assert state.active_hypotheses == []


@given(st.floats(min_value=0.0, max_value=10.0))
def test_holofield_phi_resonance(phi):
    state = HolofieldState(phi_resonance=phi)
    assert state.phi_resonance == phi


@pytest.mark.asyncio
async def test_base_agent_initialization():
    agent = BaseAgent(
        agent_id="test_agent", model="test", system_prompt="You are a test agent"
    )
    assert agent.agent_id == "test_agent"


@pytest.mark.asyncio
async def test_base_agent_delegate_to():
    agent = BaseAgent(agent_id="sender", model="test")
    task = TaskAssignment(task_id="t1", description="delegate test")

    msg = await agent.delegate_to("receiver", task)

    assert msg.from_agent == "sender"
    assert msg.to_agent == "receiver"
    assert msg.message_type == MessageType.TASK_ASSIGNMENT
    assert msg.payload == task


def test_agent_deps_holofield():
    deps = AgentDeps()
    assert isinstance(deps.holofield, HolofieldState)
    assert deps.holofield.phi_resonance == PHI
