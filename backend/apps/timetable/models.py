"""
Timetable models for weekly schedule management.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import json


class WeekPlan(models.Model):
    """Represents a weekly timetable plan.
    
    Each week has its own slot timings and department allocation per day/slot.
    Status machine: draft → verified → published
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('VERIFIED', 'Verified'),
        ('PUBLISHED', 'Published'),
    ]
    
    week_start_date = models.DateField(
        unique=True,
        db_index=True,
        help_text='Monday date of the week'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )
    
    # Tracking fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_week_plans',
        help_text='User who created this week plan'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_week_plans',
        help_text='User who verified this week plan'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_week_plans',
        help_text='User who published this week plan'
    )
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'week_plans'
        ordering = ['-week_start_date']
        indexes = [
            models.Index(fields=['status', '-week_start_date']),
            models.Index(fields=['week_start_date']),
        ]
    
    def __str__(self):
        return f"Week starting {self.week_start_date} ({self.get_status_display()})"
    
    @property
    def week_end_date(self):
        """Returns the Sunday date of the week."""
        from datetime import timedelta
        return self.week_start_date + timedelta(days=6)
    
    def can_edit(self, user):
        """Checks if the user can edit this week plan."""
        if self.status == 'DRAFT':
            return True
        if self.status == 'VERIFIED':
            # Admin/HOD can revert to draft
            return user.is_admin_user or user.is_hod
        if self.status == 'PUBLISHED':
            # Only HOD/Admin can edit published weeks with reason
            return user.is_admin_user or user.is_hod
        return False


class WeekSlotRow(models.Model):
    """Defines the rows (Slot 1..N) for a specific week.
    
    Each row represents a time slot with start/end times.
    """
    
    week_plan = models.ForeignKey(
        WeekPlan,
        on_delete=models.CASCADE,
        related_name='slot_rows'
    )
    row_index = models.IntegerField(
        help_text='Slot number (1-based index)'
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Start time for this slot'
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='End time for this slot'
    )
    
    class Meta:
        db_table = 'week_slot_rows'
        unique_together = ('week_plan', 'row_index')
        ordering = ['week_plan', 'row_index']
    
    def __str__(self):
        if self.start_time and self.end_time:
            return f"Slot {self.row_index}: {self.start_time} - {self.end_time}"
        return f"Slot {self.row_index}"
    
    def clean(self):
        """Validates that end_time > start_time if both are set."""
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError('End time must be after start time')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WeekCell(models.Model):
    """Represents a grid cell: (WeekPlan × DayOfWeek × SlotRow).
    
    Each cell holds department, topic, and faculty information.
    """
    
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    week_plan = models.ForeignKey(
        WeekPlan,
        on_delete=models.CASCADE,
        related_name='cells'
    )
    slot_row = models.ForeignKey(
        WeekSlotRow,
        on_delete=models.CASCADE,
        related_name='cells'
    )
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        help_text='0=Monday, 1=Tuesday, ..., 6=Sunday'
    )
    
    # Cell content
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_cells',
        help_text='Department allocated to this cell'
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        help_text='Topic text for this session'
    )
    faculty_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Faculty name for this session'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    
    class Meta:
        db_table = 'week_cells'
        unique_together = ('week_plan', 'slot_row', 'day_of_week')
        indexes = [
            models.Index(fields=['week_plan', 'day_of_week']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES).get(self.day_of_week, 'Unknown')
        return f"{self.week_plan.week_start_date} - {day_name} Slot {self.slot_row.row_index}"


class WeekChangeLog(models.Model):
    """Captures changes to published weeks (especially after publish).
    
    Stores before/after snapshot JSON + actor + reason.
    """
    
    week_plan = models.ForeignKey(
        WeekPlan,
        on_delete=models.CASCADE,
        related_name='change_logs'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='timetable_changes'
    )
    change_reason = models.TextField(
        help_text='Reason for making this change to a published week'
    )
    
    # Snapshots as JSON
    before_snapshot = models.JSONField(
        help_text='State before the change (rows + cells)'
    )
    after_snapshot = models.JSONField(
        help_text='State after the change (rows + cells)'
    )
    
    # What changed
    changed_rows = models.JSONField(
        default=list,
        help_text='List of row IDs that were changed'
    )
    changed_cells = models.JSONField(
        default=list,
        help_text='List of cell IDs that were changed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'week_change_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['week_plan', '-created_at']),
        ]
    
    def __str__(self):
        return f"Change log for {self.week_plan} by {self.changed_by} at {self.created_at}"


class SessionOccurrence(models.Model):
    """Represents a real dated session created when a week is published.
    
    This becomes the base for attendance and monthly reporting.
    Generated from WeekCells when a week is published.
    """
    
    week_plan = models.ForeignKey(
        WeekPlan,
        on_delete=models.CASCADE,
        related_name='session_occurrences'
    )
    week_cell = models.ForeignKey(
        WeekCell,
        on_delete=models.CASCADE,
        related_name='session_occurrences',
        null=True,
        blank=True,
        help_text='Original cell that generated this session'
    )
    
    # Session details
    date = models.DateField(
        db_index=True,
        help_text='Actual date of the session'
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session_occurrences'
    )
    topic = models.CharField(max_length=200, blank=True)
    faculty_name = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='SCHEDULED'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'session_occurrences'
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'department']),
            models.Index(fields=['week_plan', 'date']),
            models.Index(fields=['status', 'date']),
        ]
    
    def __str__(self):
        return f"Session on {self.date} at {self.start_time} - {self.department or 'No Department'}"
