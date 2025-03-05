from typing import Any, Dict, List, Optional, Union


class Payload:
    """
    Helper class for constructing APNS notification payloads.

    The APNS payload has a specific structure that this class helps to create
    in a more intuitive way than manually constructing dictionaries.
    """

    def __init__(
            self, alert_title: Optional[str] = None, alert_body: Optional[str] = None
    ):
        """
        Initialize a new payload.

        Args:
            alert_title: Optional title for the notification
            alert_body: Optional body text for the notification
        """
        self.aps_dict = {}

        # If alert title or body was provided, initialize the alert structure
        if alert_title or alert_body:
            self.set_alert(title=alert_title, body=alert_body)

        # Custom payload data outside of the 'aps' dictionary
        self.custom_data = {}

    def set_alert(
            self,
            title: Optional[str] = None,
            body: Optional[str] = None,
            subtitle: Optional[str] = None,
            launch_image: Optional[str] = None,
            title_loc_key: Optional[str] = None,
            title_loc_args: Optional[List[str]] = None,
            action_loc_key: Optional[str] = None,
            loc_key: Optional[str] = None,
            loc_args: Optional[List[str]] = None,
            summary_arg: Optional[str] = None,
            summary_arg_count: Optional[int] = None,
    ) -> "Payload":
        """
        Set the alert properties of the notification.

        Args:
            title: The title of the notification
            body: The body text of the notification
            subtitle: A subtitle for the notification
            launch_image: The name of the launch image file
            title_loc_key: The key for a localized title string
            title_loc_args: Arguments for the localized title string
            action_loc_key: The key for a localized action button string
            loc_key: The key for a localized body string
            loc_args: Arguments for the localized body string
            summary_arg: The string the notification adds to the category summary
            summary_arg_count: The number of items the notification adds to the category summary

        Returns:
            Self for method chaining
        """
        alert = {}

        if title:
            alert["title"] = title

        if body:
            alert["body"] = body

        if subtitle:
            alert["subtitle"] = subtitle

        if launch_image:
            alert["launch-image"] = launch_image

        if title_loc_key:
            alert["title-loc-key"] = title_loc_key
            if title_loc_args:
                alert["title-loc-args"] = title_loc_args

        if action_loc_key:
            alert["action-loc-key"] = action_loc_key

        if loc_key:
            alert["loc-key"] = loc_key
            if loc_args:
                alert["loc-args"] = loc_args

        if summary_arg:
            alert["summary-arg"] = summary_arg
            if summary_arg_count is not None:
                alert["summary-arg-count"] = summary_arg_count

        # Only add the alert if there are properties to set
        if alert:
            self.aps_dict["alert"] = alert

        return self

    def set_badge(self, badge: int) -> "Payload":
        """
        Set the badge count to be displayed on the app icon.

        Args:
            badge: Number to display as the badge

        Returns:
            Self for method chaining
        """
        self.aps_dict["badge"] = badge
        return self

    def set_sound(self, sound: Union[str, Dict[str, Any]]) -> "Payload":
        """
        Set the sound to play for the notification.

        Args:
            sound: Either a string with the sound name or a dictionary for critical alerts
                  Format for critical alerts: {"critical": 1, "name": "sound_name", "volume": 0.5}

        Returns:
            Self for method chaining
        """
        self.aps_dict["sound"] = sound
        return self

    def set_content_available(self, content_available: bool = True) -> "Payload":
        """
        Set the content-available flag for background notifications.

        Args:
            content_available: Whether content is available in the background

        Returns:
            Self for method chaining
        """
        if content_available:
            self.aps_dict["content-available"] = 1
        elif "content-available" in self.aps_dict:
            del self.aps_dict["content-available"]

        return self

    def set_mutable_content(self, mutable_content: bool = True) -> "Payload":
        """
        Set the mutable-content flag for notification service extensions.

        Args:
            mutable_content: Whether the content can be modified by extensions

        Returns:
            Self for method chaining
        """
        if mutable_content:
            self.aps_dict["mutable-content"] = 1
        elif "mutable-content" in self.aps_dict:
            del self.aps_dict["mutable-content"]

        return self

    def set_category(self, category: str) -> "Payload":
        """
        Set the category for custom actions.

        Args:
            category: The notification category identifier

        Returns:
            Self for method chaining
        """
        self.aps_dict["category"] = category
        return self

    def set_thread_id(self, thread_id: str) -> "Payload":
        """
        Set the thread identifier for grouping notifications.

        Args:
            thread_id: The thread identifier for grouping related notifications

        Returns:
            Self for method chaining
        """
        self.aps_dict["thread-id"] = thread_id
        return self

    def set_target_content_id(self, target_content_id: str) -> "Payload":
        """
        Set the target content identifier.

        Args:
            target_content_id: The identifier for the target content

        Returns:
            Self for method chaining
        """
        self.aps_dict["target-content-id"] = target_content_id
        return self

    def set_interruption_level(self, level: str) -> "Payload":
        """
        Set the interruption level.

        Args:
            level: One of "passive", "active", "time-sensitive", or "critical"

        Returns:
            Self for method chaining
        """
        valid_levels = ("passive", "active", "time-sensitive", "critical")
        if level not in valid_levels:
            raise ValueError(
                f"Invalid interruption level. Must be one of: {', '.join(valid_levels)}"
            )

        self.aps_dict["interruption-level"] = level
        return self

    def set_relevance_score(self, score: float) -> "Payload":
        """
        Set the relevance score (0.0 to 1.0).

        Args:
            score: A value between 0.0 and 1.0 indicating the notification's relevance

        Returns:
            Self for method chaining
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")

        self.aps_dict["relevance-score"] = score
        return self

    def add_custom_data(self, key: str, value: Any) -> "Payload":
        """
        Add custom data to the payload (outside the 'aps' dictionary).

        Args:
            key: The key for the custom data
            value: The value for the custom data

        Returns:
            Self for method chaining
        """
        self.custom_data[key] = value
        return self

    def to_dict(self) -> Dict:
        """
        Convert the payload to a dictionary.

        Returns:
            The complete payload as a dictionary
        """
        payload = {"aps": self.aps_dict.copy()}

        # Add custom data
        for key, value in self.custom_data.items():
            payload[key] = value

        return payload
