from django.apps import AppConfig

class VendorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendorapp'

    def ready(self):
        import vendorapp.signals  # Ensure signals are imported correctly
