import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any, Type
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..orchestrator.hive import Hive
from ..agents.base import BaseAgent
from ..agents.coder import CoderAgent
from ..agents.researcher import ResearcherAgent
from ..agents.tester import TesterAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ada Swarm API",
    description="HTTP API for task submission and swarm management",
)

# Global Hive instance
hive = Hive()

# In-memory task store
# Maps task_id -> task_data
tasks: Dict[str, Dict[str, Any]] = {}

# Agent type mapping
AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {
    "coder": CoderAgent,
    "researcher": ResearcherAgent,
    "tester": TesterAgent,
}


class TaskSubmission(BaseModel):
    description: str
    model: str
    agent_type: str
    capabilities: Optional[List[str]] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    results: Optional[Any] = None


class AgentListResponse(BaseModel):
    agents: List[Dict[str, Any]]


async def run_task(task_id: str, description: str, agent: BaseAgent):
    """Background task to execute the agent's run method."""
    tasks[task_id]["status"] = "in_progress"
    try:
        # Get agent dependencies from the hive
        deps = hive.get_agent_deps()

        # Run the agent
        # Note: pydantic_ai.Agent.run is async
        result = await agent.run(description, deps=deps)

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["results"] = result.data
        tasks[task_id]["progress"] = 1.0
        logger.info(f"Task {task_id} completed successfully.")
    except asyncio.CancelledError:
        tasks[task_id]["status"] = "cancelled"
        logger.info(f"Task {task_id} was cancelled.")
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["results"] = str(e)
        logger.error(f"Task {task_id} failed: {e}")


@app.post("/tasks", response_model=TaskResponse)
async def submit_task(submission: TaskSubmission):
    if submission.agent_type not in AGENT_CLASSES:
        raise HTTPException(
            status_code=400, detail=f"Invalid agent type: {submission.agent_type}"
        )

    task_id = str(uuid.uuid4())
    agent_id = f"{submission.agent_type}-{task_id[:8]}"

    # Spawn agent
    agent_class = AGENT_CLASSES[submission.agent_type]
    agent = hive.spawn_agent(
        agent_class=agent_class,
        agent_id=agent_id,
        model=submission.model,
        capabilities=submission.capabilities,
    )

    # Initialize task record
    tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0.0,
        "results": None,
        "agent_id": agent_id,
        "async_task": None,
    }

    # Schedule execution
    loop = asyncio.get_running_loop()
    async_task = loop.create_task(run_task(task_id, submission.description, agent))
    tasks[task_id]["async_task"] = async_task

    return TaskResponse(task_id=task_id, status="queued")


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        progress=task_data["progress"],
        results=task_data["results"],
    )


@app.get("/agents", response_model=AgentListResponse)
async def list_agents():
    status = hive.get_swarm_status()
    return AgentListResponse(agents=status["registry"])


@app.delete("/tasks/{task_id}", response_model=TaskResponse)
async def cancel_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = tasks[task_id]
    if task_data["status"] in ["completed", "failed", "cancelled"]:
        return TaskResponse(task_id=task_id, status=task_data["status"])

    async_task = task_data.get("async_task")
    if async_task and not async_task.done():
        async_task.cancel()
        # We don't necessarily need to await it here,
        # the run_task will handle CancelledError

    task_data["status"] = "cancelled"
    return TaskResponse(task_id=task_id, status="cancelled")


if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("ADA_SWARM_HOST", "127.0.0.1")
    port = int(os.getenv("ADA_SWARM_PORT", "8765"))

    uvicorn.run(app, host=host, port=port)
