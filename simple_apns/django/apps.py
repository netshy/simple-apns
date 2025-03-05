from django.apps import AppConfig


class SimpleAPNSConfig(AppConfig):
    name = "simple_apns.django"
    verbose_name = "Simple APNS"

    def ready(self):
        # Perform any initialization needed when the app is ready
        pass