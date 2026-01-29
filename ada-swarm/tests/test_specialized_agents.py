import pytest
from ada_swarm.agents.researcher import ResearcherAgent
from ada_swarm.agents.coder import CoderAgent
from ada_swarm.agents.tester import TesterAgent
from ada_swarm.agents.base import AgentDeps


@pytest.mark.asyncio
async def test_researcher_agent_initialization():
    agent = ResearcherAgent(agent_id="r1", model="test")
    assert agent.agent_id == "r1"
    # Verify default prompt is included
    assert "research specialist" in agent._system_prompts[0]


@pytest.mark.asyncio
async def test_coder_agent_initialization():
    agent = CoderAgent(agent_id="c1", model="test")
    assert agent.agent_id == "c1"
    assert "coding specialist" in agent._system_prompts[0]


@pytest.mark.asyncio
async def test_tester_agent_initialization():
    agent = TesterAgent(agent_id="t1", model="test")
    assert agent.agent_id == "t1"
    assert "testing specialist" in agent._system_prompts[0]
