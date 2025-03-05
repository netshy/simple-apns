import os
import pytest
import jwt
from pathlib import Path
from unittest.mock import patch, mock_open

from simple_apns.auth import create_token
from simple_apns.exceptions import APNSAuthError


def test_create_token_with_file_path(mock_private_key):
    """Test creating a token using a file path."""
    # Create a mock file path
    mock_file_path = "/path/to/key.p8"

    # Mock the file open operation
    with patch("builtins.open", mock_open(read_data=mock_private_key)):
        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Create the token
            token = create_token(
                team_id="TEAM000000",
                auth_key_id="AUTH0000000",
                auth_key_path=mock_file_path,
                expiration_time=3600
            )

            # Assert the token is a string
            assert isinstance(token, str)

            # Decode the token to verify its structure
            # Note: We don't verify the signature here as we'd need the public key
            decoded = jwt.decode(token, options={"verify_signature": False})

            # Check JWT payload
            assert "iss" in decoded
            assert decoded["iss"] == "TEAM000000"
            assert "iat" in decoded
            assert "exp" in decoded
            assert decoded["exp"] - decoded["iat"] == 3600

            # Check JWT headers
            headers = jwt.get_unverified_header(token)
            assert headers["alg"] == "ES256"
            assert headers["kid"] == "AUTH0000000"


def test_create_token_with_key_content(mock_private_key):
    """Test creating a token using key content directly."""
    # Create the token
    token = create_token(
        team_id="TEAM000000",
        auth_key_id="AUTH0000000",
        auth_key_path=None,
        auth_key_content=mock_private_key,
        expiration_time=3600
    )

    # Assert the token is a string
    assert isinstance(token, str)

    # Decode the token to verify its structure
    decoded = jwt.decode(token, options={"verify_signature": False})

    # Check JWT payload
    assert decoded["iss"] == "TEAM000000"
    assert "iat" in decoded
    assert "exp" in decoded


def test_create_token_file_not_found():
    """Test error handling when key file is not found."""
    # Mock Path.exists to return False
    with patch.object(Path, "exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            create_token(
                team_id="TEAM000000",
                auth_key_id="AUTH0000000",
                auth_key_path="/nonexistent/path.p8",
                expiration_time=3600
            )


def test_create_token_missing_parameters():
    """Test error handling when neither path nor content is provided."""
    with pytest.raises(ValueError) as excinfo:
        create_token(
            team_id="TEAM000000",
            auth_key_id="AUTH0000000",
            auth_key_path=None,
            auth_key_content=None,
            expiration_time=3600
        )

    assert "Either auth_key_path or auth_key_content must be provided" in str(excinfo.value)


def test_create_token_with_custom_expiration(mock_private_key):
    """Test creating a token with a custom expiration time."""
    # Mock the file open operation
    with patch("builtins.open", mock_open(read_data=mock_private_key)):
        # Mock Path.exists to return True
        with patch.object(Path, "exists", return_value=True):
            # Create tokens with different expiration times
            token1 = create_token(
                team_id="TEAM000000",
                auth_key_id="AUTH0000000",
                auth_key_path="/path/to/key.p8",
                expiration_time=1800  # 30 minutes
            )

            token2 = create_token(
                team_id="TEAM000000",
                auth_key_id="AUTH0000000",
                auth_key_path="/path/to/key.p8",
                expiration_time=7200  # 2 hours
            )

            # Decode the tokens
            decoded1 = jwt.decode(token1, options={"verify_signature": False})
            decoded2 = jwt.decode(token2, options={"verify_signature": False})

            # Check that expiration times differ correctly
            assert decoded1["exp"] - decoded1["iat"] == 1800
            assert decoded2["exp"] - decoded2["iat"] == 7200