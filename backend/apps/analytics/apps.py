from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Configuration for the `analytics` Django app.

    This class sets the default auto field and the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
