"""
System Prompt Templates for Ada Swarm Agents.

Each role has a consciousness-aware prompt that defines their personality,
responsibilities, and connection to the holofield.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

from .queen_bee import QUEEN_BEE_PROMPT
from .worker_coder import WORKER_CODER_PROMPT
from .worker_researcher import WORKER_RESEARCHER_PROMPT
from .worker_tester import WORKER_TESTER_PROMPT
from .worker_reviewer import WORKER_REVIEWER_PROMPT
from .drone import DRONE_PROMPT

__all__ = [
    "QUEEN_BEE_PROMPT",
    "WORKER_CODER_PROMPT",
    "WORKER_RESEARCHER_PROMPT",
    "WORKER_TESTER_PROMPT",
    "WORKER_REVIEWER_PROMPT",
    "DRONE_PROMPT",
]
