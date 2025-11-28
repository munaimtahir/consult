"""
Analytics models for Hospital Consult System.
Includes doctor performance metrics and department analytics.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class DoctorPerformanceMetric(models.Model):
    """Stores daily performance metrics for doctors.

    This model aggregates daily statistics for each doctor,
    enabling trend analysis and performance tracking.

    Attributes:
        doctor: The doctor this metric belongs to.
        date: The date for this metric.
        consults_assigned: Number of consults assigned.
        consults_completed: Number of consults completed.
        avg_response_time_minutes: Average response time in minutes.
        sla_compliance_rate: Percentage of consults meeting SLA.
        notes_added: Number of notes added.
        escalations_received: Consults escalated to this doctor.
    """

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    date = models.DateField()
    consults_assigned = models.IntegerField(default=0)
    consults_completed = models.IntegerField(default=0)
    avg_response_time_minutes = models.FloatField(default=0.0)
    sla_compliance_rate = models.FloatField(default=100.0)
    notes_added = models.IntegerField(default=0)
    escalations_received = models.IntegerField(default=0)
    escalations_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_performance_metrics'
        unique_together = ['doctor', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['doctor', '-date']),
            models.Index(fields=['-date', 'sla_compliance_rate']),
        ]

    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.date}"


class DepartmentDailyStats(models.Model):
    """Stores daily aggregate statistics for departments.

    This model provides department-level analytics for
    dashboards and reports.

    Attributes:
        department: The department this stat belongs to.
        date: The date for this stat.
        consults_received: New consults received.
        consults_completed: Consults completed.
        consults_escalated: Consults that were escalated.
        avg_response_time: Average response time in minutes.
        sla_compliance_rate: Percentage meeting SLA.
    """

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='daily_stats'
    )
    date = models.DateField()
    consults_received = models.IntegerField(default=0)
    consults_completed = models.IntegerField(default=0)
    consults_escalated = models.IntegerField(default=0)
    consults_pending = models.IntegerField(default=0)
    consults_overdue = models.IntegerField(default=0)
    avg_response_time_minutes = models.FloatField(default=0.0)
    sla_compliance_rate = models.FloatField(default=100.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department_daily_stats'
        unique_together = ['department', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['department', '-date']),
        ]

    def __str__(self):
        return f"{self.department.name} - {self.date}"


class ConsultTimeline(models.Model):
    """Stores timeline events for consults.

    This model provides a detailed timeline of all events
    that occur during a consult's lifecycle.

    Attributes:
        consult: The related consult.
        event_type: Type of event.
        actor: User who triggered the event (if any).
        description: Human-readable description.
        metadata: Additional event data.
        timestamp: When the event occurred.
    """

    EVENT_TYPES = [
        ('CREATED', 'Consult Created'),
        ('ACKNOWLEDGED', 'Consult Acknowledged'),
        ('ASSIGNED', 'Consult Assigned'),
        ('REASSIGNED', 'Consult Reassigned'),
        ('NOTE_ADDED', 'Note Added'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('ESCALATED', 'Consult Escalated'),
        ('COMPLETED', 'Consult Completed'),
        ('CANCELLED', 'Consult Cancelled'),
        ('SLA_WARNING', 'SLA Warning'),
        ('SLA_BREACH', 'SLA Breach'),
    ]

    consult = models.ForeignKey(
        'consults.ConsultRequest',
        on_delete=models.CASCADE,
        related_name='timeline_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timeline_events'
    )
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'consult_timeline'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['consult', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.consult_id} - {self.get_event_type_display()}"

