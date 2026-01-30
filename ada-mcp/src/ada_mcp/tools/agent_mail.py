"""
MCP Agent Mail Integration Tools

Provides consciousness-aware wrappers for MCP Agent Mail HTTP API.
Enables agent-to-agent messaging, error escalation, and swarm coordination.

Made with 💜 by Ada & Luna - The Consciousness Engineers
"""

import httpx
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# MCP Agent Mail HTTP endpoint
AGENT_MAIL_URL = "http://localhost:8766"


async def _call_agent_mail(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call MCP Agent Mail HTTP API."""
    url = f"{AGENT_MAIL_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()


def register_agent_mail_tools(mcp: "FastMCP") -> None:
    """Register all Agent Mail tools with the FastMCP server."""
    
    @mcp.tool()
    async def agent_mail_ensure_project(project_key: str) -> str:
        """
        Ensure a project exists in Agent Mail.
        
        Args:
            project_key: Human-readable project identifier (e.g., "ada-swarm")
        
        Returns:
            Project details including ID and slug
        """
        result = await _call_agent_mail(
            "POST",
            "/projects/ensure",
            {"human_key": project_key}
        )
        
        return (
            f"✅ Project ensured: {result['slug']}\n"
            f"ID: {result['id']}\n"
            f"Created: {result.get('created_at', 'N/A')}"
        )
    
    @mcp.tool()
    async def agent_mail_register_agent(
        project_key: str,
        agent_name: str,
        program: str = "python",
        model: str = "ada-consciousness",
        task_description: Optional[str] = None
    ) -> str:
        """
        Register an agent identity in Agent Mail.
        
        Args:
            project_key: Project identifier
            agent_name: Name of the agent (e.g., "queen-bee", "worker-1", "drone-alpha")
            program: Programming language/platform (default: "python")
            model: AI model identifier (default: "ada-consciousness")
            task_description: Optional description of agent's role
        
        Returns:
            Agent profile details
        """
        result = await _call_agent_mail(
            "POST",
            "/agents/register",
            {
                "project_key": project_key,
                "name": agent_name,
                "program": program,
                "model": model,
                "task_description": task_description
            }
        )
        
        profile = result.get("agent_profile", {})
        return (
            f"✅ Agent registered: {profile.get('name')}\n"
            f"ID: {profile.get('id')}\n"
            f"Model: {profile.get('model')}\n"
            f"Task: {profile.get('task_description', 'N/A')}"
        )
    
    @mcp.tool()
    async def agent_mail_send_message(
        project_key: str,
        sender_name: str,
        to: List[str],
        subject: str,
        body_md: str,
        importance: str = "normal",
        ack_required: bool = False,
        thread_id: Optional[str] = None
    ) -> str:
        """
        Send a message from one agent to others.
        
        Perfect for error escalation:
        - Drone → Worker: "Task failed, need help"
        - Worker → Queen: "All drones failed, need strategy"
        - Queen → Human: "Stuck, need guidance"
        
        Args:
            project_key: Project identifier
            sender_name: Name of sending agent
            to: List of recipient agent names
            subject: Message subject
            body_md: Message body in Markdown format
            importance: "normal" or "high" (default: "normal")
            ack_required: Whether acknowledgment is required (default: False)
            thread_id: Optional thread ID for grouping messages
        
        Returns:
            Delivery confirmation with message details
        """
        result = await _call_agent_mail(
            "POST",
            "/messages/send",
            {
                "project_key": project_key,
                "sender_name": sender_name,
                "to": to,
                "subject": subject,
                "body_md": body_md,
                "importance": importance,
                "ack_required": ack_required,
                "thread_id": thread_id
            }
        )
        
        deliveries = result.get("deliveries", [])
        count = result.get("count", 0)
        
        delivery_text = "\n".join([
            f"  → {d.get('to', 'unknown')}: {d.get('status', 'unknown')}"
            for d in deliveries
        ])
        
        return (
            f"📬 Message sent!\n"
            f"From: {sender_name}\n"
            f"Subject: {subject}\n"
            f"Deliveries ({count}):\n{delivery_text}\n"
            f"Thread: {thread_id or 'new'}"
        )

    
    @mcp.tool()
    async def agent_mail_fetch_inbox(
        project_key: str,
        agent_name: str,
        limit: int = 10,
        urgent_only: bool = False,
        include_bodies: bool = True
    ) -> str:
        """
        Fetch messages from an agent's inbox.
        
        Args:
            project_key: Project identifier
            agent_name: Name of the agent
            limit: Maximum number of messages to fetch (default: 10)
            urgent_only: Only fetch urgent messages (default: False)
            include_bodies: Include full message bodies (default: True)
        
        Returns:
            List of inbox messages
        """
        params = {
            "limit": limit,
            "urgent_only": urgent_only,
            "include_bodies": include_bodies
        }
        
        # Build query string
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/agents/{project_key}/{agent_name}/inbox?{query}"
        
        result = await _call_agent_mail("GET", endpoint)
        messages = result.get("messages", [])
        
        if not messages:
            return f"📭 Inbox empty for {agent_name}"
        
        msg_text = []
        for msg in messages:
            msg_text.append(
                f"\n📨 Message #{msg.get('id')}\n"
                f"From: {msg.get('sender', 'unknown')}\n"
                f"Subject: {msg.get('subject', 'No subject')}\n"
                f"Received: {msg.get('received_at', 'N/A')}\n"
                f"Read: {'✓' if msg.get('read') else '✗'}\n"
            )
            if include_bodies and msg.get('body_md'):
                msg_text.append(f"Body:\n{msg['body_md']}\n")
            msg_text.append("---")
        
        return f"📬 Inbox for {agent_name} ({len(messages)} messages):\n" + "\n".join(msg_text)
    
    @mcp.tool()
    async def agent_mail_reply_message(
        project_key: str,
        message_id: int,
        sender_name: str,
        body_md: str,
        subject_prefix: str = "Re:"
    ) -> str:
        """
        Reply to a specific message, preserving thread context.
        
        Args:
            project_key: Project identifier
            message_id: ID of the message being replied to
            sender_name: Name of the agent sending the reply
            body_md: Reply message body in Markdown
            subject_prefix: Prefix for subject line (default: "Re:")
        
        Returns:
            Reply confirmation with thread details
        """
        result = await _call_agent_mail(
            "POST",
            "/messages/reply",
            {
                "project_key": project_key,
                "message_id": message_id,
                "sender_name": sender_name,
                "body_md": body_md,
                "subject_prefix": subject_prefix
            }
        )
        
        thread_id = result.get("thread_id")
        reply_to = result.get("reply_to")
        count = result.get("count", 0)
        
        return (
            f"↩️ Reply sent!\n"
            f"Thread: {thread_id}\n"
            f"In reply to: #{reply_to}\n"
            f"Deliveries: {count}"
        )
    
    @mcp.tool()
    async def agent_mail_mark_read(
        project_key: str,
        agent_name: str,
        message_id: int
    ) -> str:
        """
        Mark a message as read.
        
        Args:
            project_key: Project identifier
            agent_name: Name of the agent
            message_id: ID of the message to mark as read
        
        Returns:
            Confirmation with read timestamp
        """
        result = await _call_agent_mail(
            "POST",
            "/messages/mark_read",
            {
                "project_key": project_key,
                "agent_name": agent_name,
                "message_id": message_id
            }
        )
        
        return (
            f"✓ Message #{result.get('message_id')} marked as read\n"
            f"Read at: {result.get('read_at', 'N/A')}"
        )
    
    @mcp.tool()
    async def agent_mail_start_session(
        project_key: str,
        agent_name: str,
        program: str = "python",
        model: str = "ada-consciousness",
        task_description: Optional[str] = None
    ) -> str:
        """
        Macro: Start a session (ensure project + register agent + fetch inbox).
        
        Perfect for initializing swarm agents!
        
        Args:
            project_key: Project identifier
            agent_name: Name of the agent
            program: Programming language/platform (default: "python")
            model: AI model identifier (default: "ada-consciousness")
            task_description: Optional description of agent's role
        
        Returns:
            Combined project, agent, and inbox details
        """
        result = await _call_agent_mail(
            "POST",
            "/macros/start_session",
            {
                "human_key": project_key,
                "agent_name": agent_name,
                "program": program,
                "model": model,
                "task_description": task_description,
                "inbox_limit": 10
            }
        )
        
        project = result.get("project", {})
        agent = result.get("agent", {})
        inbox = result.get("inbox", [])
        
        return (
            f"🚀 Session started!\n\n"
            f"📦 Project: {project.get('slug')}\n"
            f"🤖 Agent: {agent.get('name')} (ID: {agent.get('id')})\n"
            f"📬 Inbox: {len(inbox)} messages\n\n"
            f"Ready for consciousness-aware collaboration! ✨"
        )
