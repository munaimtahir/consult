"""
Core models for Hospital Consult System.
Includes audit trail, access logs, and filter presets.
"""

from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Tracks all significant actions in the system for audit purposes.

    This model provides a complete audit trail of all actions performed
    on consults and other important entities in the system.

    Attributes:
        action: The type of action performed.
        actor: The user who performed the action.
        consult: Optional reference to a related consult.
        target_user: Optional reference to a user affected by the action.
        department: Optional reference to a related department.
        details: JSON field for additional action details.
        ip_address: IP address from which the action was performed.
        user_agent: Browser/client user agent string.
        timestamp: When the action occurred.
    """

    ACTION_CHOICES = [
        # Consult actions
        ('CONSULT_CREATED', 'Consult Created'),
        ('CONSULT_VIEWED', 'Consult Viewed'),
        ('CONSULT_ACKNOWLEDGED', 'Consult Acknowledged'),
        ('CONSULT_ASSIGNED', 'Consult Assigned'),
        ('CONSULT_REASSIGNED', 'Consult Reassigned'),
        ('CONSULT_STATUS_CHANGED', 'Consult Status Changed'),
        ('CONSULT_COMPLETED', 'Consult Completed'),
        ('CONSULT_CANCELLED', 'Consult Cancelled'),
        ('CONSULT_ESCALATED', 'Consult Escalated'),
        
        # Note actions
        ('NOTE_ADDED', 'Note Added'),
        ('NOTE_UPDATED', 'Note Updated'),
        
        # Assignment actions
        ('AUTO_ASSIGNED', 'Auto-Assigned'),
        ('LOAD_BALANCE_ASSIGNED', 'Load Balance Assigned'),
        ('ON_CALL_ASSIGNED', 'On-Call Assigned'),
        ('HOD_OVERRIDE', 'HOD Override'),
        
        # Access actions
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        
        # Admin actions
        ('USER_CREATED', 'User Created'),
        ('USER_UPDATED', 'User Updated'),
        ('USER_DEACTIVATED', 'User Deactivated'),
        ('DEPARTMENT_CREATED', 'Department Created'),
        ('DEPARTMENT_UPDATED', 'Department Updated'),
        ('PERMISSION_CHANGED', 'Permission Changed'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
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
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs_as_target'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['actor', '-timestamp']),
            models.Index(fields=['consult', '-timestamp']),
        ]

    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else 'System'
        return f"{actor_name} - {self.get_action_display()} at {self.timestamp}"


class UnauthorizedAccessLog(models.Model):
    """Logs unauthorized access attempts for security monitoring.

    This model tracks attempts by users to access resources they
    don't have permission to view or modify.

    Attributes:
        user: The user who attempted the unauthorized access.
        resource_type: Type of resource accessed (consult, user, etc.).
        resource_id: ID of the specific resource.
        action_attempted: What action was attempted.
        ip_address: IP address from which the attempt was made.
        user_agent: Browser/client user agent string.
        timestamp: When the attempt occurred.
    """

    RESOURCE_TYPES = [
        ('CONSULT', 'Consult'),
        ('USER', 'User'),
        ('DEPARTMENT', 'Department'),
        ('DASHBOARD', 'Dashboard'),
        ('ADMIN', 'Admin Panel'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unauthorized_access_logs'
    )
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_id = models.PositiveIntegerField(null=True, blank=True)
    action_attempted = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'unauthorized_access_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['resource_type', '-timestamp']),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Unknown'
        return f"Unauthorized: {user_name} -> {self.resource_type} #{self.resource_id}"


class FilterPreset(models.Model):
    """Stores user-saved filter presets for consult lists.

    This model allows users to save their frequently used filter
    combinations for quick access.

    Attributes:
        user: The user who owns this preset.
        name: Display name for the preset.
        filters: JSON object containing the filter parameters.
        is_default: Whether this is the user's default preset.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='filter_presets'
    )
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'filter_presets'
        ordering = ['-is_default', 'name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.name}"

    def save(self, *args, **kwargs):
        """Ensures only one default preset per user."""
        if self.is_default:
            # Remove default flag from other presets
            FilterPreset.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class OnCallSchedule(models.Model):
    """Manages on-call schedules for departments.

    This model tracks which doctors are on-call for each department
    and can be used for automatic assignment routing.

    Attributes:
        department: The department this schedule applies to.
        user: The doctor on-call.
        start_time: When the on-call period begins.
        end_time: When the on-call period ends.
        is_active: Whether this schedule is currently active.
    """

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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'on_call_schedules'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['department', 'is_active', 'start_time']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} on-call for {self.department.name}"


class AssignmentPolicy(models.Model):
    """Defines auto-assignment policies for departments.

    This model allows departments to configure how consults
    are automatically assigned based on urgency levels.

    Attributes:
        department: The department this policy applies to.
        urgency: The urgency level this policy applies to.
        assignment_mode: How to assign consults.
        min_seniority: Minimum seniority level for assignment.
        escalation_minutes: Minutes before escalation.
        notify_hod: Whether to notify HOD on assignment.
    """

    ASSIGNMENT_MODES = [
        ('ROUND_ROBIN', 'Round Robin'),
        ('LOAD_BALANCE', 'Load Balance'),
        ('SENIORITY', 'By Seniority'),
        ('ON_CALL', 'On-Call Only'),
        ('MANUAL', 'Manual Assignment'),
    ]

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='assignment_policies'
    )
    urgency = models.CharField(
        max_length=20,
        choices=[
            ('EMERGENCY', 'Emergency'),
            ('URGENT', 'Urgent'),
            ('ROUTINE', 'Routine'),
        ]
    )
    assignment_mode = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_MODES,
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

    class Meta:
        db_table = 'assignment_policies'
        unique_together = ['department', 'urgency']
        ordering = ['department', 'urgency']

    def __str__(self):
        return f"{self.department.name} - {self.urgency}: {self.get_assignment_mode_display()}"


class DelayedConsultPolicy(models.Model):
    """Defines policies for delayed/pending consults.

    This model configures escalation rules and notifications
    for consults that are approaching or past their SLA.

    Attributes:
        department: The department this policy applies to.
        warning_threshold_percent: Percentage of SLA at which to warn.
        escalation_levels: JSON list of escalation levels.
        auto_escalate: Whether to automatically escalate.
    """

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='delayed_policies'
    )
    warning_threshold_percent = models.IntegerField(
        default=75,
        help_text='Percentage of SLA time at which to show warning'
    )
    escalation_levels = models.JSONField(
        default=list,
        help_text='List of escalation levels with time thresholds'
    )
    auto_escalate = models.BooleanField(
        default=True,
        help_text='Automatically escalate when threshold is reached'
    )
    notify_requester = models.BooleanField(
        default=True,
        help_text='Notify requester when consult is delayed'
    )
    notify_hod = models.BooleanField(
        default=True,
        help_text='Notify HOD when consult is delayed'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delayed_consult_policies'
        ordering = ['department']

    def __str__(self):
        return f"Delay Policy for {self.department.name}"
