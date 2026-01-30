import time
from typing import Dict, List, Optional, Union

import httpx

from .auth import create_token
from .exceptions import APNSException, APNSServerError, APNSTokenError, APNSTimeoutError
from .payload import Payload


class APNSClient:
    """
    Synchronous client for Apple Push Notification Service.

    This client uses httpx to make HTTP/2 requests to the APNS servers.
    """

    # Production and development endpoints
    ENDPOINT_PRODUCTION = "https://api.push.apple.com"
    ENDPOINT_DEVELOPMENT = "https://api.development.push.apple.com"

    def __init__(
        self,
        team_id: str,
        auth_key_id: str,
        auth_key_path: str,
        bundle_id: str,
        use_sandbox: bool = False,
        apns_topic: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the APNS client.

        Args:
            team_id: Apple Developer Team ID
            auth_key_id: Auth key ID (from developer portal)
            auth_key_path: Path to the .p8 file
            bundle_id: App bundle ID
            use_sandbox: Use development environment
            apns_topic: Optional custom APNs topic
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failures
        """
        self.team_id = team_id
        self.auth_key_id = auth_key_id
        self.auth_key_path = auth_key_path
        self.bundle_id = bundle_id
        self.apns_topic = apns_topic or bundle_id
        self.timeout = timeout
        self.max_retries = max_retries

        self.endpoint = (
            self.ENDPOINT_DEVELOPMENT if use_sandbox else self.ENDPOINT_PRODUCTION
        )

        self._token = None
        self._token_expires_at = 0

        timeout_config = httpx.Timeout(
            connect=5.0,
            read=timeout,
            write=5.0,
            pool=2.0,
        )

        limits = httpx.Limits(
            max_keepalive_connections=10,
            max_connections=20,
            keepalive_expiry=30.0,
        )

        self.client = httpx.Client(
            http2=True,
            timeout=timeout_config,
            limits=limits,
        )

    def _get_auth_token(self) -> str:
        """
        Get a valid authentication token or generate a new one if needed.
        """
        current_time = time.time()

        if not self._token or current_time > (self._token_expires_at - 300):
            self._token = create_token(
                team_id=self.team_id,
                auth_key_id=self.auth_key_id,
                auth_key_path=self.auth_key_path,
            )
            self._token_expires_at = current_time + 3600

        return self._token

    def _get_headers(
        self, expiration: Optional[int] = None, priority: int = 10
    ) -> Dict:
        """
        Create request headers for APNS.

        Args:
            expiration: Notification expiration time (epoch timestamp)
            priority: The notification priority (10=immediate, 5=conserve power)

        Returns:
            Dictionary of headers
        """
        headers = {
            "authorization": f"bearer {self._get_auth_token()}",
            "apns-topic": self.apns_topic,
            "apns-push-type": "alert",  # Default to alert, can be overridden
            "apns-priority": str(priority),
            "content-type": "application/json",
        }

        if expiration:
            headers["apns-expiration"] = str(expiration)

        return headers

    def send_notification(
        self,
        device_token: str,
        payload: Union[Payload, Dict],
        push_type: str = "alert",
        priority: int = 10,
        expiration: Optional[int] = None,
        collapse_id: Optional[str] = None,
    ) -> bool:
        """
        Send a notification to a device.

        Args:
            device_token: The target device token
            payload: Notification payload (Payload object or dictionary)
            push_type: APNS push type (alert, background, voip, etc.)
            priority: The notification priority (10=immediate, 5=conserve power)
            expiration: Notification expiration time (epoch timestamp)
            collapse_id: A string that identifies a group of notifications that can be replaced

        Returns:
            True if the notification was sent successfully

        Raises:
            APNSException: Base exception for all APNS-related errors
            APNSTokenError: Invalid device token
            APNSServerError: Server error from Apple
        """
        # Convert payload to dictionary if it's a Payload object
        if isinstance(payload, Payload):
            payload_dict = payload.to_dict()
        else:
            payload_dict = payload

        url = f"{self.endpoint}/3/device/{device_token}"

        headers = self._get_headers(expiration, priority)
        headers["apns-push-type"] = push_type

        if collapse_id:
            headers["apns-collapse-id"] = collapse_id

        retries = 0

        while retries <= self.max_retries:
            try:
                response = self.client.post(url, json=payload_dict, headers=headers)

                if response.status_code == 200:
                    return True

                error_response = response.json()

                if response.status_code == 400:
                    reason = error_response.get("reason", "BadRequest")
                    if reason == "BadDeviceToken":
                        raise APNSTokenError(f"Invalid device token: {device_token}")
                    raise APNSException(f"Bad request: {reason}")

                if response.status_code == 403:
                    raise APNSException("Certificate or token is not valid")

                if response.status_code == 410:
                    raise APNSTokenError(f"Token is no longer valid: {device_token}")

                retries += 1
                if retries <= self.max_retries:
                    time.sleep(0.5 * retries)
                    continue

                raise APNSServerError(
                    f"APNS server error: {response.status_code}, {error_response.get('reason', 'Unknown')}"
                )

            except httpx.TimeoutException as e:
                raise APNSTimeoutError(
                    f"Request timed out after {self.timeout}s for token {device_token[:8]}..."
                ) from e

            except httpx.RequestError as e:
                retries += 1
                if retries <= self.max_retries:
                    time.sleep(0.5 * retries)
                    continue

                raise APNSException(f"Network error: {str(e)}")

        raise APNSServerError("Failed to send notification after maximum retries")

    def send_bulk_notifications(
        self,
        device_tokens: List[str],
        payload: Union[Payload, Dict],
        push_type: str = "alert",
        priority: int = 10,
        expiration: Optional[int] = None,
        collapse_id: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        Send a notification to multiple devices.

        Args:
            device_tokens: List of target device tokens
            payload: Notification payload (Payload object or dictionary)
            push_type: APNS push type (alert, background, voip, etc.)
            priority: The notification priority (10=immediate, 5=conserve power)
            expiration: Notification expiration time (epoch timestamp)
            collapse_id: A string that identifies a group of notifications that can be replaced

        Returns:
            Dictionary mapping device tokens to success status
        """
        results = {}

        for token in device_tokens:
            try:
                success = self.send_notification(
                    device_token=token,
                    payload=payload,
                    push_type=push_type,
                    priority=priority,
                    expiration=expiration,
                    collapse_id=collapse_id,
                )
                results[token] = success
            except APNSException:
                results[token] = False

        return results

    def close(self):
        """
        Close the HTTP client and free resources.
        """
        if self.client:
            self.client.close()
