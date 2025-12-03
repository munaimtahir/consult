from django.db import models
from django.conf import settings
import uuid


class EmailNotification(models.Model):
    """
    Tracks email notifications sent to users for various consult events.
    This model enables email reply handling by storing unique tokens.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('CONSULT_GENERATED', 'Consult Generated'),
        ('CONSULT_ACKNOWLEDGED', 'Consult Acknowledged'),
        ('NOTE_ADDED', 'Note Added'),
        ('CONSULT_CLOSED', 'Consult Closed'),
        ('SLA_BREACH', 'SLA Time Breach'),
        ('REASSIGNMENT', 'Reassignment'),
        ('ANALYTICS', 'Analytics Report'),
    ]
    
    # Unique token for email reply handling
    reply_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique token for email reply handling'
    )
    
    # Notification details
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    consult = models.ForeignKey(
        'consults.ConsultRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='email_notifications',
        help_text='The consult this notification is about'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_notifications_received',
        help_text='User who received this email'
    )
    
    # Email details
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_successfully = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Reply handling
    reply_received = models.BooleanField(default=False)
    reply_received_at = models.DateTimeField(null=True, blank=True)
    reply_action_taken = models.CharField(
        max_length=50,
        blank=True,
        help_text='Action taken based on email reply (e.g., ACKNOWLEDGED)'
    )
    
    class Meta:
        db_table = 'email_notifications'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['recipient', '-sent_at']),
            models.Index(fields=['consult', '-sent_at']),
            models.Index(fields=['reply_token']),
            models.Index(fields=['notification_type', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient.email} - {self.sent_at}"


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
