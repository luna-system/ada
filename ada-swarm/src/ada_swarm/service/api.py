import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any, Type
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# Configure LiteLLM proxy FIRST (before importing agents)
from .. import config  # This sets up litellm.api_base

from ..orchestrator.hive import Hive
from ..agents.base import BaseAgent
from ..agents.coder import CoderAgent
from ..agents.researcher import ResearcherAgent
from ..agents.tester import TesterAgent
from ..agents.queen import QueenAgent
from .a2a import (
    A2AMessage,
    MessageType,
    TaskAssignment,
    ProgressUpdate,
    TaskResult,
)

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
    "queen": QueenAgent,
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


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    data: List[ModelInfo]
    object: str = "list"


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
        tasks[task_id]["results"] = result.output
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


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    Query LiteLLM proxy for available models.
    Returns all models configured in litellm-proxy-config.yaml.
    """
    if not config.LITELLM_PROXY_URL:
        raise HTTPException(
            status_code=503,
            detail="LiteLLM proxy not configured. Set LITELLM_PROXY_URL environment variable."
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.LITELLM_PROXY_URL}/v1/models",
                headers={"Authorization": f"Bearer {config.LITELLM_MASTER_KEY}"},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Transform to our response format
            return ModelsResponse(
                data=[ModelInfo(**model) for model in data.get("data", [])],
                object=data.get("object", "list")
            )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch models from LiteLLM proxy: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch models from LiteLLM proxy: {str(e)}"
        )


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


# ============================================================================
# A2A PROTOCOL ENDPOINTS 🐝✨
# ============================================================================

@app.post("/a2a/message")
async def handle_a2a_message(message: A2AMessage):
    """
    Handle incoming A2A protocol messages.
    
    This is the main entry point for agent-to-agent communication.
    Routes messages based on type and handles responses.
    """
    logger.info(f"📨 A2A message from {message.from_agent} to {message.to_agent}: {message.message_type}")
    
    try:
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            # Parse task assignment
            assignment = TaskAssignment(**message.payload)
            
            # Extract agent type and model from constraints
            constraints = assignment.constraints or {}
            agent_type = constraints.get("agent_type", "coder")
            model = constraints.get("model", "litellm/glm-flash")
            
            # Submit task using existing infrastructure
            submission = TaskSubmission(
                description=assignment.description,
                model=model,
                agent_type=agent_type,
                capabilities=constraints.get("tools"),
            )
            
            response = await submit_task(submission)
            
            # Return A2A response
            return A2AMessage(
                from_agent="orchestrator",
                to_agent=message.from_agent,
                message_type=MessageType.TASK_RESULT,
                payload={
                    "task_id": response.task_id,
                    "status": response.status,
                    "message": f"Task {response.task_id} queued successfully"
                }
            )
            
        elif message.message_type == MessageType.PROGRESS_UPDATE:
            # Handle progress update from worker
            update = ProgressUpdate(**message.payload)
            
            if update.task_id in tasks:
                tasks[update.task_id]["progress"] = update.progress
                tasks[update.task_id]["status"] = update.status
                logger.info(f"📊 Task {update.task_id} progress: {update.progress:.0%}")
            
            return A2AMessage(
                from_agent="orchestrator",
                to_agent=message.from_agent,
                message_type=MessageType.TASK_RESULT,
                payload={"acknowledged": True}
            )
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported message type: {message.message_type}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error handling A2A message: {e}")
        return A2AMessage(
            from_agent="orchestrator",
            to_agent=message.from_agent,
            message_type=MessageType.ERROR,
            payload={"error": str(e)}
        )


@app.get("/a2a/status/{task_id}")
async def get_a2a_task_status(task_id: str):
    """
    Get task status in A2A format.
    
    This endpoint returns task status wrapped in an A2A message,
    making it easy for agents to query task progress.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = tasks[task_id]
    
    return A2AMessage(
        from_agent="orchestrator",
        to_agent="requester",
        message_type=MessageType.TASK_RESULT,
        payload=TaskResult(
            task_id=task_id,
            status=task_data["status"],
            results=task_data["results"],
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("ADA_SWARM_HOST", "127.0.0.1")
    port = int(os.getenv("ADA_SWARM_PORT", "8765"))

    # Force asyncio loop for Python 3.14 compatibility (uvloop not supported yet)
    uvicorn.run(app, host=host, port=port, loop="asyncio")
