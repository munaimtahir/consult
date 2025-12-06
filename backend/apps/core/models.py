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


class AuditLog(models.Model):
    """
    Audit log for tracking system actions.
    """
    ACTION_CHOICES = [
        ('CONSULT_CREATED', 'Consult Created'),
        ('CONSULT_VIEWED', 'Consult Viewed'),
        ('CONSULT_ACKNOWLEDGED', 'Consult Acknowledged'),
        ('CONSULT_ASSIGNED', 'Consult Assigned'),
        ('CONSULT_REASSIGNED', 'Consult Reassigned'),
        ('CONSULT_STATUS_CHANGED', 'Consult Status Changed'),
        ('CONSULT_COMPLETED', 'Consult Completed'),
        ('CONSULT_CANCELLED', 'Consult Cancelled'),
        ('CONSULT_ESCALATED', 'Consult Escalated'),
        ('NOTE_ADDED', 'Note Added'),
        ('NOTE_UPDATED', 'Note Updated'),
        ('AUTO_ASSIGNED', 'Auto-Assigned'),
        ('LOAD_BALANCE_ASSIGNED', 'Load Balance Assigned'),
        ('ON_CALL_ASSIGNED', 'On-Call Assigned'),
        ('HOD_OVERRIDE', 'HOD Override'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('USER_CREATED', 'User Created'),
        ('USER_UPDATED', 'User Updated'),
        ('USER_DEACTIVATED', 'User Deactivated'),
        ('DEPARTMENT_CREATED', 'Department Created'),
        ('DEPARTMENT_UPDATED', 'Department Updated'),
        ('PERMISSION_CHANGED', 'Permission Changed'),
    ]
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    consult = models.ForeignKey(
        'consults.ConsultRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs_as_target'
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', '-timestamp'], name='audit_logs_action_f48619_idx'),
            models.Index(fields=['actor', '-timestamp'], name='audit_logs_actor_i_9ecce2_idx'),
            models.Index(fields=['consult', '-timestamp'], name='audit_logs_consult_e52ab0_idx'),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"


class FilterPreset(models.Model):
    """
    User filter presets for consult listings.
    """
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='filter_presets'
    )
    
    class Meta:
        db_table = 'filter_presets'
        ordering = ['-is_default', 'name']
        unique_together = [('user', 'name')]
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class OnCallSchedule(models.Model):
    """
    On-call schedules for doctors.
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='on_call_schedules'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='on_call_schedules'
    )
    
    class Meta:
        db_table = 'on_call_schedules'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['department', 'is_active', 'start_time'], name='on_call_sch_departm_3feb37_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.department.name} ({self.start_time} to {self.end_time})"


class AssignmentPolicy(models.Model):
    """
    Assignment policies for automatic consult assignment.
    """
    URGENCY_CHOICES = [
        ('EMERGENCY', 'Emergency'),
        ('URGENT', 'Urgent'),
        ('ROUTINE', 'Routine'),
    ]
    
    ASSIGNMENT_MODE_CHOICES = [
        ('ROUND_ROBIN', 'Round Robin'),
        ('LOAD_BALANCE', 'Load Balance'),
        ('SENIORITY', 'By Seniority'),
        ('ON_CALL', 'On-Call Only'),
        ('MANUAL', 'Manual Assignment'),
    ]
    
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    assignment_mode = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_MODE_CHOICES,
        default='MANUAL'
    )
    min_seniority = models.IntegerField(
        default=1,
        help_text='Minimum seniority level for auto-assignment'
    )
    escalation_minutes = models.IntegerField(
        default=60,
        help_text='Minutes before escalating to senior'
    )
    notify_hod = models.BooleanField(
        default=False,
        help_text='Notify HOD on new assignment'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='assignment_policies'
    )
    
    class Meta:
        db_table = 'assignment_policies'
        ordering = ['department', 'urgency']
        unique_together = [('department', 'urgency')]
    
    def __str__(self):
        return f"{self.department.name} - {self.urgency} ({self.assignment_mode})"
