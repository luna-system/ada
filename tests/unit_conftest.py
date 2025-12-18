"""Minimal pytest configuration for unit tests.

This conftest is for pure unit tests that don't need ChromaDB,
Docker, or other integration dependencies.
"""

import sys
from pathlib import Path

# Add brain to path
sys.path.insert(0, str(Path(__file__).parent.parent))
