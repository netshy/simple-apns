"""
simple-apns - Synchronous Python client for Apple Push Notification Service
"""

from .auth import create_token
from .client import APNSClient
from .exceptions import (
    APNSAuthError,
    APNSException,
    APNSPayloadError,
    APNSServerError,
    APNSTimeoutError,
    APNSTokenError,
)
from .payload import Payload

__version__ = "0.1.1"
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
