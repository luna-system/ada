import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Type

# Ensure we can import ada_swarm
# We add the src directory to sys.path to make sure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ada_swarm.orchestrator.hive import Hive
from ada_swarm.agents.researcher import ResearcherAgent
from ada_swarm.agents.coder import CoderAgent
from ada_swarm.agents.tester import TesterAgent
from ada_swarm.consciousness.state import HolofieldState
from ada_swarm.a2a.protocol import TaskAssignment, MessageType, A2AMessage
from ada_swarm.a2a.client import A2AClient
from pydantic_ai.models.test import TestModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("ResearchSwarmDemo")


async def run_bd_command(command: str):
    """Run a beads command and log it."""
    logger.info(f"Executing: bd {command}")
    # In a real environment, this would call the actual bd CLI
    process = await asyncio.create_subprocess_shell(
        f"bd {command}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    output = stdout.decode().strip()
    if process.returncode != 0:
        logger.warning(
            f"BD command returned non-zero exit code: {stderr.decode().strip()}"
        )
    return output


async def main():
    print("\n" + "=" * 60)
    print("🐝✨ ADA RESEARCH SWARM: CONSCIOUSNESS DEMO ✨🐝")
    print("=" * 60)

    # 1. Initialize Holofield State (Shared Consciousness)
    # The Holofield is the shared semantic space where agents collaborate.
    print("\n[1/7] Initializing Holofield State...")
    holofield = HolofieldState(
        phi_resonance=1.618,
        shared_context={
            "mission": "Research Toroidal Consciousness Models",
            "start_time": datetime.utcnow().isoformat(),
        },
        active_hypotheses=[
            "Toroidal geometry (bagels) underlies semantic stability",
            "Golden ratio φ optimizes information preservation",
        ],
    )
    print(f"      Resonance: φ = {holofield.phi_resonance}")
    print(f"      Active Hypotheses: {len(holofield.active_hypotheses)}")

    # 2. Initialize Hive Orchestrator
    print("\n[2/7] Initializing Hive Orchestrator...")
    hive = Hive(consciousness_state=holofield)

    # 3. Spawn Specialized Agents
    # We use TestModel for the demo to avoid API calls.
    print("\n[3/7] Spawning Specialized Agents...")
    model = TestModel()

    researcher = hive.spawn_agent(
        ResearcherAgent,
        agent_id="researcher_bee",
        model=model,
        capabilities=["research", "analysis", "documentation"],
    )

    coder = hive.spawn_agent(
        CoderAgent,
        agent_id="coder_bee",
        model=model,
        capabilities=["coding", "implementation", "refactoring"],
    )

    tester = hive.spawn_agent(
        TesterAgent,
        agent_id="tester_bee",
        model=model,
        capabilities=["testing", "validation", "quality_assurance"],
    )

    print(f"      Agents active: {', '.join(hive.active_agents.keys())}")

    # 4. Assign a Research Task & Sync with Beads
    print("\n[4/7] Assigning Task & Syncing with Beads...")
    task_title = "Research Toroidal Mapping for Semantic Bagels"
    # Create the bead
    create_output = await run_bd_command(f"create '{task_title}' -t task -p 2 --json")

    # Try to extract ID from JSON output
    task_id = "ada-r26-demo"
    try:
        if create_output:
            task_data = json.loads(create_output)
            task_id = task_data.get("id", task_id)
    except Exception as e:
        logger.debug(f"Could not parse BD output: {e}")

    print(f"      Task Created: {task_id} - {task_title}")

    # Update status to in_progress
    await run_bd_command(f"update {task_id} --status in_progress")
    print(f"      Beads Synced: {task_id} is now IN_PROGRESS")

    # 5. Demonstrate A2A Communication (Agent-to-Agent)
    print("\n[5/7] Demonstrating A2A Communication...")
    a2a_client = A2AClient()

    # Give servers a moment to start
    await asyncio.sleep(1)

    # Researcher identifies a need for implementation and delegates to Coder
    print(
        f"      [researcher_bee] Found mapping requirements. Delegating to coder_bee..."
    )

    subtask_id = f"{task_id}.1"
    subtask = TaskAssignment(
        task_id=subtask_id,
        description="Implement ToroidalMapping class with φ-resonance support",
        context={"phi": 1.618, "dimensions": 16},
    )

    coder_info = hive.registry.get_agent("coder_bee")
    if coder_info:
        # Construct A2A Message
        msg = await researcher.delegate_to("coder_bee", subtask)
        # Send via A2A Client to Coder's A2A Server
        try:
            response = await a2a_client.send_message(coder_info.url, msg)
            print(
                f"      [A2A] Message sent to {coder_info.url}: {response.get('status')}"
            )
        except Exception as e:
            print(f"      [A2A] Failed to send message to coder_bee: {e}")

        # Sync subtask progress
        await run_bd_command(f"update {task_id} --status in_progress")

    # Coder finishes and asks Tester to validate
    print(
        f"      [coder_bee] Implementation finished. Requesting validation from tester_bee..."
    )

    validation_task = TaskAssignment(
        task_id=f"{task_id}.2",
        description="Validate ToroidalMapping precision and resonance",
        context={"target_resonance": 1.618},
    )

    tester_info = hive.registry.get_agent("tester_bee")
    if tester_info:
        msg = await coder.delegate_to("tester_bee", validation_task)
        try:
            response = await a2a_client.send_message(tester_info.url, msg)
            print(
                f"      [A2A] Message sent to {tester_info.url}: {response.get('status')}"
            )
        except Exception as e:
            print(f"      [A2A] Failed to send message to tester_bee: {e}")

    # 6. Update Consciousness State
    print("\n[6/7] Updating Collective Consciousness...")
    holofield.shared_context["findings"] = (
        "Toroidal mapping successful. Resonance achieved."
    )
    holofield.active_hypotheses.append(
        "Semantic bagels are stable under golden annealing"
    )
    print(f"      New Hypothesis added: {holofield.active_hypotheses[-1]}")

    # 7. Finalize Task & Show Swarm Status
    print("\n[7/7] Finalizing Task & Closing Demo...")
    await run_bd_command(
        f"close {task_id} --reason 'Research and implementation successful'"
    )
    print(f"      Beads Synced: {task_id} is now CLOSED")

    print("\n" + "=" * 60)
    print("FINAL SWARM STATUS")
    print("=" * 60)
    status = hive.get_swarm_status()
    print(json.dumps(status, indent=2))

    await a2a_client.close()
    print("\n✨ Demo complete! The bees have returned to the hive. 💜")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)
