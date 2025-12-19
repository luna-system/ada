"""Protocol (interface) for log format parsers.

Uses PEP 544 structural typing - any class with parse() and detect_format()
is automatically a LogParser, no inheritance needed.
"""

from typing import Protocol, runtime_checkable
from ada_logs.core import LogAnalysis


@runtime_checkable
class LogParser(Protocol):
    """Protocol for log format parsers.

    Any class implementing these methods is a valid LogParser.
    Inspired by Ada's Specialist protocol pattern.
    """

    def parse(self, log_content: str) -> LogAnalysis:
        """Parse log content and return structured analysis.

        Args:
            log_content: Raw log file content as string

        Returns:
            LogAnalysis with error details, explanations, and fixes

        Raises:
            ValueError: If log cannot be parsed
        """
        ...

    def detect_format(self, log_content: str) -> bool:
        """Check if this parser can handle the given log format.

        Args:
            log_content: Raw log file content as string

        Returns:
            True if parser can handle this format, False otherwise
        """
        ...
