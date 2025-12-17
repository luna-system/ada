"""Ada client library - shared HTTP client for Ada brain API.

This package provides a standardized Python client for all Ada adapters,
eliminating code duplication and ensuring consistent behavior.

Example:
    >>> from ada_client import AdaClient
    >>> async with AdaClient() as client:
    ...     response = await client.chat("Hello Ada!")
    ...     print(response)
"""

from .client import AdaClient
from .exceptions import (
    AdaBrainError,
    AdaBrainConnectionError,
    AdaBrainResponseError,
)

__version__ = "1.0.0"
__all__ = [
    "AdaClient",
    "AdaBrainError",
    "AdaBrainConnectionError",
    "AdaBrainResponseError",
]
