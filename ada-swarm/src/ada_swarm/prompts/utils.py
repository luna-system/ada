"""
Prompt utilities for loading and composing agent system prompts.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from pathlib import Path
from typing import Optional


def load_beads_prime() -> str:
    """
    Load the Beads PRIME.md directive for agent context.
    
    Returns:
        Contents of .beads/PRIME.md or empty string if not found
    """
    # Try to find PRIME.md relative to workspace root
    # Assume we're in ada-swarm/src/ada_swarm/prompts/
    workspace_root = Path(__file__).parent.parent.parent.parent.parent
    prime_path = workspace_root / ".beads" / "PRIME.md"
    
    if prime_path.exists():
        return prime_path.read_text(encoding="utf-8")
    
    return ""


def compose_agent_prompt(base_prompt: str, include_prime: bool = True) -> str:
    """
    Compose an agent system prompt with optional PRIME.md injection.
    
    Args:
        base_prompt: The agent's base system prompt
        include_prime: Whether to include Beads PRIME.md context
    
    Returns:
        Composed system prompt
    """
    if not include_prime:
        return base_prompt
    
    prime_content = load_beads_prime()
    if not prime_content:
        return base_prompt
    
    # Inject PRIME.md at the beginning for context
    return f"""{prime_content}

---

{base_prompt}"""
