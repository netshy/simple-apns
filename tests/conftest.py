import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import httpx

from simple_apns import APNSClient, Payload


@pytest.fixture
def mock_private_key():
    return """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgevZzL1gdAFr88hb2
OF/2NxApJCzGCEDdfSp6VQO30hyhRANCAAQRWz+jn65BtOMvdyHKcvjBeBSDZH2r
1RTwjmYSi9R/zpBnuQ4EiMnCqfMPWiZqB4QdbAd0E7oH50VpuZ1P087G
-----END PRIVATE KEY-----"""


@pytest.fixture
def mock_response_success():
    """Mock a successful response from APNS"""
    response = MagicMock()
    response.status_code = 200
    return response


@pytest.fixture
def mock_response_error():
    """Mock an error response from APNS"""
    response = MagicMock()
    response.status_code = 400
    response.json.return_value = {"reason": "BadDeviceToken"}
    return response


@pytest.fixture
def apns_test_params():
    """Return test parameters for APNSClient"""
    return {
        "team_id": "TEAM000000",
        "auth_key_id": "AUTH0000000",
        "auth_key_path": "/path/to/key.p8",
        "bundle_id": "com.example.app",
        "use_sandbox": True
    }


@pytest.fixture
def mock_client(mock_private_key, apns_test_params, tmp_path):
    """Create a mocked APNSClient"""
    # Create a temporary file with the mock key
    tmp_dir = tmp_path / "keys"
    tmp_dir.mkdir(exist_ok=True)
    key_path = tmp_dir / "AuthKey_test.p8"

    with open(key_path, 'w') as f:
        f.write(mock_private_key)

    # Override the auth_key_path in test params
    test_params = apns_test_params.copy()
    test_params["auth_key_path"] = str(key_path)

    with patch('httpx.Client'):
        client = APNSClient(**test_params)
        yield client


@pytest.fixture
def sample_payload():
    """Create a sample notification payload"""
    payload = Payload(
        alert_title="Test Notification",
        alert_body="This is a test notification"
    )
    payload.set_badge(1)
    payload.set_sound("default")
    payload.add_custom_data("test_key", "test_value")
    return payload


@pytest.fixture
def sample_device_token():
    """Return a sample device token"""
    return "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"