from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'
    
    def ready(self):
        # Import tasks indirectly to avoid circular imports
        import library.signals  # Make sure the signals are initialized
