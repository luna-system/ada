"""Interactive CLI and one-shot command-line interface for Ada.

This module provides both interactive REPL mode and one-shot query mode,
demonstrating different ways to use the Ada client.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from ada_client import AdaClient, AdaBrainConnectionError, AdaBrainError

console = Console()


async def check_brain_health(client: AdaClient) -> bool:
    """Check if brain is accessible and healthy.
    
    Args:
        client: Ada client instance
        
    Returns:
        True if healthy, False otherwise
    """
    try:
        health = await client.health()
        if health.get("status") == "healthy":
            return True
        else:
            console.print(f"[yellow]⚠️  Brain status: {health.get('status', 'unknown')}[/]")
            return False
    except AdaBrainConnectionError:
        console.print(f"[red]❌ Unable to connect to Ada's brain[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Health check failed: {e}[/]")
        return False


async def interactive_mode(
    client: AdaClient,
    conversation_id: str = "cli-session",
    stream: bool = True
):
    """Run interactive REPL mode.
    
    Args:
        client: Ada client instance
        conversation_id: Conversation ID for context
        stream: Whether to stream responses (True) or wait for complete response
    """
    console.print(Panel.fit(
        "🤖 [bold cyan]Ada CLI[/] - Interactive Mode\n\n"
        "Commands: [bold]/help[/], [bold]/history[/], [bold]/clear[/], [bold]/exit[/]\n"
        "Ctrl+C to interrupt, Ctrl+D or 'exit' to quit",
        border_style="cyan"
    ))
    
    # Check brain health
    if not await check_brain_health(client):
        console.print("\n[yellow]Continuing anyway... (brain might still respond)[/]\n")
    
    history = []
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/]").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                console.print("\n[cyan]Goodbye! 👋[/]\n")
                break
            
            if user_input == "/help":
                console.print(Panel(
                    "[bold]Available Commands:[/]\n\n"
                    "  [bold]/help[/]     - Show this help message\n"
                    "  [bold]/history[/]  - Show conversation history\n"
                    "  [bold]/clear[/]    - Clear conversation context\n"
                    "  [bold]/exit[/]     - Exit the CLI\n\n"
                    "Just type your message to chat with Ada!",
                    title="Help",
                    border_style="blue"
                ))
                continue
            
            if user_input == "/history":
                if not history:
                    console.print("[dim]No conversation history yet.[/]")
                else:
                    console.print("\n[bold]Conversation History:[/]\n")
                    for i, (role, msg) in enumerate(history, 1):
                        preview = msg[:60] + "..." if len(msg) > 60 else msg
                        console.print(f"  {i}. [blue]{role}:[/] {preview}")
                continue
            
            if user_input == "/clear":
                history.clear()
                # Generate new conversation ID to reset context
                import uuid
                conversation_id = f"cli-session-{uuid.uuid4().hex[:8]}"
                console.print("[green]✓[/] Conversation cleared. Starting fresh!")
                continue
            
            # Process chat message
            history.append(("You", user_input))
            
            console.print("\n[bold green]Ada:[/] ", end="")
            
            if stream:
                # Stream response chunks
                response_parts = []
                try:
                    async for chunk in client.chat_stream(user_input, conversation_id):
                        console.print(chunk, end="")
                        response_parts.append(chunk)
                        sys.stdout.flush()
                    console.print()  # Newline after streaming
                    
                    full_response = "".join(response_parts)
                    history.append(("Ada", full_response))
                
                except AdaBrainError as e:
                    console.print(f"\n[red]Error: {e}[/]")
            
            else:
                # Wait for complete response
                try:
                    response = await client.chat(user_input, conversation_id)
                    console.print(response)
                    history.append(("Ada", response))
                
                except AdaBrainError as e:
                    console.print(f"[red]Error: {e}[/]")
        
        except KeyboardInterrupt:
            console.print("\n[dim](Use /exit to quit)[/]")
            continue
        
        except EOFError:
            console.print("\n\n[cyan]Goodbye! 👋[/]\n")
            break
        
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/]")


async def oneshot_mode(
    client: AdaClient,
    message: str,
    conversation_id: str = "cli-oneshot",
    stream: bool = True,
    output_format: str = "text"
):
    """Run one-shot query mode.
    
    Args:
        client: Ada client instance
        message: User message to send
        conversation_id: Conversation ID for context
        stream: Whether to stream response
        output_format: Output format ('text', 'json', 'markdown')
    """
    try:
        if stream:
            # Stream to stdout
            if output_format == "json":
                import json
                chunks = []
                async for chunk in client.chat_stream(message, conversation_id):
                    chunks.append(chunk)
                response = "".join(chunks)
                result = {"response": response, "conversation_id": conversation_id}
                print(json.dumps(result, indent=2))
            else:
                async for chunk in client.chat_stream(message, conversation_id):
                    print(chunk, end="")
                    sys.stdout.flush()
                print()  # Final newline
        else:
            # Complete response
            response = await client.chat(message, conversation_id)
            
            if output_format == "json":
                import json
                result = {"response": response, "conversation_id": conversation_id}
                print(json.dumps(result, indent=2))
            elif output_format == "markdown":
                md = Markdown(response)
                console.print(md)
            else:
                print(response)
    
    except AdaBrainConnectionError as e:
        console.print(f"[red]Connection error: {e}[/]")
        sys.exit(1)
    except AdaBrainError as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@click.command()
@click.argument("message", required=False)
@click.option(
    "--brain-url",
    default="http://localhost:7000",
    envvar="ADA_BRAIN_URL",
    help="Ada brain API URL (default: http://localhost:7000)"
)
@click.option(
    "--conversation-id",
    default=None,
    help="Conversation ID for context (default: auto-generated)"
)
@click.option(
    "--stream/--no-stream",
    default=True,
    help="Stream response chunks (default: stream)"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format (default: text)"
)
@click.option(
    "--timeout",
    default=120.0,
    help="Request timeout in seconds (default: 120)"
)
def main(
    message: Optional[str],
    brain_url: str,
    conversation_id: Optional[str],
    stream: bool,
    output_format: str,
    timeout: float
):
    """Ada CLI - Command-line interface for Ada's brain.
    
    If MESSAGE is provided, runs in one-shot mode. Otherwise, starts
    interactive REPL mode.
    
    Examples:
    
        # Interactive mode
        $ ada-cli
        
        # One-shot query
        $ ada-cli "What is 2+2?"
        
        # JSON output for scripting
        $ ada-cli --format json "Hello" | jq '.response'
        
        # Custom brain URL
        $ ada-cli --brain-url http://ada.example.com:7000 "Hello"
    """
    async def run():
        async with AdaClient(base_url=brain_url, timeout=timeout) as client:
            if message:
                # One-shot mode
                conv_id = conversation_id or "cli-oneshot"
                await oneshot_mode(
                    client,
                    message,
                    conv_id,
                    stream,
                    output_format
                )
            else:
                # Interactive mode
                import uuid
                conv_id = conversation_id or f"cli-session-{uuid.uuid4().hex[:8]}"
                await interactive_mode(client, conv_id, stream)
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
