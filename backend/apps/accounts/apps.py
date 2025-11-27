from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the `accounts` Django app.

    This class sets the default auto field and the name of the app. It also
    imports the app's signals to ensure they are connected when the app is
    ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    
    def ready(self):
        """Imports the signals for the app when it's ready."""
        import apps.accounts.signals  # noqa
