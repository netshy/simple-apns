import time
from pathlib import Path
from typing import Optional

import jwt  # PyJWT library


def create_token(
    team_id: str,
    auth_key_id: str,
    auth_key_path: str,
    auth_key_content: Optional[str] = None,
    expiration_time: int = 3600,  # 1 hour
) -> str:
    """
    Create an authentication token for APNS.

    This function creates a JWT token signed with the private key,
    as required by Apple for authentication with the APNS service.

    Args:
        team_id: Apple Developer Team ID
        auth_key_id: Auth key ID (from developer portal)
        auth_key_path: Path to the .p8 file (can be None if auth_key_content is provided)
        auth_key_content: Content of the .p8 file (can be None if auth_key_path is provided)
        expiration_time: Token expiration time in seconds (default: 1 hour)

    Returns:
        JWT token as a string

    Raises:
        FileNotFoundError: If the auth key file doesn't exist
        ValueError: If neither auth_key_path nor auth_key_content is provided
    """
    if not auth_key_content and not auth_key_path:
        raise ValueError("Either auth_key_path or auth_key_content must be provided")

    # Read the authentication key
    if auth_key_content:
        private_key = auth_key_content
    else:
        key_path = Path(auth_key_path)
        if not key_path.exists():
            raise FileNotFoundError(
                f"Authentication key file not found: {auth_key_path}"
            )

        with open(key_path, "r") as key_file:
            private_key = key_file.read()

    # Prepare token headers and payload
    token_headers = {
        "alg": "ES256",
        "kid": auth_key_id,
    }

    current_time = int(time.time())
    token_payload = {
        "iss": team_id,
        "iat": current_time,
        "exp": current_time + expiration_time,
    }

    # Create and sign the JWT token
    token = jwt.encode(
        payload=token_payload,
        key=private_key,
        algorithm="ES256",
        headers=token_headers,
    )

    return token
