"""
App configuration for intake app.
"""

from django.apps import AppConfig


class IntakeConfig(AppConfig):
    """Configuration for the intake app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.intake'
    verbose_name = 'Student Intake'
