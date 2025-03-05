"""
Django integration for simple-apns
"""

from .integration import (
    get_apns_client,
    reset_apns_client,
    send_bulk_notifications,
    send_notification,
)

default_app_config = "simple_apns.django.apps.SimpleAPNSConfig"

__all__ = [
    "get_apns_client",
    "send_notification",
    "send_bulk_notifications",
    "reset_apns_client",
]
