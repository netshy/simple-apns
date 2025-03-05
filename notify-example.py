from simple_apns import APNSClient, Payload

# Your Apple Developer credentials
# You can find your Team ID in the Apple Developer portal: https://developer.apple.com/account/#/membership
team_id = "ABCDE12345"

# Get your Auth Key ID from: https://developer.apple.com/account/resources/authkeys/list
auth_key_id = "ABC123DEFG"

# Download your .p8 key file from the Apple Developer portal and provide the path
# https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/establishing_a_token-based_connection_to_apns
auth_key_path = "/path/to/AuthKey_ABC123DEFG.p8"

# Your app's Bundle ID from App Store Connect: https://appstoreconnect.apple.com
bundle_id = "com.example.app"

# Device token obtained from your app using:
# https://developer.apple.com/documentation/usernotifications/registering_your_app_with_apns
device_token = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

# Create APNS client
client = APNSClient(
    team_id=team_id,
    auth_key_id=auth_key_id,
    auth_key_path=auth_key_path,
    bundle_id=bundle_id,
    use_sandbox=True  # Use False for production environment
)

# Create notification payload
payload = Payload(
    alert_title="Hello from Simple APNS",
    alert_body="This is a test notification from Simple APNS library"
)

# Add sound, badge and custom data
payload.set_sound("default")
payload.set_badge(1)
payload.add_custom_data("link", "app://open/profile/123")

try:
    # Send notification
    # For more info on push types: https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/sending_notification_requests_to_apns
    success = client.send_notification(
        device_token=device_token,
        payload=payload,
        push_type="alert",  # Options: alert, background, voip, complication, fileprovider, mdm, location
        priority=10  # 10: immediate delivery, 5: power-optimized delivery
    )
    print(f"Notification status: {'success' if success else 'failed'}")
except Exception as e:
    print(f"Error sending notification: {e}")
finally:
    # Close the connection
    client.close()
