import pytest

from simple_apns.payload import Payload


def test_payload_init_empty():
    """Test creating an empty payload."""
    payload = Payload()
    assert payload.aps_dict == {}
    assert payload.custom_data == {}

    result = payload.to_dict()
    assert result == {"aps": {}}


def test_payload_init_with_alert():
    """Test creating a payload with alert title and body."""
    payload = Payload(alert_title="Test Title", alert_body="Test Body")

    assert "alert" in payload.aps_dict
    assert payload.aps_dict["alert"]["title"] == "Test Title"
    assert payload.aps_dict["alert"]["body"] == "Test Body"

    result = payload.to_dict()
    assert result == {"aps": {"alert": {"title": "Test Title", "body": "Test Body"}}}


def test_set_alert():
    """Test setting alert properties."""
    payload = Payload()

    # Test setting basic alert properties
    payload.set_alert(title="Alert Title", body="Alert Body", subtitle="Alert Subtitle")

    assert payload.aps_dict["alert"]["title"] == "Alert Title"
    assert payload.aps_dict["alert"]["body"] == "Alert Body"
    assert payload.aps_dict["alert"]["subtitle"] == "Alert Subtitle"

    # Test method chaining
    result = payload.set_alert(
        title="New Title", loc_key="ALERT_LOC_KEY", loc_args=["arg1", "arg2"]
    )

    assert result is payload  # Method returns self
    assert payload.aps_dict["alert"]["title"] == "New Title"
    assert payload.aps_dict["alert"]["loc-key"] == "ALERT_LOC_KEY"
    assert payload.aps_dict["alert"]["loc-args"] == ["arg1", "arg2"]


def test_set_badge():
    """Test setting badge count."""
    payload = Payload()

    payload.set_badge(5)
    assert payload.aps_dict["badge"] == 5

    # Test method chaining
    result = payload.set_badge(10)
    assert result is payload  # Method returns self
    assert payload.aps_dict["badge"] == 10


def test_set_sound():
    """Test setting sound."""
    payload = Payload()

    # Test with string
    payload.set_sound("default")
    assert payload.aps_dict["sound"] == "default"

    # Test with dictionary for critical alerts
    critical_sound = {"critical": 1, "name": "critical_sound", "volume": 0.8}

    result = payload.set_sound(critical_sound)
    assert result is payload  # Method returns self
    assert payload.aps_dict["sound"] == critical_sound


def test_content_available_and_mutable():
    """Test setting content-available and mutable-content flags."""
    payload = Payload()

    # Test setting content-available
    payload.set_content_available(True)
    assert payload.aps_dict["content-available"] == 1

    # Test unsetting content-available
    payload.set_content_available(False)
    assert "content-available" not in payload.aps_dict

    # Test setting mutable-content
    payload.set_mutable_content(True)
    assert payload.aps_dict["mutable-content"] == 1

    # Test unsetting mutable-content
    payload.set_mutable_content(False)
    assert "mutable-content" not in payload.aps_dict

    # Test method chaining
    result = payload.set_content_available().set_mutable_content()
    assert result is payload  # Method returns self
    assert payload.aps_dict["content-available"] == 1
    assert payload.aps_dict["mutable-content"] == 1


def test_set_category_and_thread_id():
    """Test setting category and thread-id."""
    payload = Payload()

    payload.set_category("MESSAGE_CATEGORY")
    assert payload.aps_dict["category"] == "MESSAGE_CATEGORY"

    payload.set_thread_id("chat-thread-123")
    assert payload.aps_dict["thread-id"] == "chat-thread-123"


def test_target_content_id():
    """Test setting target-content-id."""
    payload = Payload()

    payload.set_target_content_id("target-123")
    assert payload.aps_dict["target-content-id"] == "target-123"


def test_interruption_level():
    """Test setting interruption-level."""
    payload = Payload()

    # Test valid levels
    for level in ["passive", "active", "time-sensitive", "critical"]:
        payload.set_interruption_level(level)
        assert payload.aps_dict["interruption-level"] == level

    # Test invalid level
    with pytest.raises(ValueError) as excinfo:
        payload.set_interruption_level("invalid-level")

    assert "Invalid interruption level" in str(excinfo.value)


def test_relevance_score():
    """Test setting relevance-score."""
    payload = Payload()

    # Test valid scores
    payload.set_relevance_score(0.0)
    assert payload.aps_dict["relevance-score"] == 0.0

    payload.set_relevance_score(0.5)
    assert payload.aps_dict["relevance-score"] == 0.5

    payload.set_relevance_score(1.0)
    assert payload.aps_dict["relevance-score"] == 1.0

    # Test invalid scores
    with pytest.raises(ValueError) as excinfo:
        payload.set_relevance_score(-0.1)

    assert "Relevance score must be between 0.0 and 1.0" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        payload.set_relevance_score(1.1)

    assert "Relevance score must be between 0.0 and 1.0" in str(excinfo.value)


def test_custom_data():
    """Test adding custom data."""
    payload = Payload()

    # Add various types of custom data
    payload.add_custom_data("string_key", "string_value")
    payload.add_custom_data("int_key", 123)
    payload.add_custom_data("float_key", 12.34)
    payload.add_custom_data("bool_key", True)
    payload.add_custom_data("dict_key", {"nested": "value"})
    payload.add_custom_data("list_key", [1, 2, 3])

    # Check custom data
    assert payload.custom_data["string_key"] == "string_value"
    assert payload.custom_data["int_key"] == 123
    assert payload.custom_data["float_key"] == 12.34
    assert payload.custom_data["bool_key"] is True
    assert payload.custom_data["dict_key"] == {"nested": "value"}
    assert payload.custom_data["list_key"] == [1, 2, 3]

    # Test to_dict includes all custom data
    result = payload.to_dict()
    assert result["string_key"] == "string_value"
    assert result["int_key"] == 123
    assert result["float_key"] == 12.34
    assert result["bool_key"] is True
    assert result["dict_key"] == {"nested": "value"}
    assert result["list_key"] == [1, 2, 3]


def test_complex_payload():
    """Test creating a complex payload with multiple properties."""
    payload = Payload()

    # Set various properties
    payload.set_alert(
        title="Complex Notification",
        body="This is a complex notification",
        subtitle="With a subtitle",
    )
    payload.set_badge(7)
    payload.set_sound("custom_sound")
    payload.set_category("COMPLEX_CATEGORY")
    payload.set_thread_id("complex-thread-1")
    payload.set_target_content_id("target-1")
    payload.set_content_available(True)
    payload.set_mutable_content(True)
    payload.set_interruption_level("time-sensitive")
    payload.set_relevance_score(0.8)

    # Add custom data
    payload.add_custom_data("notification_id", "notif-12345")
    payload.add_custom_data("deeplink", "app://open/section/123")

    # Verify the final structure
    result = payload.to_dict()

    assert result["aps"]["alert"]["title"] == "Complex Notification"
    assert result["aps"]["alert"]["body"] == "This is a complex notification"
    assert result["aps"]["alert"]["subtitle"] == "With a subtitle"
    assert result["aps"]["badge"] == 7
    assert result["aps"]["sound"] == "custom_sound"
    assert result["aps"]["category"] == "COMPLEX_CATEGORY"
    assert result["aps"]["thread-id"] == "complex-thread-1"
    assert result["aps"]["target-content-id"] == "target-1"
    assert result["aps"]["content-available"] == 1
    assert result["aps"]["mutable-content"] == 1
    assert result["aps"]["interruption-level"] == "time-sensitive"
    assert result["aps"]["relevance-score"] == 0.8
    assert result["notification_id"] == "notif-12345"
    assert result["deeplink"] == "app://open/section/123"
