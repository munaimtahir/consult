"""
Core models for system-wide settings.
"""

from django.db import models
from django.conf import settings


class EmailNotificationSettings(models.Model):
    """
    Email notification settings per department.
    Allows configuring which email notifications are enabled for each department.
    """
    department = models.OneToOneField(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='email_notification_settings',
        help_text='Department these settings apply to'
    )
    
    # Notification type toggles
    notify_on_consult_generated = models.BooleanField(
        default=True,
        help_text='Send email when a new consult is generated for this department'
    )
    notify_on_consult_acknowledged = models.BooleanField(
        default=True,
        help_text='Send email when a consult is acknowledged'
    )
    notify_on_note_added = models.BooleanField(
        default=True,
        help_text='Send email when a note is added to a consult'
    )
    notify_on_consult_closed = models.BooleanField(
        default=True,
        help_text='Send email when a consult is closed'
    )
    notify_on_sla_breach = models.BooleanField(
        default=True,
        help_text='Send email when SLA time is breached'
    )
    notify_on_reassignment = models.BooleanField(
        default=True,
        help_text='Send email when a consult is reassigned'
    )
    
    # Recipient settings
    send_to_hod = models.BooleanField(
        default=True,
        help_text='Send notifications to Head of Department'
    )
    send_to_assigned_doctor = models.BooleanField(
        default=True,
        help_text='Send notifications to assigned doctor'
    )
    send_to_requester = models.BooleanField(
        default=True,
        help_text='Send notifications to the requester'
    )
    
    # Additional recipients (comma-separated emails)
    additional_recipients = models.TextField(
        blank=True,
        help_text='Additional email recipients (one per line)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_notification_settings'
        verbose_name = 'Email Notification Settings'
        verbose_name_plural = 'Email Notification Settings'
    
    def __str__(self):
        return f"Email Settings for {self.department.name}"


class SMTPConfiguration(models.Model):
    """
    SMTP server configuration.
    Only one active configuration should exist at a time.
    """
    name = models.CharField(
        max_length=100,
        help_text='Configuration name (e.g., "Google Workspace Production")'
    )
    
    # SMTP Settings
    host = models.CharField(
        max_length=255,
        default='smtp.gmail.com',
        help_text='SMTP server hostname'
    )
    port = models.IntegerField(
        default=587,
        help_text='SMTP server port'
    )
    use_tls = models.BooleanField(
        default=True,
        help_text='Use TLS encryption'
    )
    username = models.CharField(
        max_length=255,
        help_text='SMTP username (email address)'
    )
    password = models.CharField(
        max_length=255,
        help_text='SMTP password (app password for Google)'
    )
    
    # Email settings
    from_email = models.EmailField(
        help_text='Default "from" email address'
    )
    from_name = models.CharField(
        max_length=255,
        default='PMC Consult System',
        help_text='Default "from" name'
    )
    reply_to_email = models.EmailField(
        blank=True,
        help_text='Reply-to email address (for email replies)'
    )
    
    # Status
    is_active = models.BooleanField(
        default=False,
        help_text='Is this configuration currently active?'
    )
    is_test_mode = models.BooleanField(
        default=False,
        help_text='Test mode - emails will be logged but not sent'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_smtp_configurations'
    )
    
    class Meta:
        db_table = 'smtp_configurations'
        verbose_name = 'SMTP Configuration'
        verbose_name_plural = 'SMTP Configurations'
        ordering = ['-is_active', '-created_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({status})"
    
    def save(self, *args, **kwargs):
        # Ensure only one active configuration
        if self.is_active:
            SMTPConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
