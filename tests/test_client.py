import time
from unittest.mock import MagicMock, call, patch

import httpx
import pytest

from simple_apns.client import APNSClient
from simple_apns.exceptions import APNSException, APNSServerError, APNSTokenError


def test_client_init(apns_test_params):
    """Test initializing the APNSClient."""
    with patch("httpx.Client"):
        client = APNSClient(**apns_test_params)

        assert client.team_id == "TEAM000000"
        assert client.auth_key_id == "AUTH0000000"
        assert client.auth_key_path == "/path/to/key.p8"
        assert client.bundle_id == "com.example.app"
        assert client.apns_topic == "com.example.app"  # Default to bundle_id
        assert client.timeout == 10  # Default
        assert client.max_retries == 3  # Default

        # Check endpoint based on use_sandbox
        assert client.endpoint == APNSClient.ENDPOINT_DEVELOPMENT

        # Test with production endpoint
        prod_params = apns_test_params.copy()
        prod_params["use_sandbox"] = False
        client = APNSClient(**prod_params)
        assert client.endpoint == APNSClient.ENDPOINT_PRODUCTION


def test_client_init_with_custom_params(apns_test_params):
    """Test initializing the APNSClient with custom parameters."""
    custom_params = apns_test_params.copy()
    custom_params.update(
        {"apns_topic": "com.example.customtopic", "timeout": 15, "max_retries": 5}
    )

    with patch("httpx.Client"):
        client = APNSClient(**custom_params)

        assert client.apns_topic == "com.example.customtopic"
        assert client.timeout == 15
        assert client.max_retries == 5


def test_get_auth_token(mock_client):
    """Test getting an authentication token."""
    with patch(
        "simple_apns.client.create_token", return_value="mock_token"
    ) as mock_create_token:
        # First call should create a new token
        token = mock_client._get_auth_token()
        assert token == "mock_token"
        mock_create_token.assert_called_once()

        # Second call should reuse the cached token
        mock_client._get_auth_token()
        assert mock_create_token.call_count == 1  # Still only called once

        # Set token to expire soon
        mock_client._token_expires_at = time.time() + 60  # 1 minute from now

        # Next call should generate a new token
        token = mock_client._get_auth_token()
        assert token == "mock_token"
        assert mock_create_token.call_count == 2  # Called again


def test_get_headers(mock_client):
    """Test generating request headers."""
    with patch.object(mock_client, "_get_auth_token", return_value="test_token"):
        # Test default headers
        headers = mock_client._get_headers()

        assert headers["authorization"] == "bearer test_token"
        assert headers["apns-topic"] == "com.example.app"
        assert headers["apns-push-type"] == "alert"
        assert headers["apns-priority"] == "10"
        assert headers["content-type"] == "application/json"
        assert "apns-expiration" not in headers

        # Test with expiration and custom priority
        headers = mock_client._get_headers(expiration=1600000000, priority=5)

        assert headers["apns-expiration"] == "1600000000"
        assert headers["apns-priority"] == "5"


def test_send_notification_success(
    mock_client, sample_payload, sample_device_token, mock_response_success
):
    """Test sending a notification successfully."""
    test_headers = {
        "authorization": "bearer test_token",
        "apns-topic": mock_client.apns_topic,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "content-type": "application/json",
    }

    with patch.object(mock_client, "_get_headers", return_value=test_headers):
        with patch.object(
            mock_client.client, "post", return_value=mock_response_success
        ) as mock_post:
            # Call the method
            success = mock_client.send_notification(
                device_token=sample_device_token, payload=sample_payload
            )

            # Assert it returns True
            assert success is True

            # Check that post was called with the expected arguments
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert (
                call_args[0][0]
                == f"{mock_client.endpoint}/3/device/{sample_device_token}"
            )
            assert call_args[1]["json"] == sample_payload.to_dict()
            assert call_args[1]["headers"] == test_headers
            assert call_args[1]["timeout"] == 10


def test_send_notification_with_dict_payload(
    mock_client, sample_device_token, mock_response_success
):
    """Test sending a notification with a dictionary payload."""
    # Create a headers dict with required keys
    test_headers = {
        "authorization": "bearer test_token",
        "apns-topic": mock_client.apns_topic,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "content-type": "application/json",
    }

    with patch.object(mock_client, "_get_headers", return_value=test_headers):
        with patch.object(
            mock_client.client, "post", return_value=mock_response_success
        ) as mock_post:
            # Create a dictionary payload
            dict_payload = {
                "aps": {"alert": {"title": "Dict Test", "body": "Test body"}}
            }

            # Call the method
            success = mock_client.send_notification(
                device_token=sample_device_token, payload=dict_payload
            )

            # Assert it returns True
            assert success is True

            # Check that post was called with the expected arguments
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert (
                call_args[0][0]
                == f"{mock_client.endpoint}/3/device/{sample_device_token}"
            )
            assert call_args[1]["json"] == dict_payload
            assert call_args[1]["headers"] == test_headers
            assert call_args[1]["timeout"] == 10


def test_send_notification_bad_token(
    mock_client, sample_payload, sample_device_token, mock_response_error
):
    """Test sending a notification with a bad device token."""
    with patch.object(mock_client, "_get_headers", return_value={"some": "headers"}):
        with patch.object(
            mock_client.client, "post", return_value=mock_response_error
        ) as mock_post:
            with pytest.raises(APNSTokenError) as excinfo:
                mock_client.send_notification(
                    device_token=sample_device_token, payload=sample_payload
                )

            assert "Invalid device token" in str(excinfo.value)
            mock_post.assert_called_once()


def test_send_notification_server_error_with_retry(
    mock_client, sample_payload, sample_device_token
):
    """Test sending a notification with a server error that triggers retries."""
    with patch.object(mock_client, "_get_headers", return_value={"some": "headers"}):
        # Create server error response
        server_error = MagicMock()
        server_error.status_code = 500
        server_error.json.return_value = {"reason": "InternalServerError"}

        # Success response for the retry
        success_response = MagicMock()
        success_response.status_code = 200

        # Mock post to return server error and then success
        with patch.object(
            mock_client.client, "post", side_effect=[server_error, success_response]
        ) as mock_post:
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                success = mock_client.send_notification(
                    device_token=sample_device_token, payload=sample_payload
                )

                assert success is True
                assert mock_post.call_count == 2  # Original request + 1 retry
                assert mock_sleep.call_count == 1  # Should sleep between retries


def test_send_notification_max_retries_exceeded(
    mock_client, sample_payload, sample_device_token
):
    """Test sending a notification where max retries are exceeded."""
    test_headers = {
        "authorization": "bearer test_token",
        "apns-topic": mock_client.apns_topic,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "content-type": "application/json",
    }

    with patch.object(mock_client, "_get_headers", return_value=test_headers):
        # Create server error response
        server_error = MagicMock()
        server_error.status_code = 500
        server_error.json.return_value = {"reason": "InternalServerError"}

        # Mock post to always return server error
        with patch.object(
            mock_client.client, "post", return_value=server_error
        ) as mock_post:
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                with pytest.raises(APNSServerError) as excinfo:
                    mock_client.send_notification(
                        device_token=sample_device_token, payload=sample_payload
                    )

                # Check a substring of the error message
                error_message = str(excinfo.value)
                assert "server error" in error_message
                assert "500" in error_message  # Status code should be in the message

                # Check call counts
                assert (
                    mock_post.call_count == 1 + mock_client.max_retries
                )  # Initial + retries
                assert (
                    mock_sleep.call_count == mock_client.max_retries
                )  # Sleep between retries


def test_send_notification_network_error(
    mock_client, sample_payload, sample_device_token
):
    """Test sending a notification with a network error."""
    with patch.object(mock_client, "_get_headers", return_value={"some": "headers"}):
        # Mock post to raise a network error
        with patch.object(
            mock_client.client, "post", side_effect=httpx.RequestError("Network error")
        ) as mock_post:
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                with pytest.raises(APNSException) as excinfo:
                    mock_client.send_notification(
                        device_token=sample_device_token, payload=sample_payload
                    )

                assert "Network error" in str(excinfo.value)
                assert mock_post.call_count == 1 + mock_client.max_retries
                assert mock_sleep.call_count == mock_client.max_retries


def test_send_notification_with_custom_options(
    mock_client, sample_payload, sample_device_token, mock_response_success
):
    """Test sending a notification with custom options."""
    with patch.object(mock_client, "_get_headers") as mock_get_headers:
        mock_get_headers.return_value = {"some": "headers"}

        with patch.object(
            mock_client.client, "post", return_value=mock_response_success
        ) as mock_post:
            success = mock_client.send_notification(
                device_token=sample_device_token,
                payload=sample_payload,
                push_type="background",
                priority=5,
                expiration=1600000000,
                collapse_id="group-123",
            )

            assert success is True

            # Check that headers were requested with the right parameters
            mock_get_headers.assert_called_once_with(sample_device_token, 1600000000, 5)

            # Check that the headers were modified
            headers = mock_post.call_args[1]["headers"]
            assert headers["apns-push-type"] == "background"
            assert "apns-collapse-id" in headers
            assert headers["apns-collapse-id"] == "group-123"


def test_send_bulk_notifications(mock_client, sample_payload):
    """Test sending bulk notifications."""
    device_tokens = ["token1", "token2", "token3"]

    # Mock send_notification to succeed for token1 and token3, fail for token2
    def mock_send(device_token, **kwargs):
        if device_token == "token2":
            raise APNSException("Test error")
        return True

    with patch.object(
        mock_client, "send_notification", side_effect=mock_send
    ) as mock_send_notification:
        results = mock_client.send_bulk_notifications(
            device_tokens=device_tokens, payload=sample_payload
        )

        # Check results
        assert results == {"token1": True, "token2": False, "token3": True}

        # Check that send_notification was called for each token
        assert mock_send_notification.call_count == 3
        mock_send_notification.assert_has_calls(
            [
                call(
                    device_token="token1",
                    payload=sample_payload,
                    push_type="alert",
                    priority=10,
                    expiration=None,
                    collapse_id=None,
                ),
                call(
                    device_token="token2",
                    payload=sample_payload,
                    push_type="alert",
                    priority=10,
                    expiration=None,
                    collapse_id=None,
                ),
                call(
                    device_token="token3",
                    payload=sample_payload,
                    push_type="alert",
                    priority=10,
                    expiration=None,
                    collapse_id=None,
                ),
            ],
            any_order=False,
        )


def test_send_bulk_notifications_with_options(mock_client, sample_payload):
    """Test sending bulk notifications with custom options."""
    device_tokens = ["token1", "token2"]

    with patch.object(
        mock_client, "send_notification", return_value=True
    ) as mock_send_notification:
        results = mock_client.send_bulk_notifications(
            device_tokens=device_tokens,
            payload=sample_payload,
            push_type="background",
            priority=5,
            expiration=1600000000,
            collapse_id="bulk-group",
        )

        # Check results
        assert results == {"token1": True, "token2": True}

        # Check that options were passed to send_notification
        mock_send_notification.assert_has_calls(
            [
                call(
                    device_token="token1",
                    payload=sample_payload,
                    push_type="background",
                    priority=5,
                    expiration=1600000000,
                    collapse_id="bulk-group",
                ),
                call(
                    device_token="token2",
                    payload=sample_payload,
                    push_type="background",
                    priority=5,
                    expiration=1600000000,
                    collapse_id="bulk-group",
                ),
            ]
        )


def test_client_close(mock_client):
    """Test closing the client."""
    with patch.object(mock_client.client, "close") as mock_close:
        mock_client.close()
        mock_close.assert_called_once()
