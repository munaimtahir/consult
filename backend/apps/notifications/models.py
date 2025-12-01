from django.db import models
from django.conf import settings


class Device(models.Model):
    """
    Stores device registration information for push notifications.
    Each device can be associated with a user and has an FCM token.
    """
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices',
        help_text='The user this device belongs to'
    )
    device_id = models.CharField(
        max_length=255,
        help_text='Unique identifier for the device'
    )
    fcm_token = models.TextField(
        help_text='Firebase Cloud Messaging token'
    )
    platform = models.CharField(
        max_length=10,
        choices=PLATFORM_CHOICES,
        default='android',
        help_text='Device platform (android or ios)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the device should receive notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'device_id']
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - {self.device_id[:20]}..."
