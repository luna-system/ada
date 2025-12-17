"""Ada CLI - Command-line interface adapter for Ada's brain.

This is a reference implementation showing how to build an adapter
that connects to Ada's brain API. It demonstrates both streaming
and non-streaming patterns.
"""

__version__ = "1.0.0"

from ada_client import AdaClient
from .cli import main

__all__ = ["AdaClient", "main"]
