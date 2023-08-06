from django.apps import AppConfig


class ExpiryAddonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "expiry_addon"

    def ready(self):
        """
        We override the ready method of AppConfig, so the application
            could start listening to the signal we create in signals.py
        :return: None
        """

        import expiry_addon.signals
