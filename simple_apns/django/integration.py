from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ..client import APNSClient
from ..payload import Payload


@lru_cache(maxsize=1)
def get_apns_client() -> APNSClient:
    """
    Get or create a cached APNSClient instance from Django settings.

    The client is configured using the SIMPLE_APNS settings in your Django settings file.
    It is cached for performance using lru_cache.

    Required settings:
    - SIMPLE_APNS['TEAM_ID']
    - SIMPLE_APNS['AUTH_KEY_ID']
    - SIMPLE_APNS['AUTH_KEY_PATH']
    - SIMPLE_APNS['BUNDLE_ID']

    Optional settings:
    - SIMPLE_APNS['USE_SANDBOX'] (default: False)
    - SIMPLE_APNS['APNS_TOPIC'] (default: BUNDLE_ID)
    - SIMPLE_APNS['TIMEOUT'] (default: 10)
    - SIMPLE_APNS['MAX_RETRIES'] (default: 3)

    Returns:
        Configured APNSClient instance

    Raises:
        ImproperlyConfigured: If required settings are missing
    """
    # Check if the settings are configured
    if not hasattr(settings, "SIMPLE_APNS"):
        raise ImproperlyConfigured(
            "SIMPLE_APNS settings are missing in your Django settings"
        )

    apns_settings = settings.SIMPLE_APNS

    # Check required settings
    required_settings = ["TEAM_ID", "AUTH_KEY_ID", "AUTH_KEY_PATH", "BUNDLE_ID"]
    missing_settings = [s for s in required_settings if s not in apns_settings]

    if missing_settings:
        raise ImproperlyConfigured(
            f"SIMPLE_APNS settings are missing the following required keys: {', '.join(missing_settings)}"
        )

    # Create the client with settings
    client = APNSClient(
        team_id=apns_settings["TEAM_ID"],
        auth_key_id=apns_settings["AUTH_KEY_ID"],
        auth_key_path=apns_settings["AUTH_KEY_PATH"],
        bundle_id=apns_settings["BUNDLE_ID"],
        use_sandbox=apns_settings.get("USE_SANDBOX", False),
        apns_topic=apns_settings.get("APNS_TOPIC"),
        timeout=apns_settings.get("TIMEOUT", 10),
        max_retries=apns_settings.get("MAX_RETRIES", 3),
    )

    return client


def _create_payload(
        title: Optional[str] = None,
        body: Optional[str] = None,
        badge: Optional[int] = None,
        sound: Optional[Union[str, Dict]] = None,
        category: Optional[str] = None,
        thread_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        content_available: bool = False,
        mutable_content: bool = False,
) -> Payload:
    """
    Create and configure an APNS Payload object.

    This is a helper function used by send_notification and send_bulk_notifications.

    Args:
        title: The notification title
        body: The notification body
        badge: Badge count to display
        sound: Sound to play
        category: Notification category
        thread_id: Thread identifier for grouping
        extra_data: Custom data to include in the payload
        content_available: Whether content is available in the background
        mutable_content: Whether the content can be modified by extensions

    Returns:
        Configured Payload object
    """
    # Create a payload
    payload = Payload(alert_title=title, alert_body=body)

    if badge is not None:
        payload.set_badge(badge)

    if sound:
        payload.set_sound(sound)

    if category:
        payload.set_category(category)

    if thread_id:
        payload.set_thread_id(thread_id)

    if content_available:
        payload.set_content_available(True)

    if mutable_content:
        payload.set_mutable_content(True)

    # Add any extra data
    if extra_data:
        for key, value in extra_data.items():
            payload.add_custom_data(key, value)

    return payload


def send_notification(
        device_token: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        badge: Optional[int] = None,
        sound: Optional[Union[str, Dict]] = None,
        category: Optional[str] = None,
        thread_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        content_available: bool = False,
        mutable_content: bool = False,
        push_type: str = "alert",
        priority: int = 10,
) -> bool:
    """
    Send a notification to a device using the Django integration.

    Args:
        device_token: The target device token
        title: The notification title
        body: The notification body
        badge: Badge count to display
        sound: Sound to play
        category: Notification category
        thread_id: Thread identifier for grouping
        extra_data: Custom data to include in the payload
        content_available: Whether content is available in the background
        mutable_content: Whether the content can be modified by extensions
        push_type: APNS push type (alert, background, voip, etc.)
        priority: Notification priority (10=immediate, 5=conserve power)

    Returns:
        True if the notification was sent successfully

    Raises:
        APNSException: If there was an error sending the notification
        ImproperlyConfigured: If the SIMPLE_APNS settings are missing or incomplete
    """
    # Create the payload using the helper function
    payload = _create_payload(
        title=title,
        body=body,
        badge=badge,
        sound=sound,
        category=category,
        thread_id=thread_id,
        extra_data=extra_data,
        content_available=content_available,
        mutable_content=mutable_content,
    )

    # Get the client and send the notification
    client = get_apns_client()
    return client.send_notification(
        device_token=device_token,
        payload=payload,
        push_type=push_type,
        priority=priority,
    )


def send_bulk_notifications(
        device_tokens: List[str],
        title: Optional[str] = None,
        body: Optional[str] = None,
        badge: Optional[int] = None,
        sound: Optional[Union[str, Dict]] = None,
        category: Optional[str] = None,
        thread_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        content_available: bool = False,
        mutable_content: bool = False,
        push_type: str = "alert",
        priority: int = 10,
) -> Dict[str, bool]:
    """
    Send a notification to multiple devices using the Django integration.

    Args:
        device_tokens: List of target device tokens
        title: The notification title
        body: The notification body
        badge: Badge count to display
        sound: Sound to play
        category: Notification category
        thread_id: Thread identifier for grouping
        extra_data: Custom data to include in the payload
        content_available: Whether content is available in the background
        mutable_content: Whether the content can be modified by extensions
        push_type: APNS push type (alert, background, voip, etc.)
        priority: Notification priority (10=immediate, 5=conserve power)

    Returns:
        Dictionary mapping device tokens to success status

    Raises:
        ImproperlyConfigured: If the SIMPLE_APNS settings are missing or incomplete
    """
    # Create the payload using the helper function
    payload = _create_payload(
        title=title,
        body=body,
        badge=badge,
        sound=sound,
        category=category,
        thread_id=thread_id,
        extra_data=extra_data,
        content_available=content_available,
        mutable_content=mutable_content,
    )

    # Get the client and send the notifications
    client = get_apns_client()
    return client.send_bulk_notifications(
        device_tokens=device_tokens,
        payload=payload,
        push_type=push_type,
        priority=priority,
    )


def reset_apns_client():
    """
    Reset the cached APNSClient.

    This is useful for testing or when the settings have changed.
    """
    get_apns_client.cache_clear()
