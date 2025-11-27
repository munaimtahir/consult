from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core Django app.

    This class sets the default auto field and the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
