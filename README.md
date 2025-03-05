# Simple APNS

A synchronous Python client for Apple Push Notification Service (APNS) that integrates easily with Django. The library uses `httpx` for HTTP/2 requests.

## Features

- Synchronous client for APNS
- JWT authentication support
- Convenient notification builder
- Built-in Django integration
- Send both single and bulk notifications
- Automatic retry attempts with delay
- Full support for all notification types (alert, background, location, voip, etc.)

## Installation

### Basic Installation

```bash
pip install simple-apns
```

### Installation with Django Support

```bash
pip install simple-apns[django]
```

## Usage

### Basic Usage

```python
from simple_apns import APNSClient, Payload

# Initialize the client
client = APNSClient(
    team_id="ABCDE12345",  # Your Apple Developer Team ID
    auth_key_id="ABC123DEFG",  # Authentication Key ID
    auth_key_path="/path/to/AuthKey_ABC123DEFG.p8",  # Path to the key file
    bundle_id="com.example.app",  # Your app's bundle ID
    use_sandbox=True,  # Use development environment
)

# Create a simple notification
payload = Payload(
    alert_title="Notification Title", 
    alert_body="Notification Text"
)

# Add custom data
payload.add_custom_data("user_id", "12345")

# Send the notification
try:
    success = client.send_notification(
        device_token="<device_token>",
        payload=payload
    )
    print(f"Notification sent: {success}")
except Exception as e:
    print(f"Error sending notification: {e}")

# Don't forget to close the connection
client.close()
```

### Creating Advanced Notifications

```python
from simple_apns import Payload

payload = Payload()

# Configure notification content
payload.set_alert(
    title="New Message",
    body="You have a new message from Anna",
    subtitle="Chat"
)

# Add sound
payload.set_sound("default")

# Set badge
payload.set_badge(5)

# Category for custom actions
payload.set_category("MESSAGE")

# Group notifications
payload.set_thread_id("chat-123")

# For background notifications
payload.set_content_available(True)

# For notification extensions
payload.set_mutable_content(True)

# Add custom data
payload.add_custom_data("message_id", "m-123")
payload.add_custom_data("sender_id", "user-456")
```

### Sending Bulk Notifications

```python
from simple_apns import APNSClient, Payload

client = APNSClient(
    team_id="ABCDE12345",
    auth_key_id="ABC123DEFG",
    auth_key_path="/path/to/AuthKey_ABC123DEFG.p8",
    bundle_id="com.example.app",
)

device_tokens = [
    "token1",
    "token2",
    "token3",
]

payload = Payload(
    alert_title="Bulk Notification", 
    alert_body="Sent to all users"
)

results = client.send_bulk_notifications(
    device_tokens=device_tokens,
    payload=payload
)

for token, success in results.items():
    print(f"Token {token}: {'success' if success else 'failed'}")

client.close()
```

## Django Integration

### Configuration

1. Add `simple_apns.django` to `INSTALLED_APPS` in your `settings.py` file:

```python
INSTALLED_APPS = [
    # ...
    'simple_apns.django',
    # ...
]
```

2. Add APNS configuration to your `settings.py` file:

```python
SIMPLE_APNS = {
    'TEAM_ID': 'ABCDE12345',
    'AUTH_KEY_ID': 'ABC123DEFG',
    'AUTH_KEY_PATH': '/path/to/AuthKey_ABC123DEFG.p8',
    'BUNDLE_ID': 'com.example.app',
    'USE_SANDBOX': True,  # Optional, default is False
    'APNS_TOPIC': None,  # Optional, default is BUNDLE_ID
    'TIMEOUT': 10,  # Optional, default is 10
    'MAX_RETRIES': 3,  # Optional, default is 3
}
```

### Using in Django

```python
from simple_apns.django import send_notification, send_bulk_notifications

# Send a single notification
try:
    success = send_notification(
        device_token="<device_token>",
        title="Title",
        body="Notification text",
        badge=1,
        sound="default",
        extra_data={"key": "value"}
    )
    print(f"Notification sent: {success}")
except Exception as e:
    print(f"Error sending notification: {e}")

# Send bulk notifications
tokens = ["token1", "token2", "token3"]
results = send_bulk_notifications(
    device_tokens=tokens,
    title="Bulk Notification",
    body="Sent to all users",
    extra_data={"campaign_id": "123"}
)
```

### Accessing the Client Directly

```python
from simple_apns.django import get_apns_client
from simple_apns import Payload

# Get the configured client
client = get_apns_client()

# Create a custom notification
payload = Payload()
payload.set_alert(title="Custom Notification", body="Text")
payload.set_content_available(True)

# Send
client.send_notification(
    device_token="<device_token>",
    payload=payload,
    push_type="background",
    priority=5
)
```

## Push Notification Types

Apple supports several types of push notifications, specified in the `push_type` parameter:

- `alert` (default): Standard notification with visual display
- `background`: Background notification for data updates without visual display
- `voip`: Notification for VoIP calls (requires special permissions)
- `complication`: Notification for watchOS complications updates
- `fileprovider`: Notification for File Provider Extension
- `mdm`: Notification for Mobile Device Management
- `location`: Notification for LocationPush

## Notification Priority

For the `priority` parameter, you can specify:

- `10` (default): Immediate notification delivery
- `5`: Delivery with power consumption optimization (for background notifications)

## Security

To ensure security, make sure that:

1. The authentication key file (.p8) is stored in a secure location
2. APNS credentials are not included in version control
3. Environment variables or secret management systems are used to store sensitive data

## Requirements

- Python 3.10+
- httpx[http2] 0.20.0+
- PyJWT 2.0.0+
- cryptography 3.4.0+
- Django 2.2+ (for Django integration)

## License

MIT