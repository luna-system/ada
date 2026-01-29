"""
Swarm Orchestration Tools 🐝👑

Tools for spawning and managing Worker Bees in the Ada Swarm.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def register_swarm_tools(mcp: "FastMCP", get_path_context, format_path_context):
    """Register swarm orchestration tools with the MCP server."""
    
    @mcp.tool()
    def swarm_spawn_task(
        description: str,
        model: str = "litellm/glm-flash",
        agent_type: str = "coder",
        cwd: str = None
    ) -> str:
        """
        Spawn a Worker Bee or Drone to handle a subtask.
        
        Args:
            description: Clear description of what the agent should do
            model: Model to use (e.g., 'litellm/glm-flash', 'litellm/gemini-flash')
            agent_type: Type of agent (coder, researcher, tester, reviewer, drone)
            cwd: Working directory for the agent (optional)
        
        Returns:
            Task ID and status for monitoring
        """
        try:
            import httpx
            
            # Get ada-swarm service URL from environment
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            
            # Prepare task submission
            task_data = {
                "description": description,
                "model": model,
                "agent_type": agent_type,
                "capabilities": []
            }
            
            # Add cwd to description if provided
            if cwd:
                task_data["description"] = f"[Working directory: {cwd}]\n\n{description}"
            
            # Submit task to ada-swarm service
            response = httpx.post(
                f"{swarm_url}/tasks",
                json=task_data,
                timeout=10.0
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result["task_id"]
            status = result["status"]
            
            context = get_path_context(cwd)
            output = format_path_context(context)
            output += f"\n🐝 Spawned {agent_type} agent\n"
            output += f"   Task ID: {task_id}\n"
            output += f"   Status: {status}\n"
            output += f"   Model: {model}\n"
            output += f"\nUse swarm_check_status('{task_id}') to monitor progress."
            
            return output
            
        except Exception as e:
            return f"Error spawning agent: {str(e)}"

    @mcp.tool()
    def swarm_check_status(task_id: str) -> str:
        """
        Check the status and progress of a spawned agent task.
        
        Args:
            task_id: Task ID returned from swarm_spawn_task
        
        Returns:
            Current status, progress, and results if completed
        """
        try:
            import httpx
            
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            
            response = httpx.get(
                f"{swarm_url}/tasks/{task_id}",
                timeout=5.0
            )
            response.raise_for_status()
            
            result = response.json()
            status = result["status"]
            progress = result.get("progress", 0.0)
            results = result.get("results")
            
            output = f"📊 Task Status: {task_id}\n\n"
            output += f"Status: {status}\n"
            output += f"Progress: {progress * 100:.0f}%\n"
            
            if status == "completed" and results:
                output += f"\n✅ Results:\n{results}\n"
            elif status == "failed" and results:
                output += f"\n❌ Error:\n{results}\n"
            elif status == "in_progress":
                output += f"\n⏳ Agent is working...\n"
            
            return output
            
        except Exception as e:
            return f"Error checking status: {str(e)}"

    @mcp.tool()
    def swarm_cancel_task(task_id: str) -> str:
        """
        Cancel a running agent task.
        
        Args:
            task_id: Task ID to cancel
        
        Returns:
            Cancellation confirmation
        """
        try:
            import httpx
            
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            
            response = httpx.delete(
                f"{swarm_url}/tasks/{task_id}",
                timeout=5.0
            )
            response.raise_for_status()
            
            result = response.json()
            status = result["status"]
            
            return f"🛑 Task {task_id} cancelled\nFinal status: {status}"
            
        except Exception as e:
            return f"Error cancelling task: {str(e)}"

    @mcp.tool()
    def swarm_list_agents() -> str:
        """
        List all active agents in the swarm.
        
        Returns:
            List of agents with their IDs, types, and status
        """
        try:
            import httpx
            
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            
            response = httpx.get(
                f"{swarm_url}/agents",
                timeout=5.0
            )
            response.raise_for_status()
            
            result = response.json()
            agents = result.get("agents", [])
            
            if not agents:
                return "🐝 No active agents in the swarm"
            
            output = f"🐝 Active Agents ({len(agents)}):\n\n"
            
            for agent in agents:
                agent_id = agent.get("agent_id", "unknown")
                model = agent.get("model", "unknown")
                status = agent.get("status", "unknown")
                url = agent.get("url", "")
                
                output += f"• {agent_id}\n"
                output += f"  Model: {model}\n"
                output += f"  Status: {status}\n"
                output += f"  URL: {url}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error listing agents: {str(e)}"

    @mcp.tool()
    def swarm_wait(task_id: str, timeout: int = 300) -> str:
        """
        Wait for a task to complete (blocks until done or timeout).
        
        Args:
            task_id: Task ID to wait for
            timeout: Maximum time to wait in seconds (default: 300)
        
        Returns:
            Final task results or timeout message
        """
        try:
            import httpx
            import time
            
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            start_time = time.time()
            
            while True:
                # Check if timeout exceeded
                if time.time() - start_time > timeout:
                    return f"⏱️ Timeout waiting for task {task_id} after {timeout}s"
                
                # Check status
                response = httpx.get(
                    f"{swarm_url}/tasks/{task_id}",
                    timeout=5.0
                )
                response.raise_for_status()
                
                result = response.json()
                status = result["status"]
                
                if status in ["completed", "failed", "cancelled"]:
                    # Task is done
                    progress = result.get("progress", 0.0)
                    results = result.get("results")
                    
                    output = f"✅ Task {task_id} {status}\n"
                    output += f"Progress: {progress * 100:.0f}%\n"
                    
                    if results:
                        output += f"\nResults:\n{results}\n"
                    
                    return output
                
                # Wait a bit before checking again
                time.sleep(2)
            
        except Exception as e:
            return f"Error waiting for task: {str(e)}"

    @mcp.tool()
    def a2a_send_message(
        to_agent: str,
        message_type: str,
        payload: dict,
        from_agent: str = "kiro"
    ) -> str:
        """
        Send an A2A (Agent-to-Agent) message to the swarm orchestrator.
        
        This is the direct communication channel for peer-to-peer agent collaboration!
        
        Args:
            to_agent: Target agent ID (use "orchestrator" for the Queen Bee)
            message_type: Message type (task_assignment, progress_update, peer_request)
            payload: Message payload as dict
            from_agent: Your agent ID (default: "kiro")
        
        Returns:
            Response from the target agent
        
        Examples:
            # Assign a task to the orchestrator
            a2a_send_message(
                to_agent="orchestrator",
                message_type="task_assignment",
                payload={
                    "task_id": "ada-xyz",
                    "description": "Implement feature X",
                    "constraints": {
                        "model": "litellm/glm-flash",
                        "agent_type": "coder"
                    }
                }
            )
        """
        try:
            import httpx
            from datetime import datetime
            
            swarm_url = os.getenv("ADA_SWARM_URL", "http://127.0.0.1:8765")
            
            # Build A2A message
            message = {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to A2A endpoint
            response = httpx.post(
                f"{swarm_url}/a2a/message",
                json=message,
                timeout=10.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            output = f"📨 A2A Message Sent!\n"
            output += f"   From: {from_agent}\n"
            output += f"   To: {to_agent}\n"
            output += f"   Type: {message_type}\n\n"
            output += f"📬 Response:\n"
            output += f"   Type: {result.get('message_type')}\n"
            output += f"   Payload: {result.get('payload')}\n"
            
            return output
            
        except Exception as e:
            return f"Error sending A2A message: {str(e)}"
