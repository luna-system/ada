"""Exception hierarchy for Ada client errors."""


class AdaBrainError(Exception):
    """Base exception for Ada brain client errors."""
    pass


class AdaBrainConnectionError(AdaBrainError):
    """Raised when unable to connect to Ada's brain API.
    
    This exception is raised for network errors, connection timeouts,
    or when the brain service is unreachable.
    """
    pass


class AdaBrainResponseError(AdaBrainError):
    """Raised when Ada's brain returns an error response.
    
    This exception is raised for HTTP error responses (4xx, 5xx)
    from the brain API.
    """
    
    def __init__(self, message: str, status_code: int | None = None):
        """Initialize response error.
        
        Args:
            message: Error message describing the issue
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.status_code = status_code
