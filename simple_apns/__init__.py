"""
simple-apns - Synchronous Python client for Apple Push Notification Service
"""

from .client import APNSClient
from .payload import Payload
from .auth import create_token
from .exceptions import (
    APNSException,
    APNSAuthError,
    APNSTokenError,
    APNSServerError,
    APNSPayloadError,
    APNSTimeoutError
)

__version__ = "0.1.0"
__all__ = [
    "APNSClient",
    "Payload",
    "create_token",
    "APNSException",
    "APNSAuthError",
    "APNSTokenError",
    "APNSServerError",
    "APNSPayloadError",
    "APNSTimeoutError",
]