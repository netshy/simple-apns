"""
Test script to verify timeout fixes work correctly
"""
import time
from simple_apns.client import APNSClient
from simple_apns.payload import Payload
from simple_apns.exceptions import APNSTimeoutError, APNSTokenError

# Replace with actual credentials
TEAM_ID = "49Q5YGDRRW"
AUTH_KEY_ID = "L3DGRQY2RT"
AUTH_KEY_PATH = r"c:\dev\padel77\padel_web\config\settings\AuthKey_L3DGRQY2RT.p8"
BUNDLE_ID = "io.ballball.Ballball"

def test_timeout_behavior():
    """Test that timeout works correctly for invalid tokens"""

    client = APNSClient(
        team_id=TEAM_ID,
        auth_key_id=AUTH_KEY_ID,
        auth_key_path=AUTH_KEY_PATH,
        bundle_id=BUNDLE_ID,
        timeout=5,
    )

    # Problematic tokens from user 29
    problematic_tokens = [
        'fbcff59c00ec71bd28bb624aa1f467a867a4bae076d5b3c56bdf407f35fe2d8b',
        '0da269a9ceab1f1387ec72456b1ddd1b48b180a496e47c73ba842ebadf5c331d',
    ]

    payload = Payload(alert_title="Test", alert_body="Timeout test")

    for token in problematic_tokens:
        print(f"\nTesting token: {token[:8]}...")

        start = time.time()
        try:
            result = client.send_notification(token, payload)
            elapsed = time.time() - start
            print(f"  ✅ Success in {elapsed:.2f}s")
        except APNSTimeoutError as e:
            elapsed = time.time() - start
            print(f"  ⏱️  Timeout in {elapsed:.2f}s (expected ~5s)")
            assert 4 < elapsed < 8, f"Expected ~5s timeout, got {elapsed:.2f}s"
        except APNSTokenError as e:
            elapsed = time.time() - start
            print(f"  ❌ Invalid token in {elapsed:.2f}s: {e}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ❌ Error in {elapsed:.2f}s: {e}")

    client.close()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_timeout_behavior()
