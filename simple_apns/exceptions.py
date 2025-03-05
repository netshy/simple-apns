class APNSException(Exception):
    """Base exception for all APNS-related errors."""
    pass


class APNSAuthError(APNSException):
    """Authentication error with APNS."""
    pass


class APNSTokenError(APNSException):
    """Invalid device token error."""
    pass


class APNSServerError(APNSException):
    """APNS server returned an error."""
    pass


class APNSPayloadError(APNSException):
    """Payload construction error."""
    pass


class APNSTimeoutError(APNSException):
    """Request timed out."""
    pass