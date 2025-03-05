import pytest
from simple_apns.exceptions import (
    APNSException,
    APNSAuthError,
    APNSTokenError,
    APNSServerError,
    APNSPayloadError,
    APNSTimeoutError
)


def test_exception_hierarchy():
    """Test the exception class hierarchy."""
    # Base exception
    base_exc = APNSException("Base exception")
    assert isinstance(base_exc, Exception)
    assert str(base_exc) == "Base exception"

    # Auth error
    auth_exc = APNSAuthError("Auth error")
    assert isinstance(auth_exc, APNSException)
    assert isinstance(auth_exc, Exception)
    assert str(auth_exc) == "Auth error"

    # Token error
    token_exc = APNSTokenError("Token error")
    assert isinstance(token_exc, APNSException)
    assert isinstance(token_exc, Exception)
    assert str(token_exc) == "Token error"

    # Server error
    server_exc = APNSServerError("Server error")
    assert isinstance(server_exc, APNSException)
    assert isinstance(server_exc, Exception)
    assert str(server_exc) == "Server error"

    # Payload error
    payload_exc = APNSPayloadError("Payload error")
    assert isinstance(payload_exc, APNSException)
    assert isinstance(payload_exc, Exception)
    assert str(payload_exc) == "Payload error"

    # Timeout error
    timeout_exc = APNSTimeoutError("Timeout error")
    assert isinstance(timeout_exc, APNSException)
    assert isinstance(timeout_exc, Exception)
    assert str(timeout_exc) == "Timeout error"


def test_exception_with_details():
    """Test exceptions with additional details."""
    # Test with additional details
    exc = APNSServerError("APNS server returned status 500 with reason: InternalServerError")
    assert "status 500" in str(exc)
    assert "InternalServerError" in str(exc)


def test_catching_specific_exceptions():
    """Test the ability to catch specific exception types."""

    def raise_token_error():
        raise APNSTokenError("Invalid token")

    # Test catching specific exception
    with pytest.raises(APNSTokenError):
        raise_token_error()

    # Test catching base exception type
    with pytest.raises(APNSException):
        raise_token_error()

    # Test that other specific types are not caught
    with pytest.raises(APNSTokenError):
        try:
            raise_token_error()
        except APNSServerError:
            pytest.fail("Should not catch APNSServerError")