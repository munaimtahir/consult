from django.apps import AppConfig


class PatientsConfig(AppConfig):
    """Configuration for the `patients` Django app.

    This class sets the default auto field and the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.patients'
