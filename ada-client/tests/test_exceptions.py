"""Basic tests for ada_client.exceptions module."""

import pytest

from ada_client.exceptions import (
    AdaBrainError,
    AdaBrainConnectionError,
    AdaBrainResponseError,
)


def test_base_exception():
    """Test AdaBrainError base exception."""
    exc = AdaBrainError("test error")
    assert str(exc) == "test error"
    assert isinstance(exc, Exception)


def test_connection_error():
    """Test AdaBrainConnectionError."""
    exc = AdaBrainConnectionError("connection failed")
    assert str(exc) == "connection failed"
    assert isinstance(exc, AdaBrainError)
    assert isinstance(exc, Exception)


def test_response_error_basic():
    """Test AdaBrainResponseError without status code."""
    exc = AdaBrainResponseError("bad request")
    assert str(exc) == "bad request"
    assert exc.status_code is None
    assert isinstance(exc, AdaBrainError)


def test_response_error_with_status():
    """Test AdaBrainResponseError with status code."""
    exc = AdaBrainResponseError("not found", status_code=404)
    assert str(exc) == "not found"
    assert exc.status_code == 404
    assert isinstance(exc, AdaBrainError)


def test_exception_hierarchy():
    """Test exception inheritance hierarchy."""
    # All exceptions should inherit from AdaBrainError
    assert issubclass(AdaBrainConnectionError, AdaBrainError)
    assert issubclass(AdaBrainResponseError, AdaBrainError)
    
    # All should ultimately be Exceptions
    assert issubclass(AdaBrainError, Exception)
    assert issubclass(AdaBrainConnectionError, Exception)
    assert issubclass(AdaBrainResponseError, Exception)


def test_catching_base_exception():
    """Test that base exception catches specific exceptions."""
    try:
        raise AdaBrainConnectionError("test")
    except AdaBrainError:
        pass  # Should be caught
    else:
        pytest.fail("AdaBrainConnectionError should be caught by AdaBrainError")
    
    try:
        raise AdaBrainResponseError("test", 500)
    except AdaBrainError:
        pass  # Should be caught
    else:
        pytest.fail("AdaBrainResponseError should be caught by AdaBrainError")
