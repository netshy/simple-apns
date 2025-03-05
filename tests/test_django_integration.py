# Configure Django settings for testing
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

# Set up Django configuration early
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sites",
        "simple_apns.django",
    ],
    SITE_ID=1,
    MIDDLEWARE_CLASSES=(),
    SECRET_KEY="secret-key-for-testing",
    SIMPLE_APNS={
        "TEAM_ID": "DJANGO_TEAM_ID",
        "AUTH_KEY_ID": "DJANGO_AUTH_KEY_ID",
        "AUTH_KEY_PATH": "/path/to/django_key.p8",
        "BUNDLE_ID": "com.example.djangoapp",
        "USE_SANDBOX": True,
    },
)
django.setup()

# Mark all tests as requiring the Django DB
pytestmark = pytest.mark.django_db


# We need to patch Django's settings module for testing
@pytest.fixture
def mock_django_settings():
    """
    This fixture now modifies the existing Django settings
    rather than completely mocking them.
    """
    # Save original settings
    original_settings = {}
    if hasattr(settings, "SIMPLE_APNS"):
        original_settings = settings.SIMPLE_APNS.copy()

    # Update settings for test
    settings.SIMPLE_APNS = {
        "TEAM_ID": "DJANGO_TEAM_ID",
        "AUTH_KEY_ID": "DJANGO_AUTH_KEY_ID",
        "AUTH_KEY_PATH": "/path/to/django_key.p8",
        "BUNDLE_ID": "com.example.djangoapp",
        "USE_SANDBOX": True,
        "TIMEOUT": 15,
        "MAX_RETRIES": 2,
    }

    yield settings

    # Restore original settings
    if original_settings:
        settings.SIMPLE_APNS = original_settings


def test_get_apns_client(mock_django_settings):
    """Test getting the APNSClient from Django settings."""
    with patch("simple_apns.django.integration.APNSClient") as mock_client_class:
        # Import the function
        from simple_apns.django.integration import get_apns_client

        # Clear the cache to ensure a new client is created
        get_apns_client.cache_clear()

        # Get the client
        client = get_apns_client()

        # Check that the client was created with the right settings
        mock_client_class.assert_called_once_with(
            team_id="DJANGO_TEAM_ID",
            auth_key_id="DJANGO_AUTH_KEY_ID",
            auth_key_path="/path/to/django_key.p8",
            bundle_id="com.example.djangoapp",
            use_sandbox=True,
            apns_topic=None,  # Should default to None
            timeout=15,
            max_retries=2,
        )

        # Calling get_apns_client again should return the cached client
        with patch("simple_apns.django.integration.APNSClient") as second_mock:
            second_client = get_apns_client()
            second_mock.assert_not_called()  # Should use cached client


def test_get_apns_client_missing_settings():
    """Test error handling when settings are missing."""
    # Import first
    from django.core.exceptions import ImproperlyConfigured

    from simple_apns.django.integration import get_apns_client

    # Clear the cache to ensure a new client is created
    get_apns_client.cache_clear()

    # Temporarily modify settings to remove SIMPLE_APNS
    original_simple_apns = None
    if hasattr(settings, "SIMPLE_APNS"):
        original_simple_apns = settings.SIMPLE_APNS
        delattr(settings, "SIMPLE_APNS")

    try:
        # Attempt to get the client
        with pytest.raises(ImproperlyConfigured) as excinfo:
            get_apns_client()

        assert "SIMPLE_APNS settings are missing" in str(excinfo.value)
    finally:
        # Restore original settings
        if original_simple_apns is not None:
            settings.SIMPLE_APNS = original_simple_apns


def test_get_apns_client_incomplete_settings():
    """Test error handling when settings are incomplete."""
    # Import first
    from django.core.exceptions import ImproperlyConfigured

    from simple_apns.django.integration import get_apns_client

    # Clear the cache to ensure a new client is created
    get_apns_client.cache_clear()

    # Save original settings
    original_simple_apns = None
    if hasattr(settings, "SIMPLE_APNS"):
        original_simple_apns = settings.SIMPLE_APNS.copy()

    try:
        # Set incomplete settings
        settings.SIMPLE_APNS = {
            "TEAM_ID": "DJANGO_TEAM_ID",
            # Missing AUTH_KEY_ID
            "AUTH_KEY_PATH": "/path/to/django_key.p8",
            "BUNDLE_ID": "com.example.djangoapp",
        }

        # Attempt to get the client
        with pytest.raises(ImproperlyConfigured) as excinfo:
            get_apns_client()

        assert "AUTH_KEY_ID" in str(excinfo.value)
    finally:
        # Restore original settings
        if original_simple_apns is not None:
            settings.SIMPLE_APNS = original_simple_apns


def test_create_payload():
    """Test the _create_payload helper function."""
    from simple_apns.django.integration import _create_payload

    # Test creating a basic payload
    payload = _create_payload(
        title="Django Notification",
        body="This is a Django notification",
        badge=3,
        sound="default",
        category="DJANGO_CATEGORY",
        thread_id="django-thread-1",
        extra_data={"django_key": "django_value"},
        content_available=True,
        mutable_content=True,
    )

    # Convert to dict for easier assertion
    payload_dict = payload.to_dict()

    # Check the payload structure
    assert payload_dict["aps"]["alert"]["title"] == "Django Notification"
    assert payload_dict["aps"]["alert"]["body"] == "This is a Django notification"
    assert payload_dict["aps"]["badge"] == 3
    assert payload_dict["aps"]["sound"] == "default"
    assert payload_dict["aps"]["category"] == "DJANGO_CATEGORY"
    assert payload_dict["aps"]["thread-id"] == "django-thread-1"
    assert payload_dict["aps"]["content-available"] == 1
    assert payload_dict["aps"]["mutable-content"] == 1
    assert payload_dict["django_key"] == "django_value"


def test_send_notification(mock_django_settings):
    """Test the send_notification function."""
    # Import first
    from simple_apns.django.integration import send_notification

    # Mock the APNSClient and its send_notification method
    mock_client = MagicMock()
    mock_client.send_notification.return_value = True

    with patch(
        "simple_apns.django.integration.get_apns_client", return_value=mock_client
    ):
        # Send a notification
        result = send_notification(
            device_token="django-device-token",
            title="Django Title",
            body="Django Body",
            badge=2,
            sound="django_sound",
            category="DJANGO_CAT",
            thread_id="django-thread",
            extra_data={"key1": "value1", "key2": "value2"},
            content_available=True,
            push_type="background",
            priority=5,
        )

        # Check the result
        assert result is True

        # Check that the client's send_notification was called correctly
        mock_client.send_notification.assert_called_once()

        # Get the payload that was passed to send_notification
        args, kwargs = mock_client.send_notification.call_args
        assert kwargs["device_token"] == "django-device-token"
        assert kwargs["push_type"] == "background"
        assert kwargs["priority"] == 5

        # Convert the payload to dict and check its structure
        payload_dict = kwargs["payload"].to_dict()
        assert payload_dict["aps"]["alert"]["title"] == "Django Title"
        assert payload_dict["aps"]["alert"]["body"] == "Django Body"
        assert payload_dict["aps"]["badge"] == 2
        assert payload_dict["aps"]["sound"] == "django_sound"
        assert payload_dict["aps"]["category"] == "DJANGO_CAT"
        assert payload_dict["aps"]["thread-id"] == "django-thread"
        assert payload_dict["aps"]["content-available"] == 1
        assert payload_dict["key1"] == "value1"
        assert payload_dict["key2"] == "value2"


def test_send_bulk_notifications(mock_django_settings):
    """Test the send_bulk_notifications function."""
    # Import first
    from simple_apns.django.integration import send_bulk_notifications

    # Mock the APNSClient and its send_bulk_notifications method
    mock_client = MagicMock()
    mock_client.send_bulk_notifications.return_value = {"token1": True, "token2": False}

    with patch(
        "simple_apns.django.integration.get_apns_client", return_value=mock_client
    ):
        # Send bulk notifications
        device_tokens = ["token1", "token2"]
        result = send_bulk_notifications(
            device_tokens=device_tokens,
            title="Bulk Title",
            body="Bulk Body",
            extra_data={"bulk_key": "bulk_value"},
            priority=5,
        )

        # Check the result
        assert result == {"token1": True, "token2": False}

        # Check that the client's send_bulk_notifications was called correctly
        mock_client.send_bulk_notifications.assert_called_once()

        # Get the arguments that were passed to send_bulk_notifications
        args, kwargs = mock_client.send_bulk_notifications.call_args
        assert kwargs["device_tokens"] == device_tokens
        assert kwargs["priority"] == 5

        # Convert the payload to dict and check its structure
        payload_dict = kwargs["payload"].to_dict()
        assert payload_dict["aps"]["alert"]["title"] == "Bulk Title"
        assert payload_dict["aps"]["alert"]["body"] == "Bulk Body"
        assert payload_dict["bulk_key"] == "bulk_value"


def test_reset_apns_client(mock_django_settings):
    """Test resetting the APNSClient cache."""
    # Import first
    from simple_apns.django.integration import get_apns_client, reset_apns_client

    with patch("simple_apns.django.integration.APNSClient") as mock_client_class:
        # Get a client (creates a new one)
        get_apns_client.cache_clear()
        client1 = get_apns_client()

        # Reset should clear the cache
        reset_apns_client()

        # Get a client again (should create a new one)
        client2 = get_apns_client()

        # Check that the client class was instantiated twice
        assert mock_client_class.call_count == 2
